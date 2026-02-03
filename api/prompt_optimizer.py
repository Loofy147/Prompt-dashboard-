"""
api/prompt_optimizer.py
LLM-powered prompt optimization with PES framework integration.

This module uses AI to automatically improve prompts by identifying weak
dimensions and generating optimized versions with comprehensive benchmarking
and cost tracking.

Quick Start:
    >>> from prompt_optimizer import optimize_prompt
    >>> result = optimize_prompt(
    ...     prompt="Write about AI.",
    ...     target_quality=0.85
    ... )
    >>> print(f"Improved from Q={result.original_q:.2f} to Q={result.optimized_q:.2f}")
    >>> print(f"Cost: ${result.total_cost_usd:.4f}")
    >>> print(f"Optimized: {result.optimized_prompt}")

Author: Prompt Dashboard Manager Team
Version: 1.0.0
License: MIT
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json
import time
import math

# Local imports
try:
    from quality_calculator import compute_Q
    from feature_analyzer import estimate_features
    from generate_response import generate_response, estimate_cost as estimate_llm_cost
except ImportError:
    # Fallback for standalone testing
    def compute_Q(features):
        weights = {'P': 0.18, 'T': 0.22, 'F': 0.20, 'S': 0.18, 'C': 0.12, 'R': 0.10}
        return sum(weights[k] * features[k] for k in weights), {}

    def estimate_features(text):
        return {'P': 0.5, 'T': 0.5, 'F': 0.5, 'S': 0.5, 'C': 0.5, 'R': 0.5}

    class MockResponse:
        def __init__(self, text):
            self.text = text
            self.total_cost_usd = 0.01
            self.total_tokens = 100
            self.latency_ms = 1000

    def generate_response(prompt, **kwargs):
        return MockResponse(prompt + " [IMPROVED]")

    def estimate_llm_cost(prompt, **kwargs):
        return {'estimated_cost_usd': 0.01, 'input_tokens': 50, 'estimated_output_tokens': 50}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# EXCEPTIONS
# ============================================================================

class CostLimitExceeded(Exception):
    """Raised when estimated cost exceeds budget."""
    pass


class OptimizationFailed(Exception):
    """Raised when optimization cannot improve prompt."""
    pass


class InvalidStrategy(Exception):
    """Raised when unknown optimization strategy specified."""
    pass


# ============================================================================
# ENUMS
# ============================================================================

class OptimizationStrategy(str, Enum):
    """Optimization strategy types."""
    BALANCED = "balanced"
    COST_EFFICIENT = "cost_efficient"
    MAX_QUALITY = "max_quality"


# ============================================================================
# META-PROMPT TEMPLATES
# ============================================================================

META_PROMPTS = {
    'P': """Analyze this prompt and improve its Persona (P) dimension to increase clarity of role and expertise.

Original Prompt: "{prompt}"

Current P Score: {p_score:.2f} / 1.00
Target P Score: ≥ 0.85

Improvements needed:
- Add explicit role specification (e.g., "You are a Senior [Role]")
- Include years of experience (e.g., "15+ years")
- Specify domain expertise (e.g., "specializing in [Domain]")
- Add credentials or background if relevant

CRITICAL: Output ONLY the improved prompt text. Do not include explanations, preambles, or meta-commentary. Keep all other aspects of the prompt unchanged.""",

    'T': """Improve the Tone (T) dimension of this prompt to ensure appropriate voice and style.

Original Prompt: "{prompt}"

Current T Score: {t_score:.2f} / 1.00
Target T Score: ≥ 0.85

Add:
- Explicit tone specification (formal/technical/persuasive/academic/casual)
- Consistent voice throughout
- Domain-appropriate language and style
- Example phrasing if helpful

Output ONLY the improved prompt. No explanations.""",

    'F': """Enhance the Format (F) dimension to clearly specify output structure.

Original Prompt: "{prompt}"

Current F Score: {f_score:.2f} / 1.00
Target F Score: ≥ 0.90

Add:
- Output structure specification (JSON schema, Markdown sections, table format, bullet points)
- Length constraints (word count, character limit, number of items)
- Section organization (specific headers, subsections)
- Template or schema if applicable

Output ONLY the improved prompt.""",

    'S': """Increase Specificity (S) by adding quantified details and concrete requirements.

Original Prompt: "{prompt}"

