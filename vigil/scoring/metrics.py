"""
Scoring metrics for cognitive benchmarks.

Implements the multi-metric scoring system for cognitive profile generation.
Each metric measures a different aspect of cognitive performance.
"""

from typing import Dict, List, Any, Optional
from vigil.environments.base import EnvironmentState


def compute_correctness(
    final_answer: str,
    hidden_rule: str,
    verify_fn: callable = None
) -> float:
    """
    Compute correctness score (binary pass/fail).

    Args:
        final_answer: Model's submitted answer
        hidden_rule: Expected rule/answer
        verify_fn: Optional custom verification function

    Returns:
        1.0 if correct, 0.0 otherwise
    """
    if verify_fn:
        return 1.0 if verify_fn(final_answer) else 0.0

    # Simple string matching fallback
    answer_lower = final_answer.lower().strip()
    rule_lower = hidden_rule.lower().strip()

    # Check if answer contains key parts of the rule
    if rule_lower in answer_lower:
        return 1.0

    # Check for common affirmative patterns if rule is about concept formation
    if any(pattern in answer_lower for pattern in [
        "core features", "shared features", "category",
        "same group", "belong to"
    ]):
        return 1.0

    return 0.0


def compute_efficiency(
    state: EnvironmentState,
    optimal_path_length: int = 5
) -> float:
    """
    Compute path efficiency score.

    Measures how efficiently the model explored the graph.
    Higher score = fewer unnecessary actions.

    Args:
        state: Final environment state
        optimal_path_length: Expected optimal path length

    Returns:
        Score between 0.0 and 1.0
    """
    actions_taken = len(state.action_history)

    if actions_taken == 0:
        return 0.0

    # Efficiency = optimal / actual
    # Perfect score if actions <= optimal
    # Decreasing score for each extra action
    efficiency = optimal_path_length / max(actions_taken, optimal_path_length)

    return min(1.0, efficiency)


def compute_evidence_quality(
    state: EnvironmentState,
    required_evidence_count: int = 3
) -> float:
    """
    Compute evidence quality score.

    Measures whether the model visited and collected sufficient evidence.

    Args:
        state: Final environment state
        required_evidence_count: Minimum evidence nodes needed

    Returns:
        Score between 0.0 and 1.0
    """
    evidence_nodes = len(state.evidence_nodes)

    if evidence_nodes == 0:
        return 0.0

    # Score based on proportion of required evidence found
    quality = evidence_nodes / required_evidence_count

    return min(1.0, quality)


def compute_calibration(
    state: EnvironmentState,
    is_correct: bool
) -> float:
    """
    Compute calibration score.

    Measures whether the model's confidence matches its accuracy.
    Well-calibrated models have confidence ≈ correctness.

    Args:
        state: Final environment state
        is_correct: Whether final answer was correct

    Returns:
        Score between 0.0 and 1.0
    """
    confidence_history = state.confidence_history

    if not confidence_history:
        return 0.5  # Default if no confidence provided

    final_confidence = confidence_history[-1]
    correctness_value = 1.0 if is_correct else 0.0

    # Calibration = 1 - |confidence - correctness|
    calibration = 1.0 - abs(final_confidence - correctness_value)

    return calibration


def compute_recovery(
    state: EnvironmentState,
    contradiction_detected: bool = False
) -> float:
    """
    Compute recovery behavior score.

    Measures whether the model adapts after encountering contradictions
    or making errors.

    Args:
        state: Final environment state
        contradiction_detected: Whether a contradiction was encountered

    Returns:
        Score between 0.0 and 1.0
    """
    action_history = state.action_history

    if not action_history:
        return 0.5

    # Check if model changed strategy after potential failure
    # Simple heuristic: did it backtrack and try a different path?
    backtrack_count = sum(
        1 for a in action_history
        if a.action_type.name == "BACKTRACK"
    )

    if backtrack_count == 0:
        # No backtracking - either perfect or no recovery
        return 0.5

    # Some backtracking shows adaptive behavior
    # Too much backtracking might indicate confusion
    if backtrack_count <= 2:
        return 1.0
    elif backtrack_count <= 4:
        return 0.7
    else:
        return 0.4


def compute_weighted_score(
    scores: Dict[str, float],
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Compute weighted overall score from metric scores.

    Args:
        scores: Dictionary mapping metric names to scores
        weights: Dictionary mapping metric names to weights
            (must sum to 1.0)

    Returns:
        Weighted average score
    """
    if not scores:
        return 0.0

    if weights is None:
        # Default equal weights
        weights = {k: 1.0 / len(scores) for k in scores}

    weighted_sum = 0.0
    total_weight = 0.0

    for metric, score in scores.items():
        if metric in weights:
            weighted_sum += score * weights[metric]
            total_weight += weights[metric]

    if total_weight == 0:
        return sum(scores.values()) / len(scores)

    return weighted_sum / total_weight


def compute_cognitive_profile(
    state: EnvironmentState,
    final_answer: str,
    hidden_rule: str = "",
    verify_fn: callable = None,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    """
    Compute full cognitive profile from exploration episode.

    Args:
        state: Final environment state
        final_answer: Model's submitted answer
        hidden_rule: Expected answer for correctness
        verify_fn: Optional custom verification function
        weights: Scoring weights

    Returns:
        Dictionary with all metric scores and final_score
    """
    # Compute individual metrics
    correctness = compute_correctness(final_answer, hidden_rule, verify_fn)

    profile = {
        "correctness": correctness,
        "efficiency": compute_efficiency(state),
        "evidence_quality": compute_evidence_quality(state),
        "calibration": compute_calibration(state, bool(correctness)),
        "recovery": compute_recovery(state)
    }

    # Compute weighted final score
    profile["final_score"] = compute_weighted_score(profile, weights)

    return profile
