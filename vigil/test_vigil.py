#!/usr/bin/env python3
"""
Test script for Vigil benchmark framework.

Run this to verify the implementation is working correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path (vigil is already the package)
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))


def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")

    from vigil.environments.base import CognitiveEnvironment, EnvironmentState, GraphAction, ActionType
    from vigil.graphs.core import CognitiveGraph, GraphNode, GraphEdge
    from vigil.scenarios.loader import ScenarioLoader
    from vigil.actions.schemas import GraphAction as ActionSchema
    from vigil.actions.parser import parse_action
    from vigil.scoring.profile import CognitiveProfile
    from vigil.scoring.metrics import compute_correctness, compute_efficiency

    print("  All imports successful!")
    return True


def test_scenario_loader():
    """Test scenario loading."""
    print("\nTesting scenario loader...")

    from vigil.scenarios.loader import ScenarioLoader

    loader = ScenarioLoader()
    scenario_ids = loader.get_scenario_ids()

    print(f"  Available scenarios: {scenario_ids}")

    # Load concept formation config
    config = loader.load("concept_formation")
    assert "scenario_id" in config
    assert config["cognitive_track"] == "learning"

    print(f"  Loaded: {config['scenario_id']}")
    print("  Scenario loader test passed!")
    return True


def test_concept_formation_env():
    """Test concept formation environment."""
    print("\nTesting concept formation environment...")

    from vigil.environments.concept_formation import ConceptFormationEnv
    from vigil.scenarios.loader import ScenarioLoader
    from vigil.actions.schemas import ActionType

    # Load config
    loader = ScenarioLoader()
    config = loader.load("concept_formation")

    # Create environment
    env = ConceptFormationEnv(scenario_config=config, difficulty=1, seed=42)
    state = env.reset()

    print(f"  Graph nodes: {len(env.graph.nodes)}")
    print(f"  Initial state: {state.current_node}, budget={state.budget_remaining}")

    # Test action menu
    action_menu = env.get_available_actions(state)
    assert "Current node" in action_menu
    assert "expand" in action_menu
    print(f"  Action menu generated: {len(action_menu)} chars")

    # Test exploration
    print("\n  Running short exploration...")
    for turn in range(3):
        if state.budget_remaining <= 0:
            break

        # Simulate expand action
        from vigil.environments.base import GraphAction
        action = GraphAction(
            action_type=ActionType.EXPAND,
            target_node=f"node_{(turn + 1) % len(env.graph.nodes)}"
        )

        success, obs = env.execute_action(state, action)
        print(f"    Turn {turn}: success={success}, obs={obs[:50]}...")

    # Test scoring
    final_answer = "Nodes in the same category share core features"
    scores = env.score_exploration(state, final_answer)

    print(f"\n  Scores:")
    for metric, score in scores.items():
        print(f"    {metric}: {score:.3f}")

    print("\n  Concept formation environment test passed!")
    return True


def test_action_parser():
    """Test action parsing."""
    print("\nTesting action parser...")

    from vigil.actions.parser import parse_action
    from vigil.actions.schemas import ActionType

    test_cases = [
        ("expand:node_5", ActionType.EXPAND, "node_5"),
        ("expand node_3", ActionType.EXPAND, "node_3"),
        ("submit", ActionType.SUBMIT, None),
        ("backtrack", ActionType.BACKTRACK, None),
        ("inspect:node_1", ActionType.INSPECT, "node_1"),
    ]

    for response, expected_type, expected_target in test_cases:
        action = parse_action(response)
        if action:
            print(f"  '{response}' -> {action.action_type.value} (target: {action.target_node})")
            assert action.action_type == expected_type
            if expected_target:
                assert action.target_node == expected_target
        else:
            print(f"  '{response}' -> None (expected {expected_type})")

    print("  Action parser test passed!")
    return True


def test_graph_generation():
    """Test graph generation."""
    print("\nTesting graph generation...")

    from vigil.graphs.core import CognitiveGraph, GraphNode, GraphEdge

    # Create simple graph
    graph = CognitiveGraph()

    # Add nodes
    for i in range(5):
        node = GraphNode(
            node_id=f"node_{i}",
            features={f"feature_{i}", f"feature_{i+1}"},
            category=f"cat_{i % 2}"
        )
        graph.add_node(node)

    # Add edges
    for i in range(4):
        graph.add_edge(
            f"node_{i}",
            GraphEdge(source=f"node_{i}", target=f"node_{i+1}", relation_type="connected_to")
        )

    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Edges: {sum(len(edges) for edges in graph.edges.values())}")

    # Test node retrieval
    node = graph.get_node("node_2")
    assert node is not None
    assert node.category == "cat_0"

    # Test neighbor retrieval
    neighbors = graph.get_neighbors("node_0")
    assert "node_1" in neighbors

    print("  Graph generation test passed!")
    return True


def test_scoring():
    """Test scoring functions."""
    print("\nTesting scoring...")

    from vigil.scoring.metrics import (
        compute_correctness,
        compute_efficiency,
        compute_evidence_quality,
        compute_calibration,
        compute_weighted_score
    )
    from vigil.environments.base import EnvironmentState

    # Test correctness
    answer = "The core features determine the category"
    rule = "Nodes in same category share core features"
    correctness = compute_correctness(answer, rule)
    print(f"  Correctness: {correctness}")

    # Test efficiency
    state = EnvironmentState(
        current_node="node_0",
        visited_nodes=["node_0", "node_1", "node_2"],
        budget_remaining=5
    )
    efficiency = compute_efficiency(state, optimal_path_length=3)
    print(f"  Efficiency: {efficiency}")

    # Test weighted score
    scores = {
        "correctness": 1.0,
        "efficiency": 0.8,
        "evidence_quality": 0.6,
        "calibration": 0.5,
        "recovery": 0.5
    }
    weights = {
        "correctness": 0.5,
        "efficiency": 0.2,
        "evidence_quality": 0.2,
        "calibration": 0.1
    }
    weighted = compute_weighted_score(scores, weights)
    print(f"  Weighted score: {weighted}")

    print("  Scoring test passed!")
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Vigil Framework Tests")
    print("=" * 60)

    tests = [
        test_imports,
        test_scenario_loader,
        test_graph_generation,
        test_action_parser,
        test_concept_formation_env,
        test_scoring
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n  TEST FAILED: {test.__name__}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