Current S Score: {s_score:.2f} / 1.00
Target S Score: ≥ 0.85

Add:
- Quantified metrics (latency targets, accuracy thresholds, performance goals)
- Numerical constraints (5 examples, 200 words, 3 sections, 10 bullet points)
- Specific technologies/frameworks/tools by name
- Concrete examples or edge cases

Output ONLY the improved prompt.""",

    'C': """Strengthen Constraints (C) by adding enforcement rules and validation criteria.

Original Prompt: "{prompt}"

Current C Score: {c_score:.2f} / 1.00
Target C Score: ≥ 0.80

Add:
- Enforcement rules using imperative language ("must include X", "cannot use Y", "always", "never")
- Validation criteria and quality gates
- Hard limits and requirements
- Error handling instructions
- Compliance requirements

Output ONLY the improved prompt.""",

    'R': """Enrich Context (R) by providing background information and use case details.

Original Prompt: "{prompt}"

Current R Score: {r_score:.2f} / 1.00
Target R Score: ≥ 0.75

Add:
- Background information or project context
- Target audience details (expertise level, role, needs)
- Success criteria or goals
- Use case examples or scenarios
- Related information that helps understanding

Output ONLY the improved prompt."""
}


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class OptimizationIteration:
    """Single iteration in the optimization process."""

    iteration_number: int
    prompt_text: str
    features: Dict[str, float]
    q_score: float
    improved_dimensions: List[str]
    cost_usd: float
    tokens_used: int
    latency_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class OptimizationResult:
    """Complete optimization result with benchmarks."""

    original_prompt: str
    optimized_prompt: str
    original_q: float
    optimized_q: float
    delta_q: float
    improvement_pct: float
    iterations: List[OptimizationIteration]
    total_cost_usd: float
    total_tokens: int
    strategy_used: str
    dimensions_improved: Dict[str, Tuple[float, float]]  # {dim: (before, after)}
    benchmark_summary: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def get_best_iteration(self) -> OptimizationIteration:
        """Get iteration with highest Q score."""
        return max(self.iterations, key=lambda x: x.q_score)

    def get_cost_per_point(self) -> float:
        """Calculate cost per 0.01 Q improvement."""
        if self.delta_q <= 0:
            return 0.0
        return self.total_cost_usd / (self.delta_q * 100)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'original_prompt': self.original_prompt,
            'optimized_prompt': self.optimized_prompt,
            'original_q': self.original_q,
            'optimized_q': self.optimized_q,
            'delta_q': self.delta_q,
            'improvement_pct': self.improvement_pct,
            'iterations': [it.to_dict() for it in self.iterations],
            'total_cost_usd': self.total_cost_usd,
            'total_tokens': self.total_tokens,
            'strategy_used': self.strategy_used,
            'dimensions_improved': self.dimensions_improved,
            'benchmark_summary': self.benchmark_summary,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class CostEstimate:
    """Cost estimation before optimization."""

    estimated_iterations: int
    estimated_tokens_per_iteration: int
    estimated_total_tokens: int
    estimated_cost_usd: float
    cost_breakdown: List[Dict[str, Any]]
    strategy: str
    current_q: float
    target_q: float
    delta_q: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


# ============================================================================
# STRATEGY CONFIGURATIONS
# ============================================================================

STRATEGY_CONFIGS = {
    OptimizationStrategy.BALANCED: {
        'target_q': 0.85,
        'max_cost': 0.20,
        'max_iterations': 3,
        'dimensions_per_iteration': 2,
        'temperature': 0.3,
        'description': 'Balanced approach: good quality at reasonable cost'
    },
    OptimizationStrategy.COST_EFFICIENT: {
        'target_q': 0.75,
        'max_cost': 0.05,
        'max_iterations': 2,
        'dimensions_per_iteration': 1,
        'temperature': 0.5,
        'description': 'Budget-friendly: essential improvements only'
    },
    OptimizationStrategy.MAX_QUALITY: {
        'target_q': 0.90,
        'max_cost': 0.50,
        'max_iterations': 5,
        'dimensions_per_iteration': 3,
        'temperature': 0.2,
        'description': 'Premium quality: comprehensive optimization'
    }
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_dimension_impact(
    dimension: str,
    current_score: float,
    target_score: float = 0.85
) -> float:
    """
    Calculate improvement impact for a dimension.

    Impact = weight × gap × improvement_probability

    Args:
        dimension: PES dimension (P, T, F, S, C, R)
        current_score: Current dimension score
        target_score: Target dimension score

    Returns:
        Impact score (higher = more beneficial to improve)
    """
    WEIGHTS = {'P': 0.18, 'T': 0.22, 'F': 0.20, 'S': 0.18, 'C': 0.12, 'R': 0.10}

    gap = target_score - current_score
    if gap <= 0:
        return 0.0

    # Improvement probability decreases as score increases
    # Easy to go from 0.3→0.6, harder to go from 0.8→0.9
    improvement_probability = 1.0 - (current_score ** 2)

    impact = WEIGHTS[dimension] * gap * improvement_probability
    return impact


def select_dimensions_to_improve(
    features: Dict[str, float],
    num_dimensions: int = 2,
    threshold: float = 0.75
) -> List[str]:
    """
    Select dimensions to improve based on impact scoring.

    Args:
        features: Current feature scores
        num_dimensions: Number of dimensions to improve
        threshold: Minimum score threshold (improve if below)

    Returns:
        List of dimension keys sorted by improvement impact
    """
    # Calculate impact for each dimension below threshold
    impacts = []
    for dim, score in features.items():
        if score < threshold:
            impact = calculate_dimension_impact(dim, score)
            impacts.append((dim, impact, score))

    # Sort by impact (highest first)
    impacts.sort(key=lambda x: x[1], reverse=True)

    # Return top N dimensions
    selected = [dim for dim, impact, score in impacts[:num_dimensions]]

    if not selected:
        # If all above threshold, improve lowest scoring dimension
        lowest = min(features.items(), key=lambda x: x[1])
        selected = [lowest[0]]

    logger.info(f"Selected dimensions to improve: {selected}")
    return selected


def merge_improvements(
    original: str,
    improvements: List[str],
    provider: str = "claude"
) -> str:
    """
    Merge multiple dimension improvements into single cohesive prompt.

    Args:
        original: Original prompt
        improvements: List of improved versions
        provider: LLM provider

    Returns:
        Merged prompt combining all improvements
    """
    if len(improvements) == 1:
        return improvements[0]

    # Create merge prompt
    merge_prompt = f"""You have an original prompt and {len(improvements)} improved versions, each focusing on different aspects.

