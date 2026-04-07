"""
Unit tests for vigil/scenarios/runtime_spec.py

Tests:
- RuntimeConfig validation
- EvaluationConditions validation
- RuntimeNode / RuntimeEdge validation
- RuntimeScenarioSpec.apply_seed_perturbation()
- RuntimeScenarioSpec.to_scenario_config_dict()

Requirements: 3, 5, 20, 21
"""

import pytest

from vigil.scenarios.runtime_spec import (
    EvaluationConditions,
    RuntimeConfig,
    RuntimeEdge,
    RuntimeNode,
    RuntimeScenarioSpec,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_nodes(n: int = 4) -> list:
    return [
        RuntimeNode(
            node_id=f"n{i}",
            label=f"Node {i}",
            summary_text=f"Summary {i}",
            inspection_detail=f"Detail {i}",
        )
        for i in range(n)
    ]


def _make_edges(nodes: list) -> list:
    edges = []
    for i in range(len(nodes) - 1):
        edges.append(RuntimeEdge(
            from_id=nodes[i].node_id,
            to_id=nodes[i + 1].node_id,
            relation="leads_to",
            traversal_cost=1,
        ))
    return edges


def _make_spec(nodes=None, edges=None) -> RuntimeScenarioSpec:
    if nodes is None:
        nodes = _make_nodes()
    if edges is None:
        edges = _make_edges(nodes)
    return RuntimeScenarioSpec(
        scenario_id="test_scenario",
        cognitive_track="learning",
        opening_prompt="You are investigating an anomaly.",
        nodes=nodes,
        edges=edges,
        entry_node_ids=["n0"],
        answer_targets={"correct_root_cause": "ROOT_CAUSE_X"},
        evidence_targets=["n1", "n2"],
        optimal_path=["n0", "n1", "n2", "n3"],
        optimal_steps=3,
        runtime_config=RuntimeConfig(action_budget=16),
        scoring_weights={"correctness": 0.3, "path_efficiency": 0.4, "evidence_coverage": 0.3},
    )


# ---------------------------------------------------------------------------
# RuntimeConfig
# ---------------------------------------------------------------------------

class TestRuntimeConfig:
    def test_defaults(self):
        rc = RuntimeConfig(action_budget=10)
        assert rc.action_budget == 10
        assert rc.turn_cap == 20
        assert rc.action_costs["inspect"] == 1
        assert rc.action_costs["ask_for_help"] == 1
        assert rc.action_costs["communication"] == 1

    def test_custom_costs(self):
        rc = RuntimeConfig(action_budget=20, action_costs={"inspect": 2})
        assert rc.action_costs["inspect"] == 2

    def test_turn_cap_exceeds_20_raises(self):
        with pytest.raises(ValueError, match="turn_cap"):
            RuntimeConfig(action_budget=10, turn_cap=21)

    def test_zero_budget_raises(self):
        with pytest.raises(ValueError, match="action_budget"):
            RuntimeConfig(action_budget=0)

    def test_negative_budget_raises(self):
        with pytest.raises(ValueError, match="action_budget"):
            RuntimeConfig(action_budget=-5)


# ---------------------------------------------------------------------------
# EvaluationConditions
# ---------------------------------------------------------------------------

class TestEvaluationConditions:
    def test_defaults(self):
        ec = EvaluationConditions()
        assert ec.allowed_tools == []
        assert ec.tool_policy == "none"
        assert ec.response_format == "structured_json"
        assert ec.interface_mode == "graph_traversal"
        assert ec.external_knowledge_policy == "none"

    def test_valid_tool_policies(self):
        for policy in ("none", "calculator_only", "search_allowed"):
            ec = EvaluationConditions(tool_policy=policy)
            assert ec.tool_policy == policy

    def test_invalid_tool_policy_raises(self):
        with pytest.raises(ValueError, match="tool_policy"):
            EvaluationConditions(tool_policy="unrestricted")

    def test_invalid_knowledge_policy_raises(self):
        with pytest.raises(ValueError, match="external_knowledge_policy"):
            EvaluationConditions(external_knowledge_policy="anything_goes")

    def test_allowed_tools_list(self):
        ec = EvaluationConditions(
            allowed_tools=["calculator"],
            tool_policy="calculator_only",
        )
        assert "calculator" in ec.allowed_tools


# ---------------------------------------------------------------------------
# RuntimeNode
# ---------------------------------------------------------------------------

class TestRuntimeNode:
    def test_defaults(self):
        n = RuntimeNode(
            node_id="n0",
            label="Entry",
            summary_text="Brief",
            inspection_detail="Full detail",
        )
        assert n.node_type == "standard"
        assert n.initial_visibility == "hidden"
        assert n.metadata == {}

    def test_valid_visibility_values(self):
        for vis in ("visible", "initial", "hidden"):
            n = RuntimeNode("n0", "L", "S", "D", initial_visibility=vis)
            assert n.initial_visibility == vis

    def test_invalid_visibility_raises(self):
        with pytest.raises(ValueError, match="initial_visibility"):
            RuntimeNode("n0", "L", "S", "D", initial_visibility="expanded")

    def test_metadata_stored(self):
        n = RuntimeNode("n0", "L", "S", "D", metadata={"attention_role": "distractor"})
        assert n.metadata["attention_role"] == "distractor"


# ---------------------------------------------------------------------------
# RuntimeEdge
# ---------------------------------------------------------------------------

class TestRuntimeEdge:
    def test_defaults(self):
        e = RuntimeEdge(from_id="n0", to_id="n1", relation="leads_to")
        assert e.traversal_cost == 1
        assert e.reveal_text == ""
        assert e.metadata == {}

    def test_custom_traversal_cost(self):
        e = RuntimeEdge("n0", "n1", "leads_to", traversal_cost=2)
        assert e.traversal_cost == 2

    def test_negative_traversal_cost_raises(self):
        with pytest.raises(ValueError, match="traversal_cost"):
            RuntimeEdge("n0", "n1", "leads_to", traversal_cost=-1)

    def test_zero_cost_allowed(self):
        e = RuntimeEdge("n0", "n1", "leads_to", traversal_cost=0)
        assert e.traversal_cost == 0


# ---------------------------------------------------------------------------
# RuntimeScenarioSpec.apply_seed_perturbation
# ---------------------------------------------------------------------------

class TestApplySeedPerturbation:
    def test_seed_zero_returns_same_spec(self):
        spec = _make_spec()
        result = spec.apply_seed_perturbation(0)
        assert result is spec

    def test_seed_nonzero_returns_new_spec(self):
        spec = _make_spec()
        result = spec.apply_seed_perturbation(1)
        assert result is not spec

    def test_node_ids_are_remapped_consistently(self):
        spec = _make_spec()
        result = spec.apply_seed_perturbation(1)
        # All original node IDs must still appear (just remapped)
        original_ids = {n.node_id for n in spec.nodes}
        result_ids = {n.node_id for n in result.nodes}
        assert original_ids == result_ids

    def test_edge_endpoints_use_remapped_ids(self):
        spec = _make_spec()
        result = spec.apply_seed_perturbation(1)
        result_node_ids = {n.node_id for n in result.nodes}
        for edge in result.edges:
            assert edge.from_id in result_node_ids
            assert edge.to_id in result_node_ids

    def test_answer_targets_preserved(self):
        spec = _make_spec()
        result = spec.apply_seed_perturbation(2)
        assert result.answer_targets == spec.answer_targets

    def test_evidence_targets_remapped_to_valid_ids(self):
        spec = _make_spec()
        result = spec.apply_seed_perturbation(1)
        result_node_ids = {n.node_id for n in result.nodes}
        for nid in result.evidence_targets:
            assert nid in result_node_ids

    def test_optimal_path_remapped_to_valid_ids(self):
        spec = _make_spec()
        result = spec.apply_seed_perturbation(1)
        result_node_ids = {n.node_id for n in result.nodes}
        for nid in result.optimal_path:
            assert nid in result_node_ids

    def test_optimal_steps_unchanged(self):
        spec = _make_spec()
        result = spec.apply_seed_perturbation(3)
        assert result.optimal_steps == spec.optimal_steps

    def test_evaluation_conditions_preserved(self):
        spec = _make_spec()
        result = spec.apply_seed_perturbation(1)
        assert result.evaluation_conditions is spec.evaluation_conditions

    def test_deterministic_same_seed(self):
        spec = _make_spec()
        r1 = spec.apply_seed_perturbation(42)
        r2 = spec.apply_seed_perturbation(42)
        assert [n.node_id for n in r1.nodes] == [n.node_id for n in r2.nodes]
        assert [e.from_id for e in r1.edges] == [e.from_id for e in r2.edges]

    def test_different_seeds_produce_different_orderings(self):
        spec = _make_spec(_make_nodes(8))
        r1 = spec.apply_seed_perturbation(1)
        r2 = spec.apply_seed_perturbation(2)
        # With 8 nodes, two different seeds should almost certainly differ
        ids1 = [n.node_id for n in r1.nodes]
        ids2 = [n.node_id for n in r2.nodes]
        assert ids1 != ids2, "Different seeds should produce different orderings"

    def test_scoring_weights_preserved(self):
        spec = _make_spec()
        result = spec.apply_seed_perturbation(1)
        assert result.scoring_weights == spec.scoring_weights

    def test_runtime_config_preserved(self):
        spec = _make_spec()
        result = spec.apply_seed_perturbation(1)
        assert result.runtime_config is spec.runtime_config


# ---------------------------------------------------------------------------
# RuntimeScenarioSpec.to_scenario_config_dict
# ---------------------------------------------------------------------------

class TestToScenarioConfigDict:
    def test_returns_dict(self):
        spec = _make_spec()
        d = spec.to_scenario_config_dict()
        assert isinstance(d, dict)

    def test_contains_optimal_steps(self):
        spec = _make_spec()
        d = spec.to_scenario_config_dict()
        assert d["optimal_steps"] == spec.optimal_steps

    def test_contains_cognitive_track(self):
        spec = _make_spec()
        d = spec.to_scenario_config_dict()
        assert d["cognitive_track"] == "learning"

    def test_contains_process_weights(self):
        spec = _make_spec()
        d = spec.to_scenario_config_dict()
        # VISScorer expects "process_weights" key
        assert "process_weights" in d
        assert d["process_weights"] == spec.scoring_weights

    def test_vis_scorer_compatible(self):
        """to_scenario_config_dict() must be passable to VISScorer.score_episode()."""
        from vigil.scoring.vis import VISScorer
        from vigil.environments.base import EnvironmentState

        spec = _make_spec()
        config = spec.to_scenario_config_dict()
        state = EnvironmentState(current_node="n0")

        scorer = VISScorer()
        result = scorer.score_episode(
            state=state,
            final_answer="ROOT_CAUSE_X",
            justification="Based on n1 and n2.",
            scenario_config=config,
            outcome_score=0.8,
        )
        assert "vis" in result
        assert 0.0 <= result["vis"] <= 1.0
