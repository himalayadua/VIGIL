"""
Unit tests for CognitiveGraph visibility system.

Tests:
- init_visibility sets start node to EXPANDED, all others to UNEXPLORED
- set_visibility only upgrades (never downgrades)
- get_agent_view filters correctly per visibility state
- category is NEVER present in get_agent_view output
- UNEXPLORED nodes are completely absent from get_agent_view
- DISCOVERED nodes show only id + edge_types (no features)
- EXPANDED nodes show id + features + edge_types (no category)

Requirements: 1.1, 1.2, 1.5, 1.6, 1.7, 1.9, 5.1
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from vigil.graphs.core import CognitiveGraph, GraphEdge, GraphNode, NodeVisibility


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_graph(num_nodes: int = 5, start: str = "n0") -> CognitiveGraph:
    """Build a simple linear graph n0 → n1 → ... → n(N-1)."""
    g = CognitiveGraph()
    for i in range(num_nodes):
        g.add_node(GraphNode(
            node_id=f"n{i}",
            features={f"feat_{i}_a", f"feat_{i}_b"},
            category=f"cat_{i % 2}",
        ))
    for i in range(num_nodes - 1):
        g.add_edge(f"n{i}", GraphEdge(source=f"n{i}", target=f"n{i+1}", relation_type="next"))
    g.init_visibility(start)
    return g


# ---------------------------------------------------------------------------
# init_visibility
# ---------------------------------------------------------------------------

class TestInitVisibility:
    def test_start_node_is_expanded(self):
        g = _make_graph(start="n0")
        assert g.get_visibility("n0") == NodeVisibility.EXPANDED

    def test_all_other_nodes_are_unexplored(self):
        g = _make_graph(num_nodes=5, start="n0")
        for i in range(1, 5):
            assert g.get_visibility(f"n{i}") == NodeVisibility.UNEXPLORED

    def test_single_node_graph(self):
        g = CognitiveGraph()
        g.add_node(GraphNode(node_id="only", features={"f1"}, category="c"))
        g.init_visibility("only")
        assert g.get_visibility("only") == NodeVisibility.EXPANDED

    def test_unknown_start_node_leaves_all_unexplored(self):
        """If start_node doesn't exist, all nodes stay UNEXPLORED."""
        g = _make_graph(num_nodes=3, start="nonexistent")
        for i in range(3):
            assert g.get_visibility(f"n{i}") == NodeVisibility.UNEXPLORED

    def test_reinit_resets_visibility(self):
        g = _make_graph(num_nodes=3, start="n0")
        g.set_visibility("n1", NodeVisibility.DISCOVERED)
        g.init_visibility("n2")
        assert g.get_visibility("n2") == NodeVisibility.EXPANDED
        # n0 and n1 should be reset to UNEXPLORED
        assert g.get_visibility("n0") == NodeVisibility.UNEXPLORED
        assert g.get_visibility("n1") == NodeVisibility.UNEXPLORED


# ---------------------------------------------------------------------------
# set_visibility — upgrade-only semantics
# ---------------------------------------------------------------------------

class TestSetVisibility:
    def test_upgrade_unexplored_to_discovered(self):
        g = _make_graph(start="n0")
        g.set_visibility("n1", NodeVisibility.DISCOVERED)
        assert g.get_visibility("n1") == NodeVisibility.DISCOVERED

    def test_upgrade_discovered_to_expanded(self):
        g = _make_graph(start="n0")
        g.set_visibility("n1", NodeVisibility.DISCOVERED)
        g.set_visibility("n1", NodeVisibility.EXPANDED)
        assert g.get_visibility("n1") == NodeVisibility.EXPANDED

    def test_upgrade_unexplored_directly_to_expanded(self):
        g = _make_graph(start="n0")
        g.set_visibility("n2", NodeVisibility.EXPANDED)
        assert g.get_visibility("n2") == NodeVisibility.EXPANDED

    def test_cannot_downgrade_expanded_to_discovered(self):
        g = _make_graph(start="n0")
        g.set_visibility("n1", NodeVisibility.EXPANDED)
        g.set_visibility("n1", NodeVisibility.DISCOVERED)  # should be ignored
        assert g.get_visibility("n1") == NodeVisibility.EXPANDED

    def test_cannot_downgrade_expanded_to_unexplored(self):
        g = _make_graph(start="n0")
        g.set_visibility("n1", NodeVisibility.EXPANDED)
        g.set_visibility("n1", NodeVisibility.UNEXPLORED)  # should be ignored
        assert g.get_visibility("n1") == NodeVisibility.EXPANDED

    def test_cannot_downgrade_discovered_to_unexplored(self):
        g = _make_graph(start="n0")
        g.set_visibility("n1", NodeVisibility.DISCOVERED)
        g.set_visibility("n1", NodeVisibility.UNEXPLORED)  # should be ignored
        assert g.get_visibility("n1") == NodeVisibility.DISCOVERED