Original:
{original}

Improved Versions:
{chr(10).join(f"{i+1}. {imp}" for i, imp in enumerate(improvements))}

Combine the best elements from all improved versions into a single, cohesive prompt. Keep all improvements but ensure the result flows naturally and is well-structured.

Output ONLY the final merged prompt."""

    try:
        response = generate_response(
            merge_prompt,
            provider=provider,
            temperature=0.3,
            max_tokens=800,
            analyze_quality=False
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Merge failed: {e}. Using first improvement.")
        return improvements[0]


# ============================================================================
# COST ESTIMATION
# ============================================================================

def estimate_optimization_cost(
    prompt: str,
    current_q: float,
    target_q: float,
    strategy: str = "balanced",
    provider: str = "claude"
) -> CostEstimate:
    """
    Estimate cost before optimizing.

    Args:
        prompt: Prompt to optimize
        current_q: Current quality score
        target_q: Target quality score
        strategy: Optimization strategy
        provider: LLM provider

    Returns:
        CostEstimate with detailed breakdown

    Example:
        >>> estimate = estimate_optimization_cost(
        ...     prompt="Write about AI.",
        ...     current_q=0.40,
        ...     target_q=0.85,
        ...     strategy="balanced"
        ... )
        >>> print(f"Estimated cost: ${estimate.estimated_cost_usd:.4f}")
        >>> print(f"Iterations: {estimate.estimated_iterations}")
    """
    delta_q = target_q - current_q

    if delta_q <= 0:
        return CostEstimate(
            estimated_iterations=0,
            estimated_tokens_per_iteration=0,
            estimated_total_tokens=0,
            estimated_cost_usd=0.0,
            cost_breakdown=[],
            strategy=strategy,
            current_q=current_q,
            target_q=target_q,
            delta_q=delta_q
        )

    # Get strategy config
    try:
        strategy_enum = OptimizationStrategy(strategy)
    except ValueError:
        strategy_enum = OptimizationStrategy.BALANCED

    config = STRATEGY_CONFIGS[strategy_enum]

    # Estimate iterations needed
    # Assumption: Each iteration improves Q by ~0.10-0.15
    avg_improvement_per_iteration = 0.12
    estimated_iterations = min(
        math.ceil(delta_q / avg_improvement_per_iteration),
        config['max_iterations']
    )

    # Estimate tokens per iteration
    # Input: original prompt + meta-prompt template (~400 tokens)
    # Output: improved prompt (~300 tokens)
    input_tokens_per_iteration = 400
    output_tokens_per_iteration = 300
    total_tokens_per_iteration = input_tokens_per_iteration + output_tokens_per_iteration

    # Multiply by dimensions improved per iteration
    dimensions_per_iteration = config['dimensions_per_iteration']
    tokens_per_iteration = total_tokens_per_iteration * dimensions_per_iteration

    # Add merge step tokens if multiple dimensions
    if dimensions_per_iteration > 1:
        tokens_per_iteration += 500  # Merge step

    estimated_total_tokens = tokens_per_iteration * estimated_iterations

    # Estimate cost using provider rates
    cost_data = estimate_llm_cost(
        prompt=prompt,
        provider=provider,
        max_tokens=output_tokens_per_iteration
    )

    # Scale up for iterations
    cost_per_iteration = cost_data['estimated_cost_usd'] * dimensions_per_iteration
    if dimensions_per_iteration > 1:
        cost_per_iteration += cost_data['estimated_cost_usd'] * 0.5  # Merge

    estimated_cost = cost_per_iteration * estimated_iterations

    # Build breakdown
    cost_breakdown = []
    for i in range(estimated_iterations):
        cost_breakdown.append({
            'iteration': i + 1,
            'dimensions': dimensions_per_iteration,
            'tokens': tokens_per_iteration,
            'cost_usd': cost_per_iteration
        })

    return CostEstimate(
        estimated_iterations=estimated_iterations,
        estimated_tokens_per_iteration=tokens_per_iteration,
        estimated_total_tokens=estimated_total_tokens,
        estimated_cost_usd=estimated_cost,
        cost_breakdown=cost_breakdown,
        strategy=strategy,
        current_q=current_q,
        target_q=target_q,
        delta_q=delta_q
    )


# ============================================================================
# MAIN OPTIMIZATION FUNCTION
# ============================================================================

def optimize_prompt(
    prompt: str,
    target_quality: float = 0.85,
    strategy: str = "balanced",
    max_iterations: int = 5,
    provider: str = "claude",
    estimate_first: bool = True,
    progress_callback: Optional[Callable[[OptimizationIteration], None]] = None
) -> OptimizationResult:
    """
    Optimize prompt using LLM-powered iterative refinement.

    Args:
        prompt: Original prompt to optimize
        target_quality: Target Q score (0.0-1.0)
        strategy: "balanced", "cost_efficient", or "max_quality"
        max_iterations: Maximum optimization iterations
        provider: LLM provider ("claude" or "openai")
        estimate_first: If True, estimate costs before optimizing
        progress_callback: Optional callback for progress updates

    Returns:
        OptimizationResult with complete optimization history

    Raises:
        CostLimitExceeded: If estimated cost exceeds strategy budget
        OptimizationFailed: If unable to improve prompt

    Example:
        >>> result = optimize_prompt(
        ...     prompt="Write about machine learning.",
        ...     target_quality=0.85,
        ...     strategy="balanced"
        ... )
        >>> print(f"Improved: {result.original_q:.2f} → {result.optimized_q:.2f}")
        >>> print(f"Cost: ${result.total_cost_usd:.4f}")
        >>> print(result.optimized_prompt)
    """
    logger.info(f"Starting optimization: target_q={target_quality}, strategy={strategy}")

    # Validate strategy
    try:
        strategy_enum = OptimizationStrategy(strategy)
    except ValueError:
        raise InvalidStrategy(f"Unknown strategy: {strategy}")

    config = STRATEGY_CONFIGS[strategy_enum]
    max_iterations = min(max_iterations, config['max_iterations'])

    # STEP 1: Analyze original prompt
    logger.info("Step 1: Analyzing original prompt...")
    original_features = estimate_features(prompt)
    original_q, _ = compute_Q(original_features)

    logger.info(f"Original Q: {original_q:.4f}")
    logger.info(f"Original features: {original_features}")

    # Check if already meets target
    if original_q >= target_quality:
        logger.info("Prompt already meets target quality!")
        return OptimizationResult(
            original_prompt=prompt,
            optimized_prompt=prompt,
            original_q=original_q,
            optimized_q=original_q,
            delta_q=0.0,
            improvement_pct=0.0,
            iterations=[],
            total_cost_usd=0.0,
            total_tokens=0,
            strategy_used=strategy,
            dimensions_improved={},
            benchmark_summary={
                'already_optimal': True,
                'original_q': original_q,
                'target_q': target_quality
            }
        )

    # STEP 2: Cost estimation
    if estimate_first:
        logger.info("Step 2: Estimating costs...")
        estimate = estimate_optimization_cost(
            prompt, original_q, target_quality, strategy, provider
        )

        logger.info(f"Estimated cost: ${estimate.estimated_cost_usd:.4f}")
        logger.info(f"Estimated iterations: {estimate.estimated_iterations}")

        if estimate.estimated_cost_usd > config['max_cost']:
            raise CostLimitExceeded(
                f"Estimated cost ${estimate.estimated_cost_usd:.4f} "
                f"exceeds budget ${config['max_cost']:.4f} for {strategy} strategy"
            )

    # STEP 3: Iterative optimization
    logger.info(f"Step 3: Starting optimization loop (max {max_iterations} iterations)...")

    current_prompt = prompt
    current_features = original_features.copy()
    current_q = original_q

    iterations = []
    total_cost = 0.0
    total_tokens = 0

    for iteration_num in range(1, max_iterations + 1):
        logger.info(f"\n--- Iteration {iteration_num}/{max_iterations} ---")
        logger.info(f"Current Q: {current_q:.4f}")

        # 3a. Identify weak dimensions
        dimensions_to_improve = select_dimensions_to_improve(
            current_features,
            num_dimensions=config['dimensions_per_iteration'],
            threshold=0.75
        )

        if not dimensions_to_improve:
            logger.info("No dimensions to improve. Stopping.")
            break

        logger.info(f"Improving dimensions: {dimensions_to_improve}")

        # 3b & 3c. Generate improvements for each dimension
        improvements = []
        iteration_cost = 0.0
        iteration_tokens = 0
        iteration_start = time.time()

        for dim in dimensions_to_improve:
            logger.info(f"Improving {dim} (current: {current_features[dim]:.2f})...")

            # Generate meta-prompt
            meta_prompt = META_PROMPTS[dim].format(
                prompt=current_prompt,
                p_score=current_features.get('P', 0),
                t_score=current_features.get('T', 0),
                f_score=current_features.get('F', 0),
                s_score=current_features.get('S', 0),
                c_score=current_features.get('C', 0),
                r_score=current_features.get('R', 0)
            )

            # Call LLM
            try:
                response = generate_response(
                    meta_prompt,
                    provider=provider,
                    temperature=config['temperature'],
                    max_tokens=600,
                    analyze_quality=False
                )

                improved_text = response.text.strip()
                improvements.append(improved_text)

                iteration_cost += response.total_cost_usd
                iteration_tokens += response.total_tokens

                logger.info(f"  ✓ Generated improvement for {dim}")

            except Exception as e:
                logger.error(f"Failed to improve {dim}: {e}")
                continue

        if not improvements:
            logger.error("No improvements generated. Stopping.")
            break

        # 3d. Merge improvements
        if len(improvements) > 1:
            logger.info("Merging improvements...")
            current_prompt = merge_improvements(current_prompt, improvements, provider)
        else:
            current_prompt = improvements[0]

        # 3e. Re-analyze
        current_features = estimate_features(current_prompt)
        new_q, _ = compute_Q(current_features)

        iteration_latency = (time.time() - iteration_start) * 1000

        # Record iteration
        iteration_data = OptimizationIteration(
            iteration_number=iteration_num,
            prompt_text=current_prompt,
            features=current_features.copy(),
            q_score=new_q,
            improved_dimensions=dimensions_to_improve,
            cost_usd=iteration_cost,
            tokens_used=iteration_tokens,
            latency_ms=iteration_latency
        )
        iterations.append(iteration_data)

        total_cost += iteration_cost
        total_tokens += iteration_tokens

        logger.info(f"Iteration {iteration_num} complete:")
        logger.info(f"  Q: {current_q:.4f} → {new_q:.4f} (Δ={new_q - current_q:+.4f})")
        logger.info(f"  Cost: ${iteration_cost:.4f}")
        logger.info(f"  Tokens: {iteration_tokens}")

        # Callback for progress
        if progress_callback:
            progress_callback(iteration_data)

        # 3f. Check convergence
        if new_q >= target_quality:
            logger.info(f"✓ Target quality {target_quality:.2f} achieved!")
            current_q = new_q
            break

        if new_q <= current_q:
            logger.warning("No improvement in this iteration. Stopping.")
            break

        current_q = new_q

        # Check cost limit
        if total_cost > config['max_cost']:
            logger.warning(f"Cost limit ${config['max_cost']:.4f} exceeded. Stopping.")
            break

    # STEP 4: Compile results
    final_features = estimate_features(current_prompt)
    final_q, _ = compute_Q(final_features)

    delta_q = final_q - original_q
    improvement_pct = (delta_q / original_q * 100) if original_q > 0 else 0

    # Build dimensions_improved dict
    dimensions_improved = {}
    for dim in ['P', 'T', 'F', 'S', 'C', 'R']:
        before = original_features[dim]
        after = final_features[dim]
        if abs(after - before) > 0.01:  # Significant change
            dimensions_improved[dim] = (before, after)

    # Build benchmark summary
    benchmark_summary = {
        'iterations_used': len(iterations),
        'target_achieved': final_q >= target_quality,
        'quality_improvement': {
            'original': original_q,
            'final': final_q,
            'delta': delta_q,
            'pct_change': improvement_pct
        },
        'cost_efficiency': {
            'total_cost': total_cost,
            'cost_per_point': (total_cost / (delta_q * 100)) if delta_q > 0 else 0,
            'tokens_used': total_tokens
        },
        'dimensions_changed': len(dimensions_improved),
        'strategy': strategy
    }

    result = OptimizationResult(
        original_prompt=prompt,
        optimized_prompt=current_prompt,
        original_q=original_q,
        optimized_q=final_q,
        delta_q=delta_q,
        improvement_pct=improvement_pct,
        iterations=iterations,
        total_cost_usd=total_cost,
        total_tokens=total_tokens,
        strategy_used=strategy,
        dimensions_improved=dimensions_improved,
        benchmark_summary=benchmark_summary
    )

    logger.info("\n" + "=" * 70)
    logger.info("OPTIMIZATION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Original Q:  {original_q:.4f}")
    logger.info(f"Optimized Q: {final_q:.4f}")
    logger.info(f"Improvement: +{delta_q:.4f} ({improvement_pct:+.1f}%)")
    logger.info(f"Total Cost:  ${total_cost:.4f}")
    logger.info(f"Iterations:  {len(iterations)}")
    logger.info("=" * 70)

    return result


# ============================================================================
# REPORTING FUNCTIONS
# ============================================================================

def generate_optimization_report(
    result: OptimizationResult,
    format: str = "markdown"
) -> str:
    """
    Generate comprehensive optimization report.

    Args:
        result: OptimizationResult object
        format: "markdown", "html", or "json"

    Returns:
        Formatted report string

    Example:
        >>> report = generate_optimization_report(result, format="markdown")
        >>> print(report)
    """
    if format == "json":
        return json.dumps(result.to_dict(), indent=2)

    if format == "markdown":
        report = f"""# Prompt Optimization Report

