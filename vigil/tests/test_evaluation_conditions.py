"""
Unit tests for EvaluationConditions enforcement.

Tests:
- tool_policy="none" rejects external tool actions with ERROR event, no budget deduction
- run_human_session() enforces same conditions as automated loop
- HumanBaseline stores evaluation_conditions and track_dimensions fields
- Property 15: spec.evaluation_conditions is the same object for AI and human paths

Requirements: 17, 20, Property 15
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from vigil.actions.schemas import (
    ExploreAction,
    GetContextAction,
    InspectAction,
    SubmitAnswerAction,
)
from vigil.environments.base import EventType, EnvironmentState
from vigil.environments.graph_scenario_env import GraphScenarioEnvironment
from vigil.scenarios.runtime_spec import (
    EvaluationConditions,
    RuntimeConfig,
    RuntimeEdge,
    RuntimeNode,
    RuntimeScenarioSpec,
)
from vigil.scoring.profile import HumanBaseline


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_spec(tool_policy: str = "none", allowed_tools=None) -> RuntimeScenarioSpec:
    nodes = [
        RuntimeNode(f"n{i}", f"Node {i}", f"Summary {i}", f"Detail {i}",
                    initial_visibility="visible" if i == 0 else "hidden")
        for i in range(4)
    ]
    edges = [RuntimeEdge(f"n{i}", f"n{i+1}", "leads_to") for i in range(3)]
    return RuntimeScenarioSpec(
        scenario_id="eval_cond_test",
        cognitive_track="learning",
        opening_prompt="Find the root cause.",
        nodes=nodes,
        edges=edges,
        entry_node_ids=["n0"],
        answer_targets={"correct_root_cause": "X"},
        evidence_targets=["n1"],
        optimal_path=["n0", "n1"],
        optimal_steps=1,
        runtime_config=RuntimeConfig(action_budget=20),
        scoring_weights={"correctness": 1.0},
        evaluation_conditions=EvaluationConditions(
            tool_policy=tool_policy,
            allowed_tools=allowed_tools or [],
        ),
        track_metadata={
            "scoring_config": {"max_steps": 20, "weights": {"correctness": 1.0}, "correctness_tiers": {}},
            "behavioral_signatures": {}, "anti_shortcutting_audit": {},
            "graph_metadata": {"entry_nodes": ["n0"]},
        },
    )


# ---------------------------------------------------------------------------
# 15.1 — tool_policy enforcement in execute_action()
# ---------------------------------------------------------------------------

class TestToolPolicyEnforcement:
    def test_tool_policy_none_allows_base_actions(self):
        """Base interface actions must always be allowed under tool_policy='none'."""
        spec = _make_spec(tool_policy="none")
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        # Explore is a base action — must succeed
        state = env.execute_action(state, GetContextAction(action_type="get_context"))
        assert state.action_history[-1].event_type == EventType.GET_CONTEXT

    def test_tool_policy_none_allows_track_specific_actions(self):
        """Track-specific actions (ask_for_help, send_message, make_commitment) are interface actions."""
        from vigil.actions.schemas import AskForHelpAction
        spec = _make_spec(tool_policy="none")
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        # ask_for_help is a track-specific interface action — must not be blocked
        action = AskForHelpAction(
            action_type="ask_for_help",
            question="What next?",
            help_type="clarification",
        )
        state = env.execute_action(state, action)
        # Should not produce an ERROR event for tool_policy violation
        # (may produce ERROR for other reasons like unknown action type)
        last_event = state.action_history[-1]
        if last_event.event_type == EventType.ERROR:
            assert "tool_policy" not in last_event.observation

    def test_unknown_action_type_rejected_with_error_event(self):
        """An action with an unknown action_type should produce an ERROR event."""
        spec = _make_spec(tool_policy="none")
        env = GraphScenarioEnvironment(spec)
        state = env.reset()

        class _FakeExternalTool:
            action_type = "call_external_api"

        budget_before = state.budget_remaining
        state = env.execute_action(state, _FakeExternalTool())
        assert state.action_history[-1].event_type == EventType.ERROR
        # Budget must not be deducted for rejected actions
        assert state.budget_remaining == budget_before

    def test_error_event_no_budget_deduction(self):
        """ERROR events must never deduct budget."""
        from vigil.actions.schemas import ActionParseError
        spec = _make_spec(tool_policy="none")
        env = GraphScenarioEnvironment(spec)
        state = env.reset()
        budget_before = state.budget_remaining
        err = ActionParseError("bad", "parse failed")
        state = env.execute_action(state, err)
        assert state.budget_remaining == budget_before

    def test_tool_policy_none_with_empty_allowed_tools(self):
        """tool_policy='none' with empty allowed_tools is the default strict mode."""
        spec = _make_spec(tool_policy="none", allowed_tools=[])
        assert spec.evaluation_conditions.tool_policy == "none"
        assert spec.evaluation_conditions.allowed_tools == []


# ---------------------------------------------------------------------------
# 15.2 — run_human_session() enforces evaluation_conditions
# ---------------------------------------------------------------------------

class TestRunHumanSessionEnforcement:
    def test_run_human_session_completes_episode(self):
        """run_human_session() must complete an episode using the same loop."""
        spec = _make_spec()
        env = GraphScenarioEnvironment(spec)

        call_count = [0]

        def _input_fn(obs: str):
            call_count[0] += 1
            if call_count[0] >= 2:
                return SubmitAnswerAction(
                    action_type="submit_answer",
                    answer="X",
                    justification="j",
                    confidence=0.8,
                )
            return GetContextAction(action_type="get_context")

        state = env.run_human_session(_input_fn)
        assert state.episode_done

    def test_run_human_session_first_obs_contains_evaluation_conditions(self):
        """First observation must include evaluation_conditions notice."""
        spec = _make_spec(tool_policy="none")
        env = GraphScenarioEnvironment(spec)

        observations = []

        def _input_fn(obs: str):
            observations.append(obs)
            return SubmitAnswerAction(
                action_type="submit_answer",
                answer="X",
                justification="j",
                confidence=0.5,
            )

        env.run_human_session(_input_fn)
        assert len(observations) >= 1
        first_obs = observations[0]
        assert "EVALUATION CONDITIONS" in first_obs
        assert "tool_policy" in first_obs.lower() or "none" in first_obs.lower()

    def test_run_human_session_uses_same_spec_evaluation_conditions(self):
        """Property 15: same evaluation_conditions object used for AI and human paths."""
        spec = _make_spec(tool_policy="none")
        env = GraphScenarioEnvironment(spec)

        # The spec.evaluation_conditions is the same object in both paths
        assert env.spec.evaluation_conditions is spec.evaluation_conditions

    def test_run_human_session_enforces_tool_policy_via_execute_action(self):
        """Human session uses execute_action() which enforces tool_policy."""
        spec = _make_spec(tool_policy="none")
        env = GraphScenarioEnvironment(spec)

        class _FakeExternalTool:
            action_type = "call_external_api"

        def _input_fn(obs: str):
            return _FakeExternalTool()

        # Should not raise — execute_action handles unknown actions gracefully
        state = env.run_human_session(_input_fn)
        # All actions should have produced ERROR events (unknown action type)
        error_events = [
            e for e in state.action_history
            if e.event_type == EventType.ERROR
        ]
        assert len(error_events) > 0


# ---------------------------------------------------------------------------
# 15.3 — HumanBaseline new fields
# ---------------------------------------------------------------------------

class TestHumanBaselineNewFields:
    def test_track_dimensions_defaults_empty(self):
        hb = HumanBaseline(scenario_id="s1")
        assert hb.track_dimensions == {}

    def test_evaluation_conditions_defaults_empty(self):
        hb = HumanBaseline(scenario_id="s1")
        assert hb.evaluation_conditions == {}

    def test_track_dimensions_can_be_set(self):
        hb = HumanBaseline(
            scenario_id="s1",
            track_dimensions={"correctness": 0.7, "evidence_coverage": 0.8},
        )
        assert hb.track_dimensions["correctness"] == 0.7

    def test_evaluation_conditions_can_be_set(self):
        hb = HumanBaseline(
            scenario_id="s1",
            evaluation_conditions={"tool_policy": "none", "allowed_tools": []},
        )
        assert hb.evaluation_conditions["tool_policy"] == "none"

    def test_to_dict_contains_track_dimensions(self):
        hb = HumanBaseline(
            scenario_id="s1",
            track_dimensions={"correctness": 0.7},
        )
        d = hb.to_dict()
        assert "track_dimensions" in d
        assert d["track_dimensions"]["correctness"] == 0.7

    def test_to_dict_contains_evaluation_conditions(self):
        hb = HumanBaseline(
            scenario_id="s1",
            evaluation_conditions={"tool_policy": "none"},
        )
        d = hb.to_dict()
        assert "evaluation_conditions" in d
        assert d["evaluation_conditions"]["tool_policy"] == "none"

    def test_from_dict_restores_track_dimensions(self):
        d = {
            "scenario_id": "s1",
            "participants": [],
            "track_dimensions": {"correctness": 0.8},
            "evaluation_conditions": {},
        }
        hb = HumanBaseline.from_dict(d)
        assert hb.track_dimensions["correctness"] == 0.8

    def test_from_dict_restores_evaluation_conditions(self):
        d = {
            "scenario_id": "s1",
            "participants": [],
            "track_dimensions": {},
            "evaluation_conditions": {"tool_policy": "none"},
        }
        hb = HumanBaseline.from_dict(d)
        assert hb.evaluation_conditions["tool_policy"] == "none"

    def test_roundtrip_preserves_new_fields(self):
        hb = HumanBaseline(
            scenario_id="s1",
            track_dimensions={"correctness": 0.75, "path_efficiency": 0.6},
            evaluation_conditions={"tool_policy": "none", "allowed_tools": []},
        )
        hb2 = HumanBaseline.from_dict(hb.to_dict())
        assert hb2.track_dimensions == hb.track_dimensions
        assert hb2.evaluation_conditions == hb.evaluation_conditions


# ---------------------------------------------------------------------------
# Property 15 — Hypothesis property test
# ---------------------------------------------------------------------------

@given(tool_policy=st.sampled_from(["none", "calculator_only", "search_allowed"]))
@settings(max_examples=30)
def test_property_15_evaluation_conditions_identical_for_ai_and_human(tool_policy: str):
    """
    Property 15: Evaluation conditions are identical for AI and human.

    spec.evaluation_conditions is the same object used by both
    GraphScenarioEnvironment.execute_action() (AI path) and
    run_human_session() (human path).
    """
    spec = _make_spec(tool_policy=tool_policy)
    env = GraphScenarioEnvironment(spec)

    # The environment stores spec, which contains evaluation_conditions
    # Both execute_action() and run_human_session() use env.spec.evaluation_conditions
    assert env.spec.evaluation_conditions is spec.evaluation_conditions
    assert env.spec.evaluation_conditions.tool_policy == tool_policy
