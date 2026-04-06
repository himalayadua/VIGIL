"""
Property-based tests for TraversalEvent invariants and replay determinism.

Properties tested:
  P7:  Every action appends a TraversalEvent
  P8:  TraversalEvent contains all required fields
  P9:  Replay determinism
  P10: Inspect populates evidence_nodes

Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 6.1
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from hypothesis import given, settings
from hypothesis import strategies as st

from vigil.actions.schemas import (
    ActionParseError,
    ExploreAction,
    GetContextAction,
    InspectAction,
    SubmitAnswerAction,
)
from vigil.environments.base import EventType, TraversalEvent
from vigil.environments.concept_formation import ConceptFormationEnv
from vigil.graphs.core import NodeVisibility

# ---------------------------------------------------------------------------
# Minimal scenario config for testing
# ---------------------------------------------------------------------------

_SCENARIO = {
    "scenario_id": "test_cf",
    "cognitive_track": "learning",
    "sub_ability": "concept_formation",
    "hidden_rule": {
        "type": "category_by_core_features",
        "description": "Nodes share core features",
        "verification_pattern": ["core features", "category"],
    },
    "scoring_weights": {"correctness": 0.5, "efficiency": 0.2, "evidence_quality": 0.2, "calibration": 0.1},
    "difficulty_levels": {
        "1": {"num_nodes": 6, "num_categories": 2, "features_per_node": 3, "core_features_per_category": 2, "feature_pool_size": 20},
    },
    "budget": {"base": 20},
}


def _make_env(seed: int = 42) -> ConceptFormationEnv:
    return ConceptFormationEnv(scenario_config=_SCENARIO, difficulty=1, seed=seed)


def _get_valid_neighbor(env: ConceptFormationEnv, state) -> str | None:
    """Return a neighbor of the current node that is not UNEXPLORED, or None."""
    neighbors = env.graph.get_neighbors(state.current_node)
    return neighbors[0] if neighbors else None


# ---------------------------------------------------------------------------
# Property 7: Every action appends a TraversalEvent
# Feature: vigil-benchmark, Property 7
# ---------------------------------------------------------------------------

@given(seed=st.integers(min_value=0, max_value=99999))
@settings(max_examples=100)
def test_property_7_every_action_appends_event(seed):
    """
    Feature: vigil-benchmark, Property 7: Every action appends a TraversalEvent

    For any action executed (including failed/invalid ones),
    len(state.action_history) increases by exactly 1.

    Validates: Requirements 3.3, 3.6, 8.1, 8.2
    """
    env = _make_env(seed)
    state = env.reset()

    actions_to_test = [
        # Valid get_context (always succeeds, free)
        GetContextAction(action_type="get_context"),
        # Invalid explore (non-existent node) — must still append event
        ExploreAction(action_type="explore", node_id="nonexistent_node_xyz"),
        # Parse error sentinel — must still append event
        ActionParseError(raw="garbage", error="test error"),
    ]

    for action in actions_to_test:
        before = len(state.action_history)
        state = env.execute_action(state, action)
        after = len(state.action_history)
        assert after == before + 1, (
            f"seed={seed}, action={type(action).__name__}: "
            f"expected action_history to grow by 1, got {before} → {after}"
        )


@given(seed=st.integers(min_value=0, max_value=99999))
@settings(max_examples=100)
def test_property_7_valid_explore_appends_event(seed):
    """
    Feature: vigil-benchmark, Property 7 (valid explore path)

    A valid explore action also appends exactly one TraversalEvent.
    """
    env = _make_env(seed)
    state = env.reset()
    neighbor = _get_valid_neighbor(env, state)
    if neighbor is None:
        return  # degenerate graph, skip

    before = len(state.action_history)
    state = env.execute_action(state, ExploreAction(action_type="explore", node_id=neighbor))
    assert len(state.action_history) == before + 1


# ---------------------------------------------------------------------------
# Property 8: TraversalEvent contains all required fields
# Feature: vigil-benchmark, Property 8
# ---------------------------------------------------------------------------

@given(seed=st.integers(min_value=0, max_value=99999))
@settings(max_examples=100)
def test_property_8_traversal_event_has_required_fields(seed):
    """
    Feature: vigil-benchmark, Property 8: TraversalEvent contains all required fields

    Every TraversalEvent must have non-null: timestamp, event_type,
    observation, state_delta.

    Validates: Requirements 3.2
    """
    env = _make_env(seed)
    state = env.reset()

    # Execute a mix of actions
    state = env.execute_action(state, GetContextAction(action_type="get_context"))
    state = env.execute_action(state, ExploreAction(action_type="explore", node_id="bad_node"))
    state = env.execute_action(state, ActionParseError(raw="x", error="e"))

    for event in state.action_history:
        assert event.timestamp is not None, "timestamp must not be None"
        assert event.timestamp > 0, "timestamp must be positive"
        assert isinstance(event.event_type, EventType), "event_type must be EventType"
        assert isinstance(event.observation, str), "observation must be a string"
        assert len(event.observation) > 0, "observation must not be empty"
        assert isinstance(event.state_delta, dict), "state_delta must be a dict"
        assert "budget_delta" in event.state_delta, "state_delta must have budget_delta"
        assert "episode_done" in event.state_delta, "state_delta must have episode_done"


# ---------------------------------------------------------------------------
# Property 9: Replay determinism
# Feature: vigil-benchmark, Property 9
# ---------------------------------------------------------------------------

@given(seed=st.integers(min_value=0, max_value=99999))
@settings(max_examples=50)  # replay is more expensive
def test_property_9_replay_determinism(seed):
    """
    Feature: vigil-benchmark, Property 9: Replay determinism

    Two calls to replay(events, seed) with identical inputs produce
    EnvironmentState objects that are field-for-field identical.

    Validates: Requirements 3.4, 3.5
    """
    env = _make_env(seed)
    state = env.reset()

    # Run a short episode to collect events
    state = env.execute_action(state, GetContextAction(action_type="get_context"))
    neighbor = _get_valid_neighbor(env, state)
    if neighbor:
        state = env.execute_action(state, ExploreAction(action_type="explore", node_id=neighbor))

    events = list(state.action_history)

    # Replay twice with same seed
    env1 = _make_env(seed)
    state1 = env1.replay(events, seed)

    env2 = _make_env(seed)
    state2 = env2.replay(events, seed)

    # States must be identical
    assert state1.current_node == state2.current_node, (
        f"seed={seed}: current_node differs after replay: {state1.current_node} vs {state2.current_node}"
    )
    assert state1.budget_remaining == state2.budget_remaining, (
        f"seed={seed}: budget_remaining differs: {state1.budget_remaining} vs {state2.budget_remaining}"
    )
    assert len(state1.action_history) == len(state2.action_history), (
        f"seed={seed}: action_history length differs: {len(state1.action_history)} vs {len(state2.action_history)}"
    )
    assert state1.visited_nodes == state2.visited_nodes, (
        f"seed={seed}: visited_nodes differ"
    )
    assert state1.evidence_nodes == state2.evidence_nodes, (
        f"seed={seed}: evidence_nodes differ"
    )


# ---------------------------------------------------------------------------
# Property 10: Inspect populates evidence_nodes
# Feature: vigil-benchmark, Property 10
# ---------------------------------------------------------------------------

@given(seed=st.integers(min_value=0, max_value=99999))
@settings(max_examples=100)
def test_property_10_inspect_populates_evidence_nodes(seed):
    """
    Feature: vigil-benchmark, Property 10: Inspect populates evidence_nodes

    After inspect(node_id) on an evidence-relevant node,
    node_id appears in state.evidence_nodes.

    Validates: Requirements 6.1
    """
    env = _make_env(seed)
    state = env.reset()

    # The start node is EXPANDED — inspect it directly
    start = state.current_node
    assert start in env._evidence_relevant, (
        "Start node should be evidence-relevant in ConceptFormationEnv"
    )

    before_evidence = list(state.evidence_nodes)
    state = env.execute_action(state, InspectAction(action_type="inspect", node_id=start))

    # start node must now be in evidence_nodes
    assert start in state.evidence_nodes, (
        f"seed={seed}: inspecting evidence-relevant node '{start}' "
        f"did not add it to evidence_nodes. evidence_nodes={state.evidence_nodes}"
    )

    # evidence_nodes should have grown by exactly 1 (first inspect of this node)
    assert len(state.evidence_nodes) == len(before_evidence) + 1, (
        f"seed={seed}: evidence_nodes should grow by 1 on first inspect, "
        f"got {len(before_evidence)} → {len(state.evidence_nodes)}"
    )


@given(seed=st.integers(min_value=0, max_value=99999))
@settings(max_examples=100)
def test_property_10_inspect_idempotent_for_evidence(seed):
    """
    Feature: vigil-benchmark, Property 10 (idempotence)

    Inspecting the same node twice does not add it to evidence_nodes twice.
    """
    env = _make_env(seed)
    state = env.reset()
    start = state.current_node

    # First inspect
    state = env.execute_action(state, InspectAction(action_type="inspect", node_id=start))
    count_after_first = len(state.evidence_nodes)

    # Second inspect of same node
    state = env.execute_action(state, InspectAction(action_type="inspect", node_id=start))
    count_after_second = len(state.evidence_nodes)

    assert count_after_first == count_after_second, (
        f"seed={seed}: inspecting same node twice added it to evidence_nodes twice"
    )
