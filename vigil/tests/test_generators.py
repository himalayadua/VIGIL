"""
Unit tests for ProceduralGenerator.

Tests:
- All four graph families produce valid CognitiveGraph instances
- size_factor controls node count within difficulty bounds
- Hidden rule is embedded and NOT accessible via get_agent_view()
- init_visibility is called (start node is EXPANDED)
- Graphs have edges (not degenerate)
- Node IDs are strings (randomised ordering applied)

Requirements: 9.1, 9.6, 9.8
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from vigil.graphs.core import CognitiveGraph, NodeVisibility
from vigil.graphs.generators import GraphFamily, ProceduralGenerator

GEN = ProceduralGenerator()

BASE_CONFIG = {
    "num_nodes": 12,
    "num_categories": 3,
    "features_per_node": 4,
    "core_features_per_category": 2,
}

RULE_CONFIG = {"type": "category_by_core_features"}


def _make(family: GraphFamily, seed: int = 42, size_factor: float = 1.0) -> CognitiveGraph:
    return GEN.generate(family, seed, size_factor, BASE_CONFIG, RULE_CONFIG)


# ---------------------------------------------------------------------------
# All four families produce valid graphs
# ---------------------------------------------------------------------------

class TestAllFamilies:
    @pytest.mark.parametrize("family", list(GraphFamily))
    def test_produces_cognitive_graph(self, family):
        g = _make(family)
        assert isinstance(g, CognitiveGraph)

    @pytest.mark.parametrize("family", list(GraphFamily))
    def test_has_nodes(self, family):
        g = _make(family)
        assert len(g.nodes) > 0

    @pytest.mark.parametrize("family", list(GraphFamily))
    def test_has_edges(self, family):
        g = _make(family)
        total_edges = sum(len(v) for v in g.edges.values())
        assert total_edges > 0, f"{family} produced a graph with no edges"

    @pytest.mark.parametrize("family", list(GraphFamily))
    def test_node_ids_are_strings(self, family):
        g = _make(family)
        for node_id in g.nodes:
            assert isinstance(node_id, str)

    @pytest.mark.parametrize("family", list(GraphFamily))
    def test_visibility_initialised(self, family):
        """init_visibility must be called — exactly one node is EXPANDED."""
        g = _make(family)
        expanded = [
            nid for nid in g.nodes
            if g.get_visibility(nid) == NodeVisibility.EXPANDED
        ]
        assert len(expanded) == 1, (
            f"{family}: expected exactly 1 EXPANDED node, got {len(expanded)}"
        )

    @pytest.mark.parametrize("family", list(GraphFamily))
    def test_start_node_in_metadata(self, family):
        g = _make(family)
        assert "start_node" in g.metadata
        assert g.metadata["start_node"] in g.nodes


# ---------------------------------------------------------------------------
# size_factor controls node count
# ---------------------------------------------------------------------------

class TestSizeFactor:
    def test_size_factor_one_gives_base_count(self):
        g = _make(GraphFamily.ERDOS_RENYI, size_factor=1.0)
        # Allow ±1 for rounding
        assert abs(len(g.nodes) - BASE_CONFIG["num_nodes"]) <= 1

    def test_size_factor_two_doubles_nodes(self):
        g = _make(GraphFamily.ERDOS_RENYI, size_factor=2.0)
        assert len(g.nodes) >= BASE_CONFIG["num_nodes"] * 1.5

    def test_size_factor_half_halves_nodes(self):
        g = _make(GraphFamily.ERDOS_RENYI, size_factor=0.5)
        assert len(g.nodes) <= BASE_CONFIG["num_nodes"]

    def test_minimum_node_count_is_three(self):
        """Even with tiny size_factor, graph must have at least 3 nodes."""
        g = _make(GraphFamily.ERDOS_RENYI, size_factor=0.01)
        assert len(g.nodes) >= 3


# ---------------------------------------------------------------------------
# Hidden rule is embedded but NOT accessible via get_agent_view()
# ---------------------------------------------------------------------------

class TestHiddenRule:
    def test_hidden_rule_stored_in_graph(self):
        g = _make(GraphFamily.STOCHASTIC_BLOCK)
        assert g.hidden_rule is not None
        assert len(g.hidden_rule) > 0

    def test_category_not_in_agent_view(self):
        """Req 9.8: hidden rule must not be accessible via Action API."""
        g = _make(GraphFamily.STOCHASTIC_BLOCK)
        view = g.get_agent_view()
        for node_data in view["expanded"].values():
            assert "category" not in node_data
        for node_data in view["discovered"].values():
            assert "category" not in node_data

    def test_hidden_rule_not_in_features(self):
        """Category labels must not appear in visible node features."""
        g = _make(GraphFamily.STOCHASTIC_BLOCK)
        category_labels = {n.category for n in g.nodes.values()}
        view = g.get_agent_view()
        for node_data in view["expanded"].values():
            for feature in node_data.get("features", []):
                assert feature not in category_labels, (
                    f"Category label '{feature}' leaked into visible features"
                )

    def test_no_rule_config_gives_no_hidden_rule(self):
        g = GEN.generate(GraphFamily.ERDOS_RENYI, 42, 1.0, BASE_CONFIG, rule_config=None)
        assert g.hidden_rule is None

    def test_category_core_features_in_metadata(self):
        """category_core_features stored in metadata for scoring use."""
        g = _make(GraphFamily.STOCHASTIC_BLOCK)
        assert "category_core_features" in g.metadata
        assert isinstance(g.metadata["category_core_features"], dict)


# ---------------------------------------------------------------------------
# Determinism — same seed → same graph
# ---------------------------------------------------------------------------

class TestDeterminism:
    @pytest.mark.parametrize("family", list(GraphFamily))
    def test_same_seed_same_node_ids(self, family):
        g1 = _make(family, seed=7)
        g2 = _make(family, seed=7)
        assert set(g1.nodes.keys()) == set(g2.nodes.keys())

    @pytest.mark.parametrize("family", list(GraphFamily))
    def test_same_seed_same_features(self, family):
        g1 = _make(family, seed=7)
        g2 = _make(family, seed=7)
        for nid in g1.nodes:
            assert g1.nodes[nid].features == g2.nodes[nid].features

    @pytest.mark.parametrize("family", list(GraphFamily))
    def test_same_seed_same_categories(self, family):
        g1 = _make(family, seed=7)
        g2 = _make(family, seed=7)
        for nid in g1.nodes:
            assert g1.nodes[nid].category == g2.nodes[nid].category

    @pytest.mark.parametrize("family", list(GraphFamily))
    def test_same_seed_same_hidden_rule(self, family):
        g1 = _make(family, seed=7)
        g2 = _make(family, seed=7)
        assert g1.hidden_rule == g2.hidden_rule


# ---------------------------------------------------------------------------
# Diversity — different seeds → different graphs
# ---------------------------------------------------------------------------

class TestDiversity:
    @pytest.mark.parametrize("family", list(GraphFamily))
    def test_different_seeds_different_node_assignments(self, family):
        """Different seeds should produce different feature/category assignments."""
        graphs = [_make(family, seed=s) for s in range(5)]
        # Collect (node_id, category) pairs as a fingerprint per graph
        fingerprints = [
            frozenset((nid, n.category) for nid, n in g.nodes.items())
            for g in graphs
        ]
        assert len(set(fingerprints)) > 1, (
            f"{family}: all 5 seeds produced identical node→category assignments"
        )

    def test_different_seeds_different_features(self):
        """Feature assignments should vary across seeds."""
        graphs = [_make(GraphFamily.ERDOS_RENYI, seed=s) for s in range(5)]
        all_feature_sets = [
            frozenset(frozenset(n.features) for n in g.nodes.values())
            for g in graphs
        ]
        assert len(set(all_feature_sets)) > 1, (
            "All 5 seeds produced identical feature assignments"
        )
