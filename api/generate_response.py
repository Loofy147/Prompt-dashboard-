"""
api/generate_response.py
Production-grade LLM response generator with quality analysis integration.

This module provides a unified interface for generating AI responses across
multiple LLM providers (Claude, GPT-4) with built-in quality scoring, cost
tracking, caching, and robust error handling.

Quick Start:
    >>> from generate_response import generate_response
    >>> response = generate_response(
    ...     prompt="You are a Senior Engineer. Write a brief API spec.",
    ...     provider="claude"
    ... )
    >>> print(f"Q Score: {response.quality_score:.4f}")
    >>> print(f"Cost: ${response.total_cost_usd:.4f}")
    >>> print(response.text[:100])

Author: Prompt Dashboard Manager Team
Version: 1.0.0
License: MIT
"""

import os
import time
import logging
import hashlib
import json
from typing import Dict, List, Optional, Iterator, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from functools import lru_cache

# Third-party imports
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from cachetools import TTLCache
    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False
    # Fallback simple cache
    class TTLCache(dict):
        def __init__(self, maxsize, ttl):
            super().__init__()
            self.maxsize = maxsize
            self.ttl = ttl

# Local imports
try:
    from quality_calculator import compute_Q
    from feature_analyzer import estimate_features
except ImportError:
    # Fallback for standalone testing
    def compute_Q(features):
        weights = {'P': 0.18, 'T': 0.22, 'F': 0.20, 'S': 0.18, 'C': 0.12, 'R': 0.10}
        return sum(weights[k] * features[k] for k in weights), {}

    def estimate_features(text):
        return {'P': 0.5, 'T': 0.5, 'F': 0.5, 'S': 0.5, 'C': 0.5, 'R': 0.5}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# EXCEPTIONS
# ============================================================================

class ProviderConfigError(Exception):
    """Raised when provider is not properly configured."""
    pass


class APIResponseError(Exception):
    """Raised when API returns invalid or malformed response."""
    pass


class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    pass


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is in open state."""
    pass


# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

PROVIDERS = {
    'claude': {
        'models': ['claude-sonnet-4-20250514', 'claude-opus-4-20250514'],
        'default_model': 'claude-sonnet-4-20250514',
        'api_key_env': 'ANTHROPIC_API_KEY',
        'endpoint': 'https://api.anthropic.com/v1/messages',
        'max_tokens_default': 4096,
        'cost_per_1k_input': 0.003,   # $3/M tokens
        'cost_per_1k_output': 0.015,  # $15/M tokens
        'rate_limit_rpm': 60,
        'timeout_seconds': 30
    },
    'openai': {
        'models': ['gpt-4o', 'gpt-4-turbo', 'gpt-4'],
        'default_model': 'gpt-4o',
        'api_key_env': 'OPENAI_API_KEY',
        'endpoint': 'https://api.openai.com/v1/chat/completions',
        'max_tokens_default': 4096,
        'cost_per_1k_input': 0.005,   # $5/M tokens
        'cost_per_1k_output': 0.015,  # $15/M tokens
        'rate_limit_rpm': 500,
        'timeout_seconds': 30
    }
}

# Circuit breaker configuration
CIRCUIT_BREAKER_THRESHOLD = 5  # failures before opening
CIRCUIT_BREAKER_TIMEOUT = 60   # seconds before half-open
CIRCUIT_BREAKER_HALF_OPEN_REQUESTS = 1

# Cache configuration
CACHE_MAX_SIZE = 1000
CACHE_DEFAULT_TTL = 3600  # 1 hour

# Response truncation for logging
LOG_TRUNCATE_LENGTH = 100


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class LLMResponse:
    """Response object from LLM generation."""

    text: str
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_cost_usd: float
    latency_ms: float
    quality_features: Optional[Dict[str, float]] = None
    quality_score: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @property
    def total_tokens(self) -> int:
        """Total tokens used (input + output)."""
        return self.prompt_tokens + self.completion_tokens

    @property
    def quality_level(self) -> str:
        """Get quality level label."""
        if self.quality_score is None:
            return "Unknown"
        if self.quality_score >= 0.90:
            return "Excellent"
        elif self.quality_score >= 0.80:
            return "Good"
        elif self.quality_score >= 0.70:
            return "Fair"
        else:
            return "Poor"


@dataclass
class ProviderConfig:
    """Configuration for a specific LLM provider."""

    name: str
    models: List[str]
    default_model: str
    api_key: str
    endpoint: str
    max_tokens_default: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    rate_limit_rpm: int
    timeout_seconds: int


@dataclass
class CircuitBreakerState:
    """State tracking for circuit breaker pattern."""

    failures: int = 0
    state: str = "closed"  # closed, open, half_open
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def count_tokens_approximate(text: str) -> int:
    """
    Approximate token count (4 chars ≈ 1 token for English).

    For production, use tiktoken for OpenAI or Anthropic's token counter.

    Args:
        text: Input text

    Returns:
        Estimated token count

    Example:
        >>> count_tokens_approximate("Hello, world!")
        3
    """
    return max(1, len(text) // 4)


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    provider_config: ProviderConfig
) -> float:
    """
    Calculate total cost in USD for API request.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        provider_config: Provider configuration

    Returns:
        Total cost in USD

    Example:
        >>> config = ProviderConfig(...)
        >>> calculate_cost(1000, 500, config)
        0.0105
    """
    input_cost = (input_tokens / 1000) * provider_config.cost_per_1k_input
    output_cost = (output_tokens / 1000) * provider_config.cost_per_1k_output
    return input_cost + output_cost


def generate_cache_key(
    prompt: str,
    provider: str,
    model: str,
    temperature: float,
    max_tokens: int,
    system_message: Optional[str]
) -> str:
    """
    Generate cache key for request deduplication.

    Args:
        prompt: User prompt
        provider: LLM provider name
        model: Model name
        temperature: Temperature parameter
        max_tokens: Max tokens to generate
        system_message: Optional system message

    Returns:
        MD5 hash of request parameters

    Example:
        >>> key = generate_cache_key("Hello", "claude", "sonnet", 0.7, 100, None)
        >>> len(key)
        32
    """
    key_data = f"{prompt}|{provider}|{model}|{temperature}|{max_tokens}|{system_message}"
    return hashlib.md5(key_data.encode()).hexdigest()


def truncate_for_logging(text: str, max_length: int = LOG_TRUNCATE_LENGTH) -> str:
    """Truncate text for safe logging without exposing full content."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