## Executive Summary

**Status**: {'✓ Success' if result.benchmark_summary['target_achieved'] else '⚠ Partial'}
**Strategy**: {result.strategy_used}
**Improvement**: {result.original_q:.4f} → {result.optimized_q:.4f} (+{result.delta_q:.4f}, {result.improvement_pct:+.1f}%)
**Cost**: ${result.total_cost_usd:.4f} ({result.total_tokens} tokens)
**Iterations**: {len(result.iterations)}

---

## Quality Breakdown

### Before Optimization
```
Q Score: {result.original_q:.4f}
"""

        # Original features
        original_features = result.iterations[0].features if result.iterations else {}
        for dim in ['P', 'T', 'F', 'S', 'C', 'R']:
            before = result.dimensions_improved.get(dim, (0, 0))[0] if dim in result.dimensions_improved else original_features.get(dim, 0)
            report += f"{dim}: {before:.2f}  "

        report += f"""
```

### After Optimization
```
Q Score: {result.optimized_q:.4f}
"""

        # Final features
        if result.iterations:
            final_features = result.iterations[-1].features
            for dim in ['P', 'T', 'F', 'S', 'C', 'R']:
                score = final_features.get(dim, 0)
                change = ""
                if dim in result.dimensions_improved:
                    before, after = result.dimensions_improved[dim]
                    delta = after - before
                    change = f" ({delta:+.2f})"
                report += f"{dim}: {score:.2f}{change}  "

        report += f"""
```

