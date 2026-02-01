"""
quality_calculator.py
Core module for computing PES quality scores from prompt features.

Quality Framework (PES):
- P (Persona): Explicit role and experience specification
- T (Tone): Appropriate voice and style for domain
- F (Format): Structured output specification
- S (Specificity): Quantified constraints and details
- C (Constraints): Enforcement mechanisms and validation
- R (Context): Background information and richness

Q = 0.18×P + 0.22×T + 0.20×F + 0.18×S + 0.12×C + 0.10×R
"""

from typing import Dict, Tuple
import math

# PES quality weights (sum = 1.0)
WEIGHTS = {
    'wP': 0.18,  # Persona
    'wT': 0.22,  # Tone
    'wF': 0.20,  # Format
    'wS': 0.18,  # Specificity
    'wC': 0.12,  # Constraints
    'wR': 0.10   # Context
}


def validate_features(features: Dict[str, float]) -> None:
    """
    Validate that all feature scores are in valid range [0, 1].

    Args:
        features: Dictionary with keys P, T, F, S, C, R

    Raises:
        ValueError: If any score is outside [0, 1] or required keys missing
    """
    required_keys = {'P', 'T', 'F', 'S', 'C', 'R'}

    if not all(key in features for key in required_keys):
        missing = required_keys - set(features.keys())
        raise ValueError(f"Missing required features: {missing}")

    for key, value in features.items():
        if key not in required_keys:
            continue

        if not isinstance(value, (int, float)):
            raise ValueError(f"Feature {key} must be numeric, got {type(value)}")

        if not (0 <= value <= 1):
            raise ValueError(
                f"Feature {key}={value} is out of bounds. "
                f"All scores must be in range [0, 1]"
            )


def compute_Q(
    features: Dict[str, float],
    weights: Dict[str, float] = None
) -> Tuple[float, Dict[str, float]]:
    """
    Compute composite quality score Q from feature values.

    Args:
        features: Dict with keys P, T, F, S, C, R (all in range 0-1)
        weights: Optional custom weights (defaults to WEIGHTS)

    Returns:
        Tuple of (Q_score, breakdown_dict)
        - Q_score: Composite quality score (0-1 range)
        - breakdown_dict: Component contributions {wP_P, wT_T, ...}

    Raises:
        ValueError: If features are invalid

    Example:
        >>> features = {'P': 0.92, 'T': 0.88, 'F': 0.95,
        ...             'S': 0.90, 'C': 0.85, 'R': 0.70}
        >>> Q, breakdown = compute_Q(features)
        >>> print(f"Q = {Q:.4f}")
        Q = 0.8766
        >>> print(breakdown)
        {'wP_P': 0.1656, 'wT_T': 0.1936, 'wF_F': 0.1900,
         'wS_S': 0.1620, 'wC_C': 0.1020, 'wR_R': 0.0700}
    """
    # Validate inputs
    validate_features(features)

    # Use default weights if not provided
    if weights is None:
        weights = WEIGHTS

    # Extract values
    P = features['P']
    T = features['T']
    F = features['F']
    S = features['S']
    C = features['C']
    R = features['R']

    # Compute weighted components (4-decimal precision)
    breakdown = {
        'wP_P': round(weights['wP'] * P, 4),
        'wT_T': round(weights['wT'] * T, 4),
        'wF_F': round(weights['wF'] * F, 4),
        'wS_S': round(weights['wS'] * S, 4),
        'wC_C': round(weights['wC'] * C, 4),
        'wR_R': round(weights['wR'] * R, 4)
    }

    # Sum components to get Q
    Q = sum(breakdown.values())

    return Q, breakdown


def compute_Q_batch(feature_list: list[Dict[str, float]]) -> list[Tuple[float, Dict[str, float]]]:
    """
    Compute Q scores for multiple prompts efficiently.

    Args:
        feature_list: List of feature dictionaries

    Returns:
        List of (Q_score, breakdown) tuples
    """
    results = []
    for features in feature_list:
        try:
            Q, breakdown = compute_Q(features)
            results.append((Q, breakdown))
        except ValueError as e:
            # Store error result
            results.append((None, {'error': str(e)}))

    return results


