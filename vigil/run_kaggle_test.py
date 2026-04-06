#!/usr/bin/env python3
"""
Local test runner for Vigil Kaggle Benchmark tasks.

This script simulates the Kaggle environment to test task definitions
before submitting to the Kaggle leaderboard.

Usage:
    python run_kaggle_test.py [--difficulty 1|2|3] [--seed 42]
"""

import sys
import argparse
from pathlib import Path

# Add vigil to path
vigil_path = Path(__file__).parent
sys.path.insert(0, str(vigil_path.parent))

print("=" * 60)
print("Vigil Kaggle Benchmark - Local Test Runner")
print("=" * 60)

# Test 1: Import check
print("\n[1/4] Testing imports...")
try:
    from vigil.environments.concept_formation import ConceptFormationEnv
    from vigil.scenarios.loader import ScenarioLoader
    from vigil.actions.parser import parse_action
    from vigil.actions.schemas import ActionType
    print("  ✓ All imports successful")
except ImportError as e:
    print(f"  ✗ Import error: {e}")
    sys.exit(1)

# Test 2: Scenario loading
print("\n[2/4] Loading scenario configurations...")
try:
    loader = ScenarioLoader()
    concept_config = loader.load("concept_formation")
    print(f"  ✓ Loaded: {concept_config['scenario_id']}")
    print(f"    Track: {concept_config['cognitive_track']}")
    print(f"    Sub-ability: {concept_config['sub_ability']}")
except Exception as e:
    print(f"  ✗ Scenario load error: {e}")
    sys.exit(1)

# Test 3: Environment instantiation
print("\n[3/4] Testing environment instantiation...")
try:
    env = ConceptFormationEnv(scenario_config=concept_config, difficulty=1, seed=42)
    state = env.reset()
    print(f"  ✓ Environment created")
    print(f"    Graph nodes: {len(env.graph.nodes)}")
    print(f"    Initial budget: {state.budget_remaining}")
except Exception as e:
    print(f"  ✗ Environment error: {e}")
    sys.exit(1)

# Test 4: Action execution
print("\n[4/4] Testing action execution...")
try:
    action_menu = env.get_available_actions(state)
    print(f"  ✓ Action menu generated ({len(action_menu)} chars)")

    # Test action parsing
    from vigil.actions.parser import parse_action
    test_actions = [
        "expand:node_1",
        "submit",
        "backtrack",
        "inspect:node_0"
    ]
    for action_str in test_actions:
        action = parse_action(action_str)
        if action:
            print(f"    Parsed: '{action_str}' -> {action.action_type.value}")
        else:
            print(f"    Failed to parse: '{action_str}'")

    # Test scoring
    final_answer = "Nodes in the same category share core features"
    scores = env.score_exploration(state, final_answer)
    print(f"\n  ✓ Scoring test:")
    for metric, score in scores.items():
        print(f"    {metric}: {score:.3f}")

except Exception as e:
    print(f"  ✗ Action execution error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("All local tests passed!")
print("=" * 60)
print("\nNext steps:")
print("1. Copy vigil/ to your Kaggle notebook")
print("2. Run vigil_kaggle_notebook.ipynb on Kaggle")
print("3. Submit to leaderboard with %choose magic command")
print()
