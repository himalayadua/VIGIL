"""
Property-based tests for VISScorer.

Properties tested:
  P11: Efficiency metric uses action_history length
  P14: Exploration efficiency formula
  P15: Contamination warning threshold

Requirements: 8.1, 8.3, 10.3, 10.10
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from hypothesis import given, settings
from hypothesis import strategies as st

from vigil.environments.base import EnvironmentState, EventType, TraversalEvent
from vigil.scoring.metrics import compute_efficiency
from vigil.scoring.vis import VISScorer

VIS = VISScorer()

_SCENARIO = {
    "optimal_steps": 6,
    "process_weights": {
        "exploration_efficiency": 1/6,
        "learning_rate": 1/6,
        "adaptivity": 1/6,
        "recovery": 1/6,
        "stopping_quality": 1/6,
        "metacognition": 1/6,
    },
}


def _make_state_with_n_events(n: int) -> EnvironmentState:
    state = EnvironmentState(current_node="n0", budget_remaining=100)
    for i in range(n):
        state.action_history.append(TraversalEvent.make(
            event_type=EventType.EXPLORE,
            observation="test",
            node_id=f"n{i}",
        ))
    return state


# ---------------------------------------------------------------------------
# Property 11: Efficiency metric uses action_history length
# Feature: vigil-benchmark, Property 11
# ---------------------------------------------------------------------------

@given(
    n_actions=st.integers(min_value=0, max_value=50),
    optimal=st.integers(min_value=1, max_value=20),
)
@settings(max_examples=100)
def test_property_11_efficiency_uses_action_history_length(n_actions, optimal):
    """
    Feature: vigil-benchmark, Property 11: Efficiency metric uses action_history length

    compute_efficiency uses len(state.action_history) as the action count.
    Returns 0.0 when len(state.action_history) == 0.

    Validates: Requirements 8.1, 8.3
    """
    state = _make_state_with_n_events(n_actions)

    result = compute_efficiency(state, optimal_path_length=optimal)

    if n_actions == 0:
        assert result == 0.0, (
            f"n_actions=0: expected 0.0, got {result}"
        )
    else:
        expected = optimal / max(n_actions, optimal)
        assert abs(result - min(1.0, expected)) < 1e-9, (
            f"n_actions={n_actions}, optimal={optimal}: "
            f"expected {min(1.0, expected):.4f}, got {result:.4f}"
        )


# ---------------------------------------------------------------------------
# Property 14: Exploration efficiency formula
# Feature: vigil-benchmark, Property 14
# ---------------------------------------------------------------------------

@given(
    n_visited=st.integers(min_value=0, max_value=30),
    n_evidence=st.integers(min_value=0, max_value=30),
)
@settings(max_examples=100)
def test_property_14_exploration_efficiency_formula(n_visited, n_evidence):
    """
    Feature: vigil-benchmark, Property 14: Exploration efficiency formula

    compute_exploration_efficiency(state) equals
    len(evidence_nodes) / len(visited_nodes) when visited_nodes is non-empty,
    and equals 0.0 when visited_nodes is empty.

    Validates: Requirements 10.3
    """
    state = EnvironmentState(current_node="n0", budget_remaining=100)
    state.visited_nodes = [f"v{i}" for i in range(n_visited)]
    state.evidence_nodes = [f"e{i}" for i in range(n_evidence)]

    result = VIS.compute_exploration_efficiency(state)

    if n_visited == 0:
        assert result == 0.0, (
            f"n_visited=0: expected 0.0, got {result}"
        )
    else:
        expected = min(1.0, n_evidence / n_visited)
        assert abs(result - expected) < 1e-9, (
            f"n_visited={n_visited}, n_evidence={n_evidence}: "
            f"expected {expected:.4f}, got {result:.4f}"
        )


# ---------------------------------------------------------------------------
# Property 15: Contamination warning threshold
# Feature: vigil-benchmark, Property 15
# ---------------------------------------------------------------------------

@given(seed=st.integers(min_value=0, max_value=99999))
@settings(max_examples=100)
def test_property_15_contamination_warning_when_cr_above_0_8(seed):
    """
    Feature: vigil-benchmark, Property 15: Contamination warning threshold

    When compute_contamination_risk(state) > 0.8, the dict returned by
    VISScorer.score_episode contains contamination_warning = True.

    Validates: Requirements 10.10
    """
    # Build a state with high contamination risk:
    # immediate submit with no exploration = maximum directness + early submit
    state = EnvironmentState(current_node="n0", budget_remaining=100)
    state.action_history.append(TraversalEvent.make(
        event_type=EventType.SUBMIT_ANSWER,
        observation="submitted immediately",
        episode_done=True,
    ))

    cr = VIS.compute_contamination_risk(state)
    result = VIS.score_episode(state, "answer", "", _SCENARIO, outcome_score=1.0)

    # The property: if CR > 0.8, warning must be True
    if cr > 0.8:
        assert result["contamination_warning"] is True, (
            f"seed={seed}: CR={cr:.3f} > 0.8 but contamination_warning is False"
        )

    # Inverse: if warning is True, CR must be > 0.8
    if result["contamination_warning"]:
        assert result["contamination_risk"] > 0.8, (
            f"seed={seed}: contamination_warning=True but CR={result['contamination_risk']:.3f} <= 0.8"
        )
