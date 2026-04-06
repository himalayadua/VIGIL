"""
Property-based tests for ProceduralGenerator.

Properties tested:
  P12: ProceduralGenerator is deterministic
  P13: Different seeds produce distinct graphs

Requirements: 9.2, 9.3
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from hypothesis import given, settings
from hypothesis import strategies as st

from vigil.graphs.generators import GraphFamily, ProceduralGenerator

GEN = ProceduralGenerator()

BASE_CONFIG = {
    "num_nodes": 10,
    "num_categories": 2,
    "features_per_node": 3,
    "core_features_per_category": 2,
}

_FAMILIES = list(GraphFamily)


# ---------------------------------------------------------------------------
# Property 12: ProceduralGenerator is deterministic
# Feature: vigil-benchmark, Property 12
# ---------------------------------------------------------------------------

@given(
    family=st.sampled_from(_FAMILIES),
    seed=st.integers(min_value=0, max_value=99999),
)
@settings(max_examples=100)
def test_property_12_generator_determinism(family, seed):
    """
    Feature: vigil-benchmark, Property 12: ProceduralGenerator is deterministic

    Two calls with identical (family, seed, difficulty_config) produce
    CognitiveGraph objects with identical node sets, edge sets,
    feature assignments, and hidden rules.

    Validates: Requirements 9.2
    """
    g1 = GEN.generate(family, seed, 1.0, BASE_CONFIG, {"type": "category_by_core_features"})
    g2 = GEN.generate(family, seed, 1.0, BASE_CONFIG, {"type": "category_by_core_features"})

    # Same node IDs
    assert set(g1.nodes.keys()) == set(g2.nodes.keys()), (
        f"family={family}, seed={seed}: node ID sets differ between two calls"
    )

    # Same features per node
    for nid in g1.nodes:
        assert g1.nodes[nid].features == g2.nodes[nid].features, (
            f"family={family}, seed={seed}: features differ for node {nid}"
        )

    # Same categories per node
    for nid in g1.nodes:
        assert g1.nodes[nid].category == g2.nodes[nid].category, (
            f"family={family}, seed={seed}: category differs for node {nid}"
        )

    # Same hidden rule
    assert g1.hidden_rule == g2.hidden_rule, (
        f"family={family}, seed={seed}: hidden_rule differs between two calls"
    )

    # Same edge structure (same neighbor sets)
    for nid in g1.nodes:
        n1 = set(g1.get_neighbors(nid))
        n2 = set(g2.get_neighbors(nid))
        assert n1 == n2, (
            f"family={family}, seed={seed}: neighbors of {nid} differ: {n1} vs {n2}"
        )


# ---------------------------------------------------------------------------
# Property 13: Different seeds produce distinct graphs
# Feature: vigil-benchmark, Property 13
# ---------------------------------------------------------------------------

@given(
    family=st.sampled_from(_FAMILIES),
    seed_a=st.integers(min_value=0, max_value=49999),
    seed_b=st.integers(min_value=50000, max_value=99999),
)
@settings(max_examples=100)
def test_property_13_different_seeds_distinct_graphs(family, seed_a, seed_b):
    """
    Feature: vigil-benchmark, Property 13: Different seeds produce distinct graphs

    Two calls with different seeds produce graphs with different node orderings
    or different edge structures with probability ≥ 0.99.

    We use non-overlapping seed ranges (0-49999 vs 50000-99999) to ensure
    seed_a != seed_b in all cases, then check that at least one structural
    property differs.

    Validates: Requirements 9.3
    """
    # seed_a and seed_b are guaranteed different by the non-overlapping ranges
    assert seed_a != seed_b

    g1 = GEN.generate(family, seed_a, 1.0, BASE_CONFIG, {"type": "category_by_core_features"})
    g2 = GEN.generate(family, seed_b, 1.0, BASE_CONFIG, {"type": "category_by_core_features"})

    # Check at least one of: node IDs, features, categories, or edges differs
    node_ids_differ = set(g1.nodes.keys()) != set(g2.nodes.keys())

    features_differ = any(
        g1.nodes[nid].features != g2.nodes.get(nid, g1.nodes[nid]).features
        for nid in g1.nodes
        if nid in g2.nodes
    )

    categories_differ = any(
        g1.nodes[nid].category != g2.nodes.get(nid, g1.nodes[nid]).category
        for nid in g1.nodes
        if nid in g2.nodes
    )

    edges_differ = any(
        set(g1.get_neighbors(nid)) != set(g2.get_neighbors(nid))
        for nid in g1.nodes
        if nid in g2.nodes
    )

    something_differs = (
        node_ids_differ or features_differ or categories_differ or edges_differ
    )

    assert something_differs, (
        f"family={family}, seed_a={seed_a}, seed_b={seed_b}: "
        "two different seeds produced structurally identical graphs"
    )