---

## Iteration Timeline

"""
        for iteration in result.iterations:
            report += f"""**Iteration {iteration.iteration_number}**
- Improved: {', '.join(iteration.improved_dimensions)}
- Q Score: {iteration.q_score:.4f}
- Cost: ${iteration.cost_usd:.4f}
- Time: {iteration.latency_ms:.0f}ms

"""

        report += f"""---

## Cost Analysis

- **Total Spent**: ${result.total_cost_usd:.4f}
- **Tokens Used**: {result.total_tokens:,}
- **Cost per Quality Point**: ${result.get_cost_per_point():.4f} per 0.01 Q improvement
- **Strategy Budget**: {STRATEGY_CONFIGS[OptimizationStrategy(result.strategy_used)]['max_cost']} USD

---

## Optimized Prompt

```
{result.optimized_prompt}
```

---

## Recommendations

"""
        if result.optimized_q < 0.90:
            report += "- Consider using 'max_quality' strategy for further improvements\n"
        if result.total_cost_usd > 0.20:
            report += "- High optimization cost - consider 'cost_efficient' strategy for future prompts\n"
        if len(result.iterations) == 1:
            report += "- Single iteration - could benefit from additional refinement\n"

        report += "\n---\n*Generated by Prompt Dashboard Manager*"

        return report

    # HTML format
    return f"<html><body><h1>Optimization Report</h1><pre>{generate_optimization_report(result, 'markdown')}</pre></body></html>"


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("PROMPT OPTIMIZER - DEMO & TESTS")
    print("=" * 70)

    # Test Case 1: Basic optimization
    print("\nTest 1: Basic Optimization")
    print("-" * 70)

    test_prompt = "Write about artificial intelligence."

    # Analyze original
    features = estimate_features(test_prompt)
    q_original, _ = compute_Q(features)
    print(f"Original prompt: {test_prompt}")
    print(f"Original Q: {q_original:.4f}")
    print(f"Original features: {features}")

    # Estimate cost
    print("\nCost Estimation:")
    estimate = estimate_optimization_cost(
        test_prompt,
        current_q=q_original,
        target_q=0.80,
        strategy="balanced"
    )
    print(f"  Estimated iterations: {estimate.estimated_iterations}")
    print(f"  Estimated cost: ${estimate.estimated_cost_usd:.4f}")
    print(f"  Estimated tokens: {estimate.estimated_total_tokens}")

    # Note: Full optimization requires actual API keys
    print("\n⚠️  Full optimization requires API keys (ANTHROPIC_API_KEY or OPENAI_API_KEY)")
    print("Set environment variables to run live optimization.")

    # Test Case 2: Already optimal prompt
    print("\n" + "=" * 70)
    print("Test 2: Already Optimal Prompt")
    print("-" * 70)

    good_prompt = """You are a Senior Software Engineer with 15+ years of experience in distributed systems.

Create a detailed technical specification for a REST API with the following requirements:
- Authentication using JWT tokens
- Rate limiting (100 requests per minute)
- Error handling with standard HTTP codes
- OpenAPI 3.0 documentation

Output format: JSON with the following structure:
- endpoints: array of endpoint definitions
- security: authentication scheme
- error_codes: HTTP status code mappings

Context: This API will serve 1 million daily active users with target latency <200ms."""

    features = estimate_features(good_prompt)
    q_good, _ = compute_Q(features)
    print(f"Q Score: {q_good:.4f}")
    print(f"Features: {features}")

    if q_good >= 0.85:
        print("✓ Prompt already meets quality target (Q ≥ 0.85)")

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nFor production use:")
    print("1. Set ANTHROPIC_API_KEY or OPENAI_API_KEY")
    print("2. Import: from prompt_optimizer import optimize_prompt")
    print("3. Use: result = optimize_prompt(prompt, target_quality=0.85)")
    print("4. Access: result.optimized_prompt, result.total_cost_usd, etc.")