# ---------------------------------------------------------------------------
# get_agent_view — filtering by visibility state
# ---------------------------------------------------------------------------

class TestGetAgentView:
    def test_unexplored_nodes_absent_from_view(self):
        """Req 1.5, 1.9: UNEXPLORED nodes must not appear at all."""
        g = _make_graph(num_nodes=5, start="n0")
        view = g.get_agent_view()
        all_visible_ids = set(view["expanded"]) | set(view["discovered"])
        for i in range(1, 5):
            assert f"n{i}" not in all_visible_ids

    def test_expanded_node_in_expanded_section(self):
        g = _make_graph(start="n0")
        view = g.get_agent_view()
        assert "n0" in view["expanded"]
        assert "n0" not in view["discovered"]

    def test_discovered_node_in_discovered_section(self):
        g = _make_graph(start="n0")
        g.set_visibility("n1", NodeVisibility.DISCOVERED)
        view = g.get_agent_view()
        assert "n1" in view["discovered"]
        assert "n1" not in view["expanded"]

    def test_expanded_node_has_features(self):
        """Req 1.7: EXPANDED nodes expose features."""
        g = _make_graph(start="n0")
        view = g.get_agent_view()
        assert "features" in view["expanded"]["n0"]
        assert len(view["expanded"]["n0"]["features"]) > 0

    def test_discovered_node_has_no_features(self):
        """Req 1.6: DISCOVERED nodes must NOT expose features."""
        g = _make_graph(start="n0")
        g.set_visibility("n1", NodeVisibility.DISCOVERED)
        view = g.get_agent_view()
        assert "features" not in view["discovered"]["n1"]

    def test_expanded_node_has_edge_types(self):
        g = _make_graph(start="n0")
        view = g.get_agent_view()
        assert "edge_types" in view["expanded"]["n0"]

    def test_discovered_node_has_edge_types(self):
        g = _make_graph(start="n0")
        g.set_visibility("n1", NodeVisibility.DISCOVERED)
        view = g.get_agent_view()
        assert "edge_types" in view["discovered"]["n1"]

    def test_category_never_in_expanded_view(self):
        """Req 1.7, 5.1: category must NEVER appear in agent view."""
        g = _make_graph(start="n0")
        view = g.get_agent_view()
        for node_data in view["expanded"].values():
            assert "category" not in node_data

    def test_category_never_in_discovered_view(self):
        """Req 1.6, 5.1: category must NEVER appear in agent view."""
        g = _make_graph(start="n0")
        g.set_visibility("n1", NodeVisibility.DISCOVERED)
        view = g.get_agent_view()
        for node_data in view["discovered"].values():
            assert "category" not in node_data

    def test_empty_graph_returns_empty_view(self):
        g = CognitiveGraph()
        view = g.get_agent_view()
        assert view == {"expanded": {}, "discovered": {}}

    def test_all_nodes_expanded_all_appear_in_expanded(self):
        g = _make_graph(num_nodes=3, start="n0")
        g.set_visibility("n1", NodeVisibility.EXPANDED)
        g.set_visibility("n2", NodeVisibility.EXPANDED)
        view = g.get_agent_view()
        assert set(view["expanded"].keys()) == {"n0", "n1", "n2"}
        assert view["discovered"] == {}

    def test_mixed_visibility_states(self):
        g = _make_graph(num_nodes=4, start="n0")
        g.set_visibility("n1", NodeVisibility.DISCOVERED)
        g.set_visibility("n2", NodeVisibility.EXPANDED)
        # n3 stays UNEXPLORED
        view = g.get_agent_view()
        assert "n0" in view["expanded"]
        assert "n2" in view["expanded"]
        assert "n1" in view["discovered"]
        assert "n3" not in view["expanded"]
        assert "n3" not in view["discovered"]


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------

class TestSerialization:
    def test_to_dict_includes_visibility(self):
        g = _make_graph(num_nodes=3, start="n0")
        g.set_visibility("n1", NodeVisibility.DISCOVERED)
        d = g.to_dict()
        assert "visibility" in d
        assert d["visibility"]["n0"] == "expanded"
        assert d["visibility"]["n1"] == "discovered"
        assert d["visibility"]["n2"] == "unexplored"

    def test_from_dict_restores_visibility(self):
        g = _make_graph(num_nodes=3, start="n0")
        g.set_visibility("n1", NodeVisibility.DISCOVERED)
        restored = CognitiveGraph.from_dict(g.to_dict())
        assert restored.get_visibility("n0") == NodeVisibility.EXPANDED
        assert restored.get_visibility("n1") == NodeVisibility.DISCOVERED
        assert restored.get_visibility("n2") == NodeVisibility.UNEXPLORED

    def test_category_not_in_agent_view_after_round_trip(self):
        g = _make_graph(num_nodes=2, start="n0")
        restored = CognitiveGraph.from_dict(g.to_dict())
        view = restored.get_agent_view()
        for node_data in view["expanded"].values():
            assert "category" not in node_data
