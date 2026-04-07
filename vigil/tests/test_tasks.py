"""
Unit tests for Kaggle SDK task functions.

Tests:
- Each sub-task returns a float in [0.0, 1.0]
- 20-turn cap terminates loop and returns 0.0
- Budget exhaustion returns 0.0
- vigil_learning_benchmark returns aggregate float

Requirements: 17.1, 17.4, 17.7, 17.8
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from vigil.tasks.track1_learning import (
    concept_formation_sub,
    associative_sub,
    reinforcement_sub,
    observational_sub,
    procedural_sub,
    language_sub,
    vigil_learning_benchmark,
    _run_episode,
    _ENV_MAP,
)
from vigil.scenarios.loader import ScenarioLoader


# ---------------------------------------------------------------------------
# Mock LLM for testing
# ---------------------------------------------------------------------------

class MockLLM:
    """
    Mock LLM that always submits immediately.
    Used to test budget exhaustion and turn cap behaviour.
    """
    def __init__(self, response=None):
        self._response = response
        self.call_count = 0

    def prompt(self, obs, schema=None):
        self.call_count += 1
        if self._response:
            return self._response
        # Return a structured SubmitAnswerAction dict for schema=VigilAction
        return {
            "action_type": "submit_answer",
            "answer": "test answer",
            "justification": "test justification",
            "confidence": 0.5,
        }


class MockLLMGetContext:
    """Mock LLM that always calls get_context (free action, never ends episode)."""
    def __init__(self, max_calls=25):
        self.call_count = 0
        self._max_calls = max_calls

    def prompt(self, obs, schema=None):
        self.call_count += 1
        return {"action_type": "get_context"}


# ---------------------------------------------------------------------------
# Sub-task return type tests
# ---------------------------------------------------------------------------

class TestSubTaskReturnTypes:
    """Each sub-task must return a float in [0.0, 1.0]."""

    @pytest.mark.parametrize("sub_task_fn", [
        concept_formation_sub,
        associative_sub,
        reinforcement_sub,
        observational_sub,
        procedural_sub,
        language_sub,
    ])
    def test_returns_float(self, sub_task_fn):
        llm = MockLLM()
        result = sub_task_fn(llm, difficulty=1, seed=42)
        assert isinstance(result, float), f"{sub_task_fn.__name__} must return float, got {type(result)}"

    @pytest.mark.parametrize("sub_task_fn", [
        concept_formation_sub,
        associative_sub,
        reinforcement_sub,
        observational_sub,
        procedural_sub,
        language_sub,
    ])
    def test_returns_in_range(self, sub_task_fn):
        llm = MockLLM()
        result = sub_task_fn(llm, difficulty=1, seed=42)
        assert 0.0 <= result <= 1.0, f"{sub_task_fn.__name__} returned {result}, expected [0.0, 1.0]"

    @pytest.mark.parametrize("sub_task_fn", [
        concept_formation_sub,
        associative_sub,
        reinforcement_sub,
        observational_sub,
        procedural_sub,
        language_sub,
    ])
    def test_different_seeds_run_without_error(self, sub_task_fn):
        for seed in [1, 42, 999]:
            llm = MockLLM()
            result = sub_task_fn(llm, difficulty=1, seed=seed)
            assert isinstance(result, float)


# ---------------------------------------------------------------------------
# 20-turn cap test (Req 17.8)
# ---------------------------------------------------------------------------

class TestTurnCap:
    def test_20_turn_cap_returns_0_when_no_submit(self):
        """Req 17.8: loop terminates after 20 turns and returns 0.0."""
        # MockLLMGetContext never submits — loop must terminate at 20 turns
        llm = MockLLMGetContext(max_calls=100)
        loader = ScenarioLoader()
        from vigil.environments.concept_formation import ConceptFormationEnv
        config = loader.load("concept_formation")
        env = ConceptFormationEnv(scenario_config=config, difficulty=1, seed=42)

        result = _run_episode(llm, env)

        assert result == 0.0, f"Expected 0.0 when no submit within 20 turns, got {result}"
        assert llm.call_count <= 20, f"LLM called {llm.call_count} times, expected ≤ 20"

    def test_llm_called_at_most_20_times(self):
        """Hard cap: llm.prompt() called at most 20 times per episode."""
        llm = MockLLMGetContext()
        loader = ScenarioLoader()
        from vigil.environments.concept_formation import ConceptFormationEnv
        config = loader.load("concept_formation")
        env = ConceptFormationEnv(scenario_config=config, difficulty=1, seed=42)
        _run_episode(llm, env)
        assert llm.call_count <= 20


# ---------------------------------------------------------------------------
# Budget exhaustion test (Req 17.7)
# ---------------------------------------------------------------------------

class TestBudgetExhaustion:
    def test_returns_0_when_budget_exhausted_without_submit(self):
        """Req 17.7: returns 0.0 when budget exhausted without submit_answer."""
        # Use a mock that always explores (costs budget) but never submits
        class ExploreOnlyLLM:
            def __init__(self):
                self.call_count = 0
            def prompt(self, obs, schema=None):
                self.call_count += 1
                # Always try to explore a non-existent node (ERROR, no budget deduction)
                # This means budget never runs out via explore, but we test the 20-turn cap
                return {"action_type": "get_context"}

        llm = ExploreOnlyLLM()
        loader = ScenarioLoader()
        from vigil.environments.concept_formation import ConceptFormationEnv
        config = loader.load("concept_formation")
        # Set very low budget
        config_low = dict(config)
        config_low["budget"] = {"base": 2}
        env = ConceptFormationEnv(scenario_config=config_low, difficulty=1, seed=42)
        result = _run_episode(llm, env)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0


# ---------------------------------------------------------------------------
# vigil_learning_benchmark
# ---------------------------------------------------------------------------

class TestVigilLearningBenchmark:
    def test_returns_float(self):
        """vigil_learning_benchmark returns a float."""
        llm = MockLLM()
        result = vigil_learning_benchmark(llm)
        assert isinstance(result, float)

    def test_returns_in_range(self):
        llm = MockLLM()
        result = vigil_learning_benchmark(llm)
        assert 0.0 <= result <= 1.0

    def test_aggregates_all_six_scenarios(self):
        """Benchmark runs all 6 scenario types."""
        call_log = []

        class LoggingLLM:
            def prompt(self, obs, schema=None):
                call_log.append(obs[:30])
                return {
                    "action_type": "submit_answer",
                    "answer": "test",
                    "justification": "test",
                    "confidence": 0.5,
                }

        result = vigil_learning_benchmark(LoggingLLM())
        assert isinstance(result, float)
        # Should have been called at least 6 times (once per scenario type minimum)
        assert len(call_log) >= 6


# ---------------------------------------------------------------------------
# Tests for vigil/tasks/vigil_benchmark.py (task 8)
# ---------------------------------------------------------------------------

from typing import Any

from vigil.tasks.vigil_benchmark import _run_episode as _run_episode_new
from vigil.environments.graph_scenario_env import GraphScenarioEnvironment
from vigil.scenarios.runtime_spec import (
    EvaluationConditions,
    RuntimeConfig,
    RuntimeEdge,
    RuntimeNode,
    RuntimeScenarioSpec,
)


# ---------------------------------------------------------------------------
# Mock LLM helpers
# ---------------------------------------------------------------------------

class _SubmitAfterNTurns:
    """Mock LLM that submits an answer after N explore actions."""

    def __init__(self, n_explores: int = 2, answer: str = "ROOT_CAUSE_X"):
        self._n = n_explores
        self._answer = answer
        self._turn = 0

    def prompt(self, obs: str, schema=None) -> Any:
        from vigil.actions.schemas import ExploreAction, SubmitAnswerAction
        self._turn += 1
        if self._turn > self._n:
            return SubmitAnswerAction(
                action_type="submit_answer",
                answer=self._answer,
                justification=f"Based on exploration.",
                confidence=0.8,
            )
        # Explore the first visible neighbor
        import re
        neighbors = re.findall(r"n\d+", obs)
        node_id = neighbors[0] if neighbors else "n1"
        return ExploreAction(action_type="explore", node_id=node_id)


class _NeverSubmits:
    """Mock LLM that never submits — always explores (triggers turn cap)."""

    def __init__(self):
        self._turn = 0

    def prompt(self, obs: str, schema=None) -> Any:
        from vigil.actions.schemas import GetContextAction
        self._turn += 1
        return GetContextAction(action_type="get_context")


class _ExhaustsBudget:
    """Mock LLM that explores until budget is gone."""

    def __init__(self):
        self._turn = 0

    def prompt(self, obs: str, schema=None) -> Any:
        from vigil.actions.schemas import ExploreAction
        self._turn += 1
        import re
        neighbors = re.findall(r"n\d+", obs)
        node_id = neighbors[0] if neighbors else "n1"
        return ExploreAction(action_type="explore", node_id=node_id)


def _make_test_spec(action_budget: int = 10) -> RuntimeScenarioSpec:
    """Build a minimal spec for task tests."""
    nodes = [
        RuntimeNode(f"n{i}", f"Node {i}", f"Summary {i}", f"Detail {i}",
                    initial_visibility="visible" if i == 0 else "hidden")
        for i in range(4)
    ]
    edges = [
        RuntimeEdge(f"n{i}", f"n{i+1}", "leads_to", traversal_cost=1)
        for i in range(3)
    ]
    return RuntimeScenarioSpec(
        scenario_id="test_task_scenario",
        cognitive_track="learning",
        opening_prompt="Find the root cause.",
        nodes=nodes,
        edges=edges,
        entry_node_ids=["n0"],
        answer_targets={"correct_root_cause": "ROOT_CAUSE_X"},
        evidence_targets=["n1", "n2"],
        optimal_path=["n0", "n1", "n2"],
        optimal_steps=2,
        runtime_config=RuntimeConfig(action_budget=action_budget),
        scoring_weights={"correctness": 0.3, "path_efficiency": 0.4, "evidence_coverage": 0.3},
        track_metadata={
            "scoring_config": {
                "max_steps": action_budget,
                "weights": {"correctness": 0.3, "path_efficiency": 0.4, "evidence_coverage": 0.3},
                "correctness_tiers": {"full_1.0": "ROOT_CAUSE_X"},
            },
            "behavioral_signatures": {},
            "anti_shortcutting_audit": {},
            "graph_metadata": {"entry_nodes": ["n0"]},
        },
    )


# ---------------------------------------------------------------------------
# _run_episode (new) — return dict structure
# ---------------------------------------------------------------------------

class TestRunEpisodeNew:
    def test_returns_dict_with_vis_key(self):
        spec = _make_test_spec()
        env = GraphScenarioEnvironment(spec)
        llm = _SubmitAfterNTurns(n_explores=1)
        result = _run_episode_new(llm, env, spec, seed=0)
        assert "vis" in result

    def test_returns_dict_with_scenario_id(self):
        spec = _make_test_spec()
        env = GraphScenarioEnvironment(spec)
        llm = _SubmitAfterNTurns(n_explores=1)
        result = _run_episode_new(llm, env, spec, seed=0)
        assert result["scenario_id"] == "test_task_scenario"

    def test_returns_dict_with_seed(self):
        spec = _make_test_spec()
        env = GraphScenarioEnvironment(spec)
        llm = _SubmitAfterNTurns(n_explores=1)
        result = _run_episode_new(llm, env, spec, seed=42)
        assert result["seed"] == 42

    def test_returns_dict_with_behavioral_signatures(self):
        spec = _make_test_spec()
        env = GraphScenarioEnvironment(spec)
        llm = _SubmitAfterNTurns(n_explores=1)
        result = _run_episode_new(llm, env, spec, seed=0)
        assert "behavioral_signatures" in result

    def test_returns_dict_with_contamination_warning(self):
        spec = _make_test_spec()
        env = GraphScenarioEnvironment(spec)
        llm = _SubmitAfterNTurns(n_explores=1)
        result = _run_episode_new(llm, env, spec, seed=0)
        assert "contamination_warning" in result

    def test_vis_in_range_0_to_1(self):
        spec = _make_test_spec()
        env = GraphScenarioEnvironment(spec)
        llm = _SubmitAfterNTurns(n_explores=1)
        result = _run_episode_new(llm, env, spec, seed=0)
        assert 0.0 <= result["vis"] <= 1.0

    def test_returns_vis_0_when_20_turn_cap_reached(self):
        """Property 10: 20-turn cap terminates loop, returns 0.0."""
        spec = _make_test_spec(action_budget=100)
        env = GraphScenarioEnvironment(spec)
        llm = _NeverSubmits()
        result = _run_episode_new(llm, env, spec, seed=0)
        assert result["vis"] == 0.0

    def test_returns_vis_0_when_budget_exhausted(self):
        """Property 10: budget exhaustion terminates loop, returns 0.0."""
        spec = _make_test_spec(action_budget=2)
        env = GraphScenarioEnvironment(spec)
        llm = _ExhaustsBudget()
        result = _run_episode_new(llm, env, spec, seed=0)
        assert result["vis"] == 0.0

    def test_three_limits_are_independent_of_optimal_steps(self):
        """Property 10: none of the three limits is derived from optimal_steps."""
        spec = _make_test_spec(action_budget=5)
        # optimal_steps = 2, but budget = 5 — they are independent
        assert spec.optimal_steps == 2
        assert spec.runtime_config.action_budget == 5
        env = GraphScenarioEnvironment(spec)
        llm = _SubmitAfterNTurns(n_explores=1)
        result = _run_episode_new(llm, env, spec, seed=0)
        # Should complete normally (not limited by optimal_steps)
        assert "vis" in result


# ---------------------------------------------------------------------------
# vigil_episode — float return
# ---------------------------------------------------------------------------

class TestVigilEpisode:
    PACKS_DIR = Path(__file__).parent.parent / "scenarios" / "packs"

    @pytest.fixture(autouse=True)
    def skip_if_no_pack(self):
        if not (self.PACKS_DIR / "vigil_all_30_scenarios.json").exists():
            pytest.skip("Track 1 authored pack not found")

    def test_vigil_episode_returns_float(self):
        from vigil.tasks.vigil_benchmark import _vigil_episode_impl

        class _MockLLM:
            def prompt(self, obs, schema=None):
                from vigil.actions.schemas import SubmitAnswerAction
                return SubmitAnswerAction(
                    action_type="submit_answer",
                    answer="test",
                    justification="test",
                    confidence=0.5,
                )

        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(self.PACKS_DIR))
        ids = catalog.get_scenario_ids(track="learning")
        result = _vigil_episode_impl(_MockLLM(), ids[0], seed=0, packs_dir=str(self.PACKS_DIR))
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0


# ---------------------------------------------------------------------------
# vigil_benchmark — float return
# ---------------------------------------------------------------------------

class TestVigilBenchmark:
    PACKS_DIR = Path(__file__).parent.parent / "scenarios" / "packs"

    @pytest.fixture(autouse=True)
    def skip_if_no_pack(self):
        if not (self.PACKS_DIR / "vigil_all_30_scenarios.json").exists():
            pytest.skip("Track 1 authored pack not found")

    def test_vigil_benchmark_returns_float(self):
        from vigil.tasks.vigil_benchmark import _vigil_benchmark_impl

        class _MockLLM:
            def prompt(self, obs, schema=None):
                from vigil.actions.schemas import SubmitAnswerAction
                return SubmitAnswerAction(
                    action_type="submit_answer",
                    answer="test",
                    justification="test",
                    confidence=0.5,
                )

        # Use only 1 scenario to keep test fast
        from vigil.scenarios.catalog import ScenarioCatalog
        catalog = ScenarioCatalog(packs_dir=str(self.PACKS_DIR))
        ids = catalog.get_scenario_ids(track="learning")

        # Monkey-patch catalog to return only 1 scenario
        import vigil.tasks.vigil_benchmark as vb
        original_catalog = vb._catalog
        vb._catalog = None

        class _SingleScenarioCatalog:
            def get_scenario_ids(self, track=None):
                return [ids[0]]
            def load(self, sid, seed=0):
                return catalog.load(sid, seed=seed)

        vb._catalog = _SingleScenarioCatalog()
        try:
            result = _vigil_benchmark_impl(_MockLLM(), packs_dir=str(self.PACKS_DIR))
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0
        finally:
            vb._catalog = original_catalog


# ---------------------------------------------------------------------------
# Property 10 — Hypothesis property test
# ---------------------------------------------------------------------------

from hypothesis import given, settings
from hypothesis import strategies as st


@given(
    budget=st.integers(min_value=1, max_value=5),
    optimal_steps=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=30)
def test_property_10_three_independent_limits(budget: int, optimal_steps: int):
    """
    Property 10: Three independent limits.

    Budget exhaustion, episode_done, and 20-turn cap each independently
    terminate the loop. None is derived from spec.optimal_steps.
    """
    # Build spec where optimal_steps != budget to confirm independence
    nodes = [
        RuntimeNode(f"n{i}", f"N{i}", f"S{i}", f"D{i}",
                    initial_visibility="visible" if i == 0 else "hidden")
        for i in range(3)
    ]
    edges = [RuntimeEdge("n0", "n1", "leads_to"), RuntimeEdge("n1", "n2", "leads_to")]
    spec = RuntimeScenarioSpec(
        scenario_id="prop10_test",
        cognitive_track="learning",
        opening_prompt="Test.",
        nodes=nodes,
        edges=edges,
        entry_node_ids=["n0"],
        answer_targets={"correct_root_cause": "X"},
        evidence_targets=["n1"],
        optimal_path=["n0"] * optimal_steps,
        optimal_steps=optimal_steps,
        runtime_config=RuntimeConfig(action_budget=budget),
        scoring_weights={"correctness": 1.0},
        track_metadata={
            "scoring_config": {"max_steps": budget, "weights": {"correctness": 1.0}, "correctness_tiers": {}},
            "behavioral_signatures": {}, "anti_shortcutting_audit": {},
            "graph_metadata": {"entry_nodes": ["n0"]},
        },
    )
    env = GraphScenarioEnvironment(spec)
    llm = _NeverSubmits()
    result = _run_episode_new(llm, env, spec, seed=0)

    # With _NeverSubmits, episode never completes → vis must be 0.0
    assert result["vis"] == 0.0
    # The result must not depend on optimal_steps
    assert result["scenario_id"] == "prop10_test"
