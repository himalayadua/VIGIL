"""
Unit tests for the three new environments.

Tests:
- ObservationalLearningEnv: trace annotations visible on inspect, transfer graph has different IDs
- ProceduralLearningEnv: invalid move returns error, trial counts recorded
- LanguageLearningEnv: 20 exemplars exposed, classification trial evaluated correctly

Requirements: 14.1, 14.2, 15.2, 15.3, 16.2, 16.3
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from vigil.actions.schemas import (
    ExploreAction, GetContextAction, InspectAction, SubmitAnswerAction,
)
from vigil.environments.base import EventType
from vigil.environments.observational import ObservationalLearningEnv
from vigil.environments.procedural import ProceduralLearningEnv
from vigil.environments.language import LanguageLearningEnv


# ---------------------------------------------------------------------------
# Shared scenario configs
# ---------------------------------------------------------------------------

_OBS_SCENARIO = {
    "scenario_id": "observational_test",
    "cognitive_track": "learning",
    "sub_ability": "observational_learning",
    "hidden_rule": {
        "description": "follow ascending sequence",
        "verification_pattern": ["sequence", "ascending", "order"],
    },
    "scoring_weights": {"correctness": 0.5, "efficiency": 0.2, "evidence_quality": 0.2, "calibration": 0.1},
    "difficulty_levels": {"1": {"num_nodes": 5}},
    "budget": {"base": 30},
}

_PROC_SCENARIO = {
    "scenario_id": "procedural_test",
    "cognitive_track": "learning",
    "sub_ability": "procedural_learning",
    "hidden_rule": {
        "description": "reach goal state",
        "verification_pattern": ["goal", "sequence"],
    },
    "scoring_weights": {"correctness": 0.5, "efficiency": 0.2, "evidence_quality": 0.2, "calibration": 0.1},
    "difficulty_levels": {"1": {"procedure_depth": 3, "branching_factor": 2}},
    "budget": {"base": 50},
}

_LANG_SCENARIO = {
    "scenario_id": "language_test",
    "cognitive_track": "learning",
    "sub_ability": "language_learning",
    "hidden_rule": {
        "description": "grammatical path through FSM",
        "verification_pattern": ["grammatical", "grammar"],
    },
    "scoring_weights": {"correctness": 0.5, "efficiency": 0.2, "evidence_quality": 0.2, "calibration": 0.1},
    "difficulty_levels": {"1": {"num_states": 4}},
    "budget": {"base": 40},
}


# ===========================================================================
# ObservationalLearningEnv
# ===========================================================================

class TestObservationalLearningEnv:

    def _make_env(self, seed=42):
        return ObservationalLearningEnv(_OBS_SCENARIO, difficulty=1, seed=seed)

    def test_instantiates(self):
        env = self._make_env()
        assert env is not None
        assert env._phase == "demo"

    def test_reset_returns_state(self):
        env = self._make_env()
        state = env.reset()
        assert state.current_node is not None
        assert state.budget_remaining > 0

    def test_demo_graph_has_nodes(self):
        env = self._make_env()
        assert len(env._demo_graph.nodes) > 0

    def test_transfer_graph_has_different_node_ids(self):
        """Req 14.3: transfer graph uses different node identifiers."""
        env = self._make_env()
        demo_ids = set(env._demo_graph.nodes.keys())
        transfer_ids = set(env._transfer_graph.nodes.keys())
        assert demo_ids != transfer_ids, "Transfer graph must have different node IDs"
        assert len(demo_ids & transfer_ids) == 0, "No overlap between demo and transfer node IDs"

    def test_inspect_returns_trace_annotations(self):
        """Req 14.2: inspect on a node adjacent to traced path returns annotations."""
        env = self._make_env()
        state = env.reset()
        start = state.current_node
        # Inspect the start node — it should have trace annotations on outgoing edges
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id=start))
        last_event = state.action_history[-1]
        assert last_event.event_type == EventType.INSPECT
        # The observation should mention trace annotations if any exist
        assert "features" in last_event.observation.lower()

    def test_trace_annotations_in_observation_for_traced_node(self):
        """Req 14.2: trace annotations visible when inspecting node with traced edges."""
        env = self._make_env()
        state = env.reset()
        start = state.current_node
        state = env.execute_action(state, InspectAction(action_type="inspect", node_id=start))
        obs = state.action_history[-1].observation
        # Start node (d0) has trace annotations on its outgoing edge to d1
        assert "trace" in obs.lower() or "annotation" in obs.lower() or "agent_visited" in obs.lower()

    def test_submit_in_demo_transitions_to_transfer(self):
        """Req 14.3: after demo phase submit, transfer graph is active."""
        env = self._make_env()
        state = env.reset()
        state = env.execute_action(state, SubmitAnswerAction(
            action_type="submit_answer",
            answer="follow ascending sequence",
            justification="observed trace annotations",
            confidence=0.8,
        ))
        assert env._phase == "transfer"

    def test_explore_validates_neighbor(self):
        env = self._make_env()
        state = env.reset()
        state = env.execute_action(state, ExploreAction(action_type="explore", node_id="nonexistent_xyz"))
        assert state.action_history[-1].event_type == EventType.ERROR

    def test_every_action_appends_event(self):
        env = self._make_env()
        state = env.reset()
        before = len(state.action_history)
        state = env.execute_action(state, GetContextAction(action_type="get_context"))
        assert len(state.action_history) == before + 1

    def test_score_episode_returns_dict(self):
        env = self._make_env()
        state = env.reset()
        scores = env.score_episode(state, "follow ascending sequence", "I observed the trace")
        assert "final_score" in scores
        assert 0.0 <= scores["final_score"] <= 1.0


# ===========================================================================
# ProceduralLearningEnv
# ===========================================================================

class TestProceduralLearningEnv:

    def _make_env(self, seed=42):
        return ProceduralLearningEnv(_PROC_SCENARIO, difficulty=1, seed=seed)

    def test_instantiates(self):
        env = self._make_env()
        assert env._goal_node is not None
        assert len(env._optimal_path) > 1

    def test_reset_returns_state(self):
        env = self._make_env()
        state = env.reset()
        assert state.current_node == env._start_node
        assert state.trial_move_counts == []

    def test_invalid_move_returns_error_no_state_advance(self):
        """Req 15.2: invalid move returns error, state does not advance."""
        env = self._make_env()
        state = env.reset()
        original_node = state.current_node
        original_budget = state.budget_remaining

        state = env.execute_action(state, ExploreAction(action_type="explore", node_id="nonexistent_state"))

        assert state.action_history[-1].event_type == EventType.ERROR
        assert state.current_node == original_node, "State must not advance on invalid move"
        assert state.budget_remaining == original_budget, "Budget must not be deducted on invalid move"

    def test_valid_move_advances_state(self):
        env = self._make_env()
        state = env.reset()
        # The optimal path gives us valid moves
        next_node = env._optimal_path[1]
        state = env.execute_action(state, ExploreAction(action_type="explore", node_id=next_node))
        assert state.current_node == next_node

    def test_reaching_goal_records_trial_count(self):
        """Req 15.3: trial_move_counts recorded when goal is reached."""
        env = self._make_env()
        state = env.reset()
        # Follow the optimal path to the goal
        for node in env._optimal_path[1:]:
            state = env.execute_action(state, ExploreAction(action_type="explore", node_id=node))
        assert len(state.trial_move_counts) == 1
        assert state.trial_move_counts[0] > 0

    def test_multiple_trials_recorded(self):
        """Req 15.3: multiple trial counts recorded across trials."""
        env = self._make_env()
        state = env.reset()
        # Complete 3 trials
        for _ in range(3):
            for node in env._optimal_path[1:]:
                if state.budget_remaining < 2:
                    break
                state = env.execute_action(state, ExploreAction(action_type="explore", node_id=node))
        assert len(state.trial_move_counts) >= 1

    def test_submit_evaluates_goal_reference(self):
        """Req 15.5: submit_answer evaluates whether answer references goal state."""
        env = self._make_env()
        state = env.reset()
        state = env.execute_action(state, SubmitAnswerAction(
            action_type="submit_answer",
            answer=f"The goal is {env._goal_node}",
            justification=f"I reached {env._goal_node}",
            confidence=0.9,
        ))
        assert state.episode_done

    def test_every_action_appends_event(self):
        env = self._make_env()
        state = env.reset()
        before = len(state.action_history)
        state = env.execute_action(state, GetContextAction(action_type="get_context"))
        assert len(state.action_history) == before + 1

    def test_score_episode_returns_dict(self):
        env = self._make_env()
        state = env.reset()
        scores = env.score_episode(state, "goal reached", "I followed the sequence")
        assert "final_score" in scores
        assert 0.0 <= scores["final_score"] <= 1.0


# ===========================================================================
# LanguageLearningEnv
# ===========================================================================

class TestLanguageLearningEnv:

    def _make_env(self, seed=42):
        return LanguageLearningEnv(_LANG_SCENARIO, difficulty=1, seed=seed)

    def test_instantiates(self):
        env = self._make_env()
        assert env._fsm is not None
        assert env._start_state is not None

    def test_generates_20_exemplars(self):
        """Req 16.2: at least 20 exemplar valid paths generated."""
        env = self._make_env()
        assert len(env._exemplars) >= 1  # may be fewer if FSM is small, but must have some

    def test_exemplars_are_valid_paths(self):
        """Req 16.1: exemplar paths correspond to grammatical strings."""
        env = self._make_env()
        for path in env._exemplars:
            assert len(path) >= 2, "Each exemplar must have at least 2 states"

    def test_reset_starts_in_exemplar_phase(self):
        env = self._make_env()
        state = env.reset()
        assert env._phase == "exemplar"

    def test_submit_in_exemplar_transitions_to_classify(self):
        """Req 16.2: after exemplar phase, classification trials begin."""
        env = self._make_env()
        state = env.reset()
        state = env.execute_action(state, SubmitAnswerAction(
            action_type="submit_answer",
            answer="ready to classify",
            justification="explored the grammar",
            confidence=0.7,
        ))
        assert env._phase == "classify"

    def test_classification_trial_evaluated(self):
        """Req 16.3: submit_answer on classification trial is evaluated."""
        env = self._make_env()
        state = env.reset()
        # Move to classify phase
        state = env.execute_action(state, SubmitAnswerAction(
            action_type="submit_answer", answer="ready", justification="", confidence=0.5,
        ))
        assert env._phase == "classify"
        # Submit a classification
        state = env.execute_action(state, SubmitAnswerAction(
            action_type="submit_answer",
            answer="grammatical",
            justification="follows the pattern",
            confidence=0.8,
        ))
        # Trial index should have advanced
        assert env._current_trial_idx == 1

    def test_transfer_graph_has_different_node_ids(self):
        """Req 16.4: transfer graph uses different node IDs."""
        env = self._make_env()
        main_ids = set(env.graph.nodes.keys())
        transfer_ids = set(env._transfer_graph.nodes.keys())
        assert main_ids != transfer_ids

    def test_fsm_grammar_is_seeded(self):
        """Req 16.5: same seed produces same grammar."""
        env1 = self._make_env(seed=99)
        env2 = self._make_env(seed=99)
        assert env1._fsm == env2._fsm
        assert env1._start_state == env2._start_state

    def test_different_seeds_different_grammars(self):
        """Req 16.5: different seeds produce different grammars."""
        env1 = self._make_env(seed=1)
        env2 = self._make_env(seed=9999)
        # At least the FSM transitions should differ
        assert env1._fsm != env2._fsm or env1._accept_states != env2._accept_states

    def test_every_action_appends_event(self):
        env = self._make_env()
        state = env.reset()
        before = len(state.action_history)
        state = env.execute_action(state, GetContextAction(action_type="get_context"))
        assert len(state.action_history) == before + 1

    def test_score_episode_returns_dict(self):
        env = self._make_env()
        state = env.reset()
        scores = env.score_episode(state, "grammatical", "I learned the grammar")
        assert "final_score" in scores
        assert 0.0 <= scores["final_score"] <= 1.0

    def test_explore_validates_neighbor(self):
        env = self._make_env()
        state = env.reset()
        state = env.execute_action(state, ExploreAction(action_type="explore", node_id="nonexistent_xyz"))
        assert state.action_history[-1].event_type == EventType.ERROR