def get_quality_level(Q: float) -> str:
    """
    Map Q score to qualitative quality level.

    Args:
        Q: Quality score (0-1)

    Returns:
        Quality level string: "Excellent", "Good", "Fair", or "Poor"
    """
    if Q >= 0.90:
        return "Excellent"
    elif Q >= 0.80:
        return "Good"
    elif Q >= 0.70:
        return "Fair"
    else:
        return "Poor"


def suggest_improvements(features: Dict[str, float], threshold: float = 0.75) -> list[str]:
    """
    Generate improvement suggestions for low-scoring dimensions.

    Args:
        features: Feature scores dict
        threshold: Minimum acceptable score (default 0.75)

    Returns:
        List of actionable suggestions
    """
    suggestions = []

    if features['P'] < threshold:
        suggestions.append(
            "Improve Persona: Add explicit role specification "
            "(e.g., 'You are a [role] with [experience]')"
        )

    if features['T'] < threshold:
        suggestions.append(
            "Improve Tone: Specify desired voice "
            "(formal/casual/technical) or include example phrasing"
        )

    if features['F'] < threshold:
        suggestions.append(
            "Improve Format: Define output structure "
            "(JSON schema, bullet points, table, word count)"
        )

    if features['S'] < threshold:
        suggestions.append(
            "Improve Specificity: Add quantified constraints "
            "(character limits, numerical targets, time bounds)"
        )

    if features['C'] < threshold:
        suggestions.append(
            "Improve Constraints: Insert enforcement rules "
            "(cite sources, mark uncertainties, validation criteria)"
        )

    if features['R'] < threshold:
        suggestions.append(
            "Improve Context: Provide background information "
            "(use case, target audience, success metrics)"
        )

    return suggestions


def benchmark_performance(n: int = 1000) -> float:
    """
    Benchmark Q calculation performance.

    Args:
        n: Number of calculations to perform

    Returns:
        Average time per calculation in milliseconds
    """
    import time

    test_features = {
        'P': 0.90, 'T': 0.85, 'F': 0.92,
        'S': 0.88, 'C': 0.80, 'R': 0.75
    }

    start = time.perf_counter()
    for _ in range(n):
        compute_Q(test_features)
    end = time.perf_counter()

    avg_time_ms = ((end - start) / n) * 1000
    return avg_time_ms


if __name__ == '__main__':
    # Example usage and testing
    print("Quality Calculator Demo")
    print("=" * 50)

    # Example 1: High-quality prompt
    features_high = {
        'P': 0.92,  # Strong persona
        'T': 0.88,  # Appropriate tone
        'F': 0.95,  # Well-defined format
        'S': 0.90,  # Specific constraints
        'C': 0.85,  # Clear constraints
        'R': 0.70   # Good context
    }

    Q, breakdown = compute_Q(features_high)
    print("\nExample 1: High-Quality Prompt")
    print(f"Features: {features_high}")
    print(f"Breakdown: {breakdown}")
    print(f"Q Score: {Q:.4f} ({get_quality_level(Q)})")

    # Example 2: Low-quality prompt
    features_low = {
        'P': 0.50, 'T': 0.60, 'F': 0.55,
        'S': 0.45, 'C': 0.40, 'R': 0.35
    }

    Q2, breakdown2 = compute_Q(features_low)
    print("\nExample 2: Low-Quality Prompt")
    print(f"Q Score: {Q2:.4f} ({get_quality_level(Q2)})")
    print("Suggestions:")
    for suggestion in suggest_improvements(features_low):
        print(f"  - {suggestion}")

    # Performance benchmark
    print("\nPerformance Benchmark:")
    avg_time = benchmark_performance(1000)
    print(f"Average time per calculation: {avg_time:.4f}ms")
    print(f"Target: <1ms per calculation - {'✓ PASS' if avg_time < 1 else '✗ FAIL'}")