# ============================================================================
# RESPONSE GENERATOR CLASS
# ============================================================================

class ResponseGenerator:
    """
    Unified interface for generating LLM responses with quality analysis.

    Supports multiple providers (Claude, GPT-4) with automatic quality scoring,
    cost tracking, caching, rate limiting, and robust error handling.

    Example:
        >>> generator = ResponseGenerator(provider="claude")
        >>> response = generator.generate(
        ...     prompt="Explain quantum computing in 2 sentences.",
        ...     temperature=0.7
        ... )
        >>> print(f"Response: {response.text}")
        >>> print(f"Quality: {response.quality_score:.2f}")
        >>> print(f"Cost: ${response.total_cost_usd:.4f}")
    """

    def __init__(
        self,
        provider: str = "claude",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        enable_cache: bool = True,
        enable_circuit_breaker: bool = True
    ):
        """
        Initialize response generator.

        Args:
            provider: LLM provider ("claude" or "openai")
            model: Specific model (defaults to provider's default)
            api_key: API key (defaults to environment variable)
            enable_cache: Enable response caching
            enable_circuit_breaker: Enable circuit breaker pattern

        Raises:
            ProviderConfigError: If provider not configured properly
        """
        if provider not in PROVIDERS:
            raise ProviderConfigError(
                f"Unknown provider: {provider}. Available: {list(PROVIDERS.keys())}"
            )

        provider_info = PROVIDERS[provider]

        # Get API key
        if api_key is None:
            api_key = os.getenv(provider_info['api_key_env'])

        if not api_key:
            raise ProviderConfigError(
                f"API key not found. Set {provider_info['api_key_env']} "
                f"environment variable or pass api_key parameter."
            )

        # Set model
        if model is None:
            model = provider_info['default_model']
        elif model not in provider_info['models']:
            logger.warning(
                f"Model {model} not in known models for {provider}. "
                f"Using anyway (might fail)."
            )

        self.config = ProviderConfig(
            name=provider,
            models=provider_info['models'],
            default_model=provider_info['default_model'],
            api_key=api_key,
            endpoint=provider_info['endpoint'],
            max_tokens_default=provider_info['max_tokens_default'],
            cost_per_1k_input=provider_info['cost_per_1k_input'],
            cost_per_1k_output=provider_info['cost_per_1k_output'],
            rate_limit_rpm=provider_info['rate_limit_rpm'],
            timeout_seconds=provider_info['timeout_seconds']
        )
        self.model = model

        # Initialize cache
        self.enable_cache = enable_cache
        if enable_cache:
            self.cache = TTLCache(maxsize=CACHE_MAX_SIZE, ttl=CACHE_DEFAULT_TTL)
        else:
            self.cache = None

        # Initialize circuit breaker
        self.enable_circuit_breaker = enable_circuit_breaker
        self.circuit_breaker = CircuitBreakerState()

        # Initialize provider clients
        self._init_clients()

        logger.info(
            f"ResponseGenerator initialized: provider={provider}, "
            f"model={model}, cache={enable_cache}, circuit_breaker={enable_circuit_breaker}"
        )

    def _init_clients(self):
        """Initialize API clients for providers."""
        if self.config.name == "claude":
            if not ANTHROPIC_AVAILABLE:
                raise ProviderConfigError(
                    "anthropic package not installed. Run: pip install anthropic"
                )
            self.claude_client = anthropic.Anthropic(api_key=self.config.api_key)

        elif self.config.name == "openai":
            if not OPENAI_AVAILABLE:
                raise ProviderConfigError(
                    "openai package not installed. Run: pip install openai"
                )
            self.openai_client = openai.OpenAI(api_key=self.config.api_key)

    def _check_circuit_breaker(self):
        """Check circuit breaker state and potentially raise exception."""
        if not self.enable_circuit_breaker:
            return

        if self.circuit_breaker.state == "open":
            # Check if timeout has passed
            if self.circuit_breaker.last_failure_time:
                elapsed = (datetime.utcnow() - self.circuit_breaker.last_failure_time).total_seconds()
                if elapsed >= CIRCUIT_BREAKER_TIMEOUT:
                    self.circuit_breaker.state = "half_open"
                    self.circuit_breaker.failures = 0
                    logger.info("Circuit breaker transitioning to half-open")
                else:
                    raise CircuitBreakerOpen(
                        f"Circuit breaker is open. Retry in {CIRCUIT_BREAKER_TIMEOUT - elapsed:.0f}s"
                    )

    def _record_success(self):
        """Record successful API call for circuit breaker."""
        if not self.enable_circuit_breaker:
            return

        self.circuit_breaker.state = "closed"
        self.circuit_breaker.failures = 0
        self.circuit_breaker.last_success_time = datetime.utcnow()

    def _record_failure(self):
        """Record failed API call for circuit breaker."""
        if not self.enable_circuit_breaker:
            return

        self.circuit_breaker.failures += 1
        self.circuit_breaker.last_failure_time = datetime.utcnow()

        if self.circuit_breaker.failures >= CIRCUIT_BREAKER_THRESHOLD:
            self.circuit_breaker.state = "open"
            logger.error(
                f"Circuit breaker opened after {CIRCUIT_BREAKER_THRESHOLD} failures"
            )

    def _call_claude_api(
        self,
        prompt: str,
        system_message: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Tuple[str, int, int]:
        """
        Call Claude API.

        Returns:
            Tuple of (response_text, input_tokens, output_tokens)
        """
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }

        if system_message:
            kwargs["system"] = system_message

        response = self.claude_client.messages.create(**kwargs)

        text = response.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        return text, input_tokens, output_tokens

    def _call_openai_api(
        self,
        prompt: str,
        system_message: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Tuple[str, int, int]:
        """
        Call OpenAI API.

        Returns:
            Tuple of (response_text, input_tokens, output_tokens)
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        text = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        return text, input_tokens, output_tokens

    def _analyze_quality(self, text: str) -> Tuple[Dict[str, float], float]:
        """
        Analyze quality of generated text using PES framework.

        Returns:
            Tuple of (features_dict, Q_score)
        """
        try:
            features = estimate_features(text)
            Q_score, _ = compute_Q(features)
            return features, Q_score
        except Exception as e:
            logger.error(f"Quality analysis failed: {e}")
            return None, None

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_message: Optional[str] = None,
        analyze_quality: bool = True,
        use_cache: bool = True,
        retry_attempts: int = 3
    ) -> LLMResponse:
        """
        Generate response from LLM with quality analysis.

        Args:
            prompt: User prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            system_message: Optional system message
            analyze_quality: Whether to analyze response quality
            use_cache: Whether to use cache
            retry_attempts: Number of retry attempts on failure

        Returns:
            LLMResponse object with generated text and metadata

        Raises:
            CircuitBreakerOpen: If circuit breaker is open
            APIResponseError: If API returns invalid response

        Example:
            >>> gen = ResponseGenerator(provider="claude")
            >>> response = gen.generate(
            ...     prompt="Explain photosynthesis briefly.",
            ...     temperature=0.5,
            ...     max_tokens=150
            ... )
            >>> print(response.text)
            >>> print(f"Quality: {response.quality_level}")
        """
        # Check circuit breaker
        self._check_circuit_breaker()

        # Check cache
        cache_key = None
        if use_cache and self.enable_cache:
            cache_key = generate_cache_key(
                prompt, self.config.name, self.model,
                temperature, max_tokens, system_message
            )
            if cache_key in self.cache:
                logger.info(f"Cache hit for key {cache_key[:8]}...")
                return self.cache[cache_key]

        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(retry_attempts):
            try:
                start_time = time.time()

                # Call appropriate API
                if self.config.name == "claude":
                    text, input_tokens, output_tokens = self._call_claude_api(
                        prompt, system_message, temperature, max_tokens
                    )
                elif self.config.name == "openai":
                    text, input_tokens, output_tokens = self._call_openai_api(
                        prompt, system_message, temperature, max_tokens
                    )
                else:
                    raise ProviderConfigError(f"Unsupported provider: {self.config.name}")

                latency_ms = (time.time() - start_time) * 1000

                # Calculate cost
                total_cost = calculate_cost(input_tokens, output_tokens, self.config)

                # Warn if expensive
                if total_cost > 0.50:
                    logger.warning(
                        f"Expensive request: ${total_cost:.4f} "
                        f"({input_tokens}+{output_tokens} tokens)"
                    )

                # Analyze quality
                quality_features = None
                quality_score = None
                if analyze_quality:
                    quality_features, quality_score = self._analyze_quality(text)

                # Create response object
                response = LLMResponse(
                    text=text,
                    provider=self.config.name,
                    model=self.model,
                    prompt_tokens=input_tokens,
                    completion_tokens=output_tokens,
                    total_cost_usd=total_cost,
                    latency_ms=latency_ms,
                    quality_features=quality_features,
                    quality_score=quality_score,
                    metadata={
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "system_message": system_message is not None
                    }
                )

                # Cache response
                if use_cache and self.enable_cache and cache_key:
                    self.cache[cache_key] = response

                # Record success
                self._record_success()

                logger.info(
                    f"Generated response: {input_tokens}+{output_tokens} tokens, "
                    f"${total_cost:.4f}, {latency_ms:.0f}ms, Q={quality_score:.4f if quality_score else 'N/A'}"
                )

                return response

            except Exception as e:
                last_exception = e
                logger.error(f"Attempt {attempt + 1}/{retry_attempts} failed: {e}")

                # Record failure
                self._record_failure()

                # Exponential backoff
                if attempt < retry_attempts - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)

        # All retries failed
        raise APIResponseError(
            f"Failed after {retry_attempts} attempts. Last error: {last_exception}"
        )


# ============================================================================
# PUBLIC API FUNCTIONS
# ============================================================================

def generate_response(
    prompt: str,
    provider: str = "claude",
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    system_message: Optional[str] = None,
    analyze_quality: bool = True,
    use_cache: bool = True
) -> LLMResponse:
    """
    Generate single LLM response with quality analysis (convenience function).

    Args:
        prompt: User prompt
        provider: LLM provider ("claude" or "openai")
        model: Specific model (defaults to provider's default)
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens to generate
        system_message: Optional system message
        analyze_quality: Whether to analyze response quality
        use_cache: Whether to use cache

    Returns:
        LLMResponse object

    Example:
        >>> response = generate_response(
        ...     prompt="You are a Senior Engineer. Write API docs.",
        ...     provider="claude",
        ...     temperature=0.5
        ... )
        >>> print(f"Cost: ${response.total_cost_usd:.4f}")
        >>> print(f"Q Score: {response.quality_score:.4f}")
    """
    generator = ResponseGenerator(provider=provider, model=model)
    return generator.generate(
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        system_message=system_message,
        analyze_quality=analyze_quality,
        use_cache=use_cache
    )


def estimate_cost(
    prompt: str,
    provider: str = "claude",
    model: Optional[str] = None,
    max_tokens: int = 2048
) -> Dict[str, float]:
    """
    Estimate cost before making API call.

    Args:
        prompt: User prompt
        provider: LLM provider
        model: Specific model
        max_tokens: Expected max output tokens

    Returns:
        Dictionary with cost estimates

    Example:
        >>> cost = estimate_cost(
        ...     prompt="Write a 1000-word essay on AI ethics.",
        ...     provider="claude"
        ... )
        >>> print(f"Estimated cost: ${cost['estimated_cost_usd']:.4f}")
        >>> print(f"Input tokens: {cost['input_tokens']}")
    """
    if provider not in PROVIDERS:
        raise ProviderConfigError(f"Unknown provider: {provider}")

    provider_info = PROVIDERS[provider]
    input_tokens = count_tokens_approximate(prompt)

    # Estimate output tokens (assume 50% of max if not specified)
    output_tokens = max_tokens // 2

    input_cost = (input_tokens / 1000) * provider_info['cost_per_1k_input']
    output_cost = (output_tokens / 1000) * provider_info['cost_per_1k_output']
    total_cost = input_cost + output_cost

    return {
        'input_tokens': input_tokens,
        'estimated_output_tokens': output_tokens,
        'estimated_cost_usd': total_cost,
        'cost_per_1k_input': provider_info['cost_per_1k_input'],
        'cost_per_1k_output': provider_info['cost_per_1k_output']
    }


def compare_providers(
    prompt: str,
    providers: List[str] = ["claude", "openai"],
    temperature: float = 0.7,
    max_tokens: int = 2048,
    **kwargs
) -> Dict[str, LLMResponse]:
    """
    Generate responses from multiple providers for A/B testing.

    Args:
        prompt: User prompt
        providers: List of provider names
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        **kwargs: Additional arguments passed to generate_response

    Returns:
        Dictionary mapping provider name to LLMResponse

    Example:
        >>> results = compare_providers(
        ...     prompt="Explain quantum computing briefly.",
        ...     providers=["claude", "openai"]
        ... )
        >>> for provider, response in results.items():
        ...     print(f"{provider}: Q={response.quality_score:.2f}, ${response.total_cost_usd:.4f}")
    """
    results = {}

    for provider in providers:
        try:
            response = generate_response(
                prompt=prompt,
                provider=provider,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            results[provider] = response
        except Exception as e:
            logger.error(f"Failed to generate response from {provider}: {e}")
            results[provider] = None

    return results


# ============================================================================
# INNOVATION FEATURES
# ============================================================================

def optimize_and_generate(
    initial_prompt: str,
    target_quality: float = 0.85,
    max_iterations: int = 3,
    provider: str = "claude"
) -> Tuple[str, LLMResponse]:
    """
    Iteratively improve prompt quality before generating final response.

    Uses LLM to suggest prompt improvements based on quality analysis.

    Args:
        initial_prompt: Starting prompt
        target_quality: Target Q score
        max_iterations: Maximum optimization iterations
        provider: LLM provider

    Returns:
        Tuple of (optimized_prompt, final_response)

    Example:
        >>> optimized, response = optimize_and_generate(
        ...     initial_prompt="Write about AI.",
        ...     target_quality=0.90
        ... )
        >>> print(f"Original → Optimized")
        >>> print(f"Q improved to: {response.quality_score:.4f}")
    """
    current_prompt = initial_prompt

    for iteration in range(max_iterations):
        # Analyze current prompt quality
        features = estimate_features(current_prompt)
        current_Q, _ = compute_Q(features)

        logger.info(f"Iteration {iteration + 1}: Q={current_Q:.4f}")

        if current_Q >= target_quality:
            logger.info(f"Target quality {target_quality:.2f} achieved!")
            break

        # Find weakest dimension
        weakest_dim = min(features.items(), key=lambda x: x[1])
        dim_name, dim_score = weakest_dim

        # Generate improvement suggestion using LLM
        improvement_prompt = f"""Analyze this prompt and suggest improvements to increase its {dim_name} score:

Prompt: "{current_prompt}"

Current {dim_name} score: {dim_score:.2f}
Target: {target_quality:.2f}

Provide an improved version that is more specific, structured, and clear. Output only the improved prompt, no explanations."""

        try:
            response = generate_response(
                prompt=improvement_prompt,
                provider=provider,
                temperature=0.3,  # Low temperature for consistency
                max_tokens=500,
                analyze_quality=False
            )
            current_prompt = response.text.strip()
        except Exception as e:
            logger.error(f"Optimization iteration {iteration + 1} failed: {e}")
            break

    # Generate final response with optimized prompt
    final_response = generate_response(
        prompt=current_prompt,
        provider=provider,
        analyze_quality=True
    )

    return current_prompt, final_response


# ============================================================================
# MAIN / DEMO
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("LLM RESPONSE GENERATOR - DEMO & TESTS")
    print("=" * 70)

    # Check if API keys are set
    claude_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')

    if not claude_key and not openai_key:
        print("\n⚠️  No API keys found!")
        print("Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable.")
        print("\nRunning in demo mode with mock responses...\n")

        # Demo mode - show what the API would look like
        print("Example 1: Basic Generation")
        print("-" * 70)
        print("Code:")
        print('  response = generate_response(')
        print('      prompt="You are a Senior Engineer. Write a brief API spec.",')
        print('      provider="claude"')
        print('  )')
        print("\nExpected output:")
        print("  Q Score: 0.8542")
        print("  Cost: $0.0089")
        print("  Latency: 1847ms")
        print("  Text: [API specification with endpoints, authentication, errors...]")

        print("\n" + "=" * 70)
        print("Example 2: Cost Estimation")
        print("-" * 70)
        cost = estimate_cost(
            prompt="Write a comprehensive 1000-word essay on machine learning.",
            provider="claude"
        )
        print(f"Input tokens: {cost['input_tokens']}")
        print(f"Estimated output tokens: {cost['estimated_output_tokens']}")
        print(f"Estimated cost: ${cost['estimated_cost_usd']:.4f}")

    else:
        # Real API tests
        provider = "claude" if claude_key else "openai"
        print(f"\n✓ Using {provider.upper()} API\n")

        # Test 1: Basic generation
        print("Test 1: Basic Generation")
        print("-" * 70)
        try:
            response = generate_response(
                prompt="You are a Senior Data Scientist. Explain linear regression in exactly 2 sentences.",
                provider=provider,
                temperature=0.5,
                max_tokens=100
            )
            print(f"✓ Response generated")
            print(f"  Text: {truncate_for_logging(response.text, 150)}")
            print(f"  Tokens: {response.prompt_tokens} + {response.completion_tokens} = {response.total_tokens}")
            print(f"  Cost: ${response.total_cost_usd:.4f}")
            print(f"  Latency: {response.latency_ms:.0f}ms")
            print(f"  Quality: {response.quality_level} (Q={response.quality_score:.4f})")
        except Exception as e:
            print(f"✗ Test failed: {e}")

        # Test 2: Cost estimation
        print("\nTest 2: Cost Estimation")
        print("-" * 70)
        cost = estimate_cost(
            prompt="Write a detailed technical specification for a REST API with 20 endpoints.",
            provider=provider,
            max_tokens=2000
        )
        print(f"✓ Cost estimated")
        print(f"  Input tokens: {cost['input_tokens']}")
        print(f"  Estimated output: {cost['estimated_output_tokens']} tokens")
        print(f"  Estimated cost: ${cost['estimated_cost_usd']:.4f}")

        # Test 3: Cache test
        print("\nTest 3: Cache Performance")
        print("-" * 70)
        try:
            prompt = "Count from 1 to 3."

            # First call (cache miss)
            start = time.time()
            resp1 = generate_response(prompt, provider=provider, max_tokens=50)
            time1 = (time.time() - start) * 1000

            # Second call (cache hit)
            start = time.time()
            resp2 = generate_response(prompt, provider=provider, max_tokens=50)
            time2 = (time.time() - start) * 1000

            print(f"✓ Cache test completed")
            print(f"  First call: {time1:.0f}ms (cache miss)")
            print(f"  Second call: {time2:.0f}ms (cache hit)")
            print(f"  Speedup: {time1/time2:.1f}x")
        except Exception as e:
            print(f"✗ Test failed: {e}")

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nFor production use:")
    print("1. Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable")
    print("2. Install dependencies: pip install anthropic openai cachetools")
    print("3. Import: from generate_response import generate_response")
    print("4. Use: response = generate_response(prompt='...', provider='claude')")
