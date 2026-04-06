"""
Property-based tests for CognitiveGraph fog-of-war visibility system.

Properties tested:
  P1: Visibility initialisation invariant
  P2: Explore updates visibility
  P3: Agent view excludes unexplored nodes

Each property runs 100 examples via Hypothesis.

Requirements: 1.2, 1.3, 1.5, 1.6, 1.7, 1.9, 5.1
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from vigil.graphs.core import CognitiveGraph, GraphEdge, GraphNode, NodeVisibility


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_graph(num_nodes: int, seed: int) -> tuple[CognitiveGraph, list[str]]:
    """Build a graph with num_nodes nodes and random edges seeded by seed."""
    import random
    rng = random.Random(seed)
    g = CognitiveGraph()
    node_ids = [f"node_{i}" for i in range(num_nodes)]
    for nid in node_ids:
        g.add_node(GraphNode(
            node_id=nid,
            features={f"f_{nid}_0", f"f_{nid}_1"},
            category=f"cat_{rng.randint(0, 2)}",
        ))
    # Add some random edges
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i != j and rng.random() < 0.3:
                g.add_edge(node_ids[i], GraphEdge(
                    source=node_ids[i], target=node_ids[j], relation_type="link"
                ))
    return g, node_ids


# ---------------------------------------------------------------------------
# Property 1: Visibility initialisation invariant
# Feature: vigil-benchmark, Property 1
# ---------------------------------------------------------------------------

@given(
    num_nodes=st.integers(min_value=1, max_value=20),
    seed=st.integers(min_value=0, max_value=99999),
    start_idx=st.integers(min_value=0, max_value=19),
)
@settings(max_examples=100)
def test_property_1_visibility_init(num_nodes, seed, start_idx):
    """
    Feature: vigil-benchmark, Property 1: Visibility initialisation invariant

    For any CognitiveGraph initialised with a given start node,
    every node except the start node has visibility UNEXPLORED,
    and the start node has visibility EXPANDED.

    Validates: Requirements 1.2
    """
    g, node_ids = _build_graph(num_nodes, seed)
    start_node = node_ids[start_idx % num_nodes]
    g.init_visibility(start_node)

    # Start node must be EXPANDED
    assert g.get_visibility(start_node) == NodeVisibility.EXPANDED, (
        f"Start node {start_node} should be EXPANDED after init_visibility"
    )

    # All other nodes must be UNEXPLORED
    for nid in node_ids:
        if nid != start_node:
            assert g.get_visibility(nid) == NodeVisibility.UNEXPLORED, (
                f"Node {nid} should be UNEXPLORED after init_visibility, "
                f"got {g.get_visibility(nid)}"
            )


# ---------------------------------------------------------------------------
# Property 2: Explore updates visibility
# Feature: vigil-benchmark, Property 2
# ---------------------------------------------------------------------------

@given(
    num_nodes=st.integers(min_value=2, max_value=15),
    seed=st.integers(min_value=0, max_value=99999),
)
@settings(max_examples=100)
def test_property_2_explore_updates_visibility(num_nodes, seed):
    """
    Feature: vigil-benchmark, Property 2: Explore updates visibility

    After set_visibility(node_id, EXPANDED) is called on a node,
    that node has visibility EXPANDED.
    After set_visibility(neighbor_id, DISCOVERED) is called on a neighbor,
    that neighbor has visibility at least DISCOVERED.

    This simulates what execute_action(explore) must do:
    - set the explored node to EXPANDED
    - set all its direct neighbors to at least DISCOVERED

    Validates: Requirements 1.3
    """
    g, node_ids = _build_graph(num_nodes, seed)
    g.init_visibility(node_ids[0])

    # Simulate an explore action on node_ids[0]:
    # 1. Set the explored node to EXPANDED (already is, but test the contract)
    g.set_visibility(node_ids[0], NodeVisibility.EXPANDED)
    assert g.get_visibility(node_ids[0]) == NodeVisibility.EXPANDED

    # 2. Set all neighbors to at least DISCOVERED
    neighbors = g.get_neighbors(node_ids[0])
    for neighbor_id in neighbors:
        g.set_visibility(neighbor_id, NodeVisibility.DISCOVERED)

    # Verify: explored node is EXPANDED
    assert g.get_visibility(node_ids[0]) == NodeVisibility.EXPANDED

    # Verify: all neighbors are at least DISCOVERED
    for neighbor_id in neighbors:
        vis = g.get_visibility(neighbor_id)
        assert vis in (NodeVisibility.DISCOVERED, NodeVisibility.EXPANDED), (
            f"Neighbor {neighbor_id} should be at least DISCOVERED after explore, "
            f"got {vis}"
        )


# ---------------------------------------------------------------------------
# Property 3: Agent view excludes unexplored nodes
# Feature: vigil-benchmark, Property 3
# ---------------------------------------------------------------------------

@given(
    num_nodes=st.integers(min_value=1, max_value=20),
    seed=st.integers(min_value=0, max_value=99999),
    num_discovered=st.integers(min_value=0, max_value=10),
    num_expanded=st.integers(min_value=0, max_value=10),
)
@settings(max_examples=100)
def test_property_3_agent_view_excludes_unexplored(
    num_nodes, seed, num_discovered, num_expanded
):
    """
    Feature: vigil-benchmark, Property 3: Agent view excludes unexplored nodes

    get_agent_view() must:
    - Contain no UNEXPLORED node
    - DISCOVERED nodes: only id + edge_types (no features, no category)
    - EXPANDED nodes: id + features + edge_types (no category)

    Validates: Requirements 1.5, 1.6, 1.7, 1.9, 5.1
    """
    import random
    rng = random.Random(seed)

    g, node_ids = _build_graph(num_nodes, seed)
    g.init_visibility(node_ids[0])

    # Randomly promote some nodes
    shuffled = node_ids[1:]
    rng.shuffle(shuffled)
    for nid in shuffled[:num_discovered]:
        g.set_visibility(nid, NodeVisibility.DISCOVERED)
    for nid in shuffled[num_discovered: num_discovered + num_expanded]:
        g.set_visibility(nid, NodeVisibility.EXPANDED)

    view = g.get_agent_view()
    all_visible = set(view["expanded"]) | set(view["discovered"])

    # P3a: No UNEXPLORED node appears in the view
    for nid in node_ids:
        if g.get_visibility(nid) == NodeVisibility.UNEXPLORED:
            assert nid not in all_visible, (
                f"UNEXPLORED node {nid} must not appear in agent view"
            )

    # P3b: DISCOVERED nodes have no features and no category
    for nid, data in view["discovered"].items():
        assert "features" not in data, (
            f"DISCOVERED node {nid} must not expose features"
        )
        assert "category" not in data, (
            f"DISCOVERED node {nid} must not expose category"
        )
        assert "id" in data or nid in data  # id present (as key or field)

    # P3c: EXPANDED nodes have features but no category
    for nid, data in view["expanded"].items():
        assert "features" in data, (
            f"EXPANDED node {nid} must expose features"
        )
        assert "category" not in data, (
            f"EXPANDED node {nid} must NOT expose category"
        )

    # P3d: Every EXPANDED/DISCOVERED node in the view actually has that visibility
    for nid in view["expanded"]:
        assert g.get_visibility(nid) == NodeVisibility.EXPANDED
    for nid in view["discovered"]:
        assert g.get_visibility(nid) == NodeVisibility.DISCOVERED
