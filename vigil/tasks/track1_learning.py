"""
Track 1: Learning - Kaggle Benchmark Tasks

Implements cognitive graph environments for the Learning faculty:
- Concept Formation
- Associative Learning
- Reinforcement Learning

Each task follows the Kaggle Benchmarks SDK pattern:
- @kbench.task decorator
- llm as first parameter
- Proper return type annotations (-> float)
"""

import kaggle_benchmarks as kbench
from typing import Optional, Dict, Any

from vigil.environments.concept_formation import ConceptFormationEnv
from vigil.environments.associative import AssociativeLearningEnv
from vigil.environments.reinforcement import ReinforcementLearningEnv
from vigil.scenarios.loader import ScenarioLoader
from vigil.actions.parser import parse_action
from vigil.actions.schemas import ActionType, GraphAction


def _run_exploration_loop(
    llm,
    env,
    state,
    max_turns: int = 15
) -> tuple[bool, str, Dict[str, float]]:
    """
    Run the main exploration loop for any cognitive environment.

    Args:
        llm: LLM to evaluate
        env: Cognitive environment instance
        state: Initial environment state
        max_turns: Maximum exploration turns

    Returns:
        Tuple of (completed, final_answer, scores)
    """
    final_answer = ""

    for turn in range(max_turns):
        if state.budget_remaining <= 0:
            break

        # Present current state and get action
        prompt = f"""
You are exploring an unknown graph to discover a hidden pattern.
The graph contains nodes belonging to hidden categories.
Nodes in the same category share core features.
Your task is to infer the categorization rule.

{env.get_available_actions(state)}

Your action (use format 'expand:node_id' or 'submit' when ready):
"""
        response = llm.prompt(prompt)

        # Parse action
        action = parse_action(response)

        if action and action.is_valid():
            success, obs = env.execute_action(state, action)

            if action.action_type == ActionType.SUBMIT:
                # Get final hypothesis
                final_prompt = """
Based on your exploration, what is the hidden rule for how nodes are categorized?
Describe the pattern you discovered.
"""
                final_answer = llm.prompt(final_prompt)
                scores = env.score_exploration(state, final_answer)
                return True, final_answer, scores

        # Update state display
        state = env.reset() if not state else state

    # Timeout - model didn't submit
    return False, final_answer, {}


@kbench.task(name="concept_formation_learning")
def concept_formation_task(
    llm,
    difficulty: int = 2,
    seed: int = 42
) -> float:
    """
    Track 1 Learning: Concept Formation Test

    Model must explore graph and infer latent categorization rule.
    Scored 0.0 - 1.0 on correctness, efficiency, evidence, calibration.

    Args:
        llm: LLM to evaluate
        difficulty: Difficulty level (1-3)
        seed: Random seed for reproducibility

    Returns:
        Final score (0.0 - 1.0)
    """
    # Load scenario configuration
    loader = ScenarioLoader()
    config = loader.load("concept_formation")

    # Initialize environment
    env = ConceptFormationEnv(
        scenario_config=config,
        difficulty=difficulty,
        seed=seed
    )
    state = env.reset()

    # Exploration loop
    max_turns = 15
    for turn in range(max_turns):
        if state.budget_remaining <= 0:
            break

        # Present current state
        prompt = f"""
You are exploring an unknown graph to discover a hidden pattern.
The graph contains nodes belonging to hidden categories.
Nodes in the same category share core features.
Your task is to infer the categorization rule.

{env.get_available_actions(state)}

Your action:
"""
        response = llm.prompt(prompt)

        # Parse and execute action
        action = parse_action(response)

        if action and action.is_valid():
            success, obs = env.execute_action(state, action)

            if action.action_type == ActionType.SUBMIT:
                # Get final hypothesis
                final_prompt = """
Based on your exploration, what is the hidden rule for how nodes are categorized?
Describe the pattern you discovered.
"""
                final_answer = llm.prompt(final_prompt)
                scores = env.score_exploration(state, final_answer)
                return scores["final_score"]

    # Timeout - model didn't submit
    return 0.0


@kbench.task(name="associative_learning")
def associative_learning_task(
    llm,
    difficulty: int = 2,
    seed: int = 42
) -> float:
    """
    Track 1 Learning: Associative Learning Test

    Model must learn relationships between co-occurring events.
    Scored 0.0 - 1.0.

    Args:
        llm: LLM to evaluate
        difficulty: Difficulty level (1-3)
        seed: Random seed

    Returns:
        Final score (0.0 - 1.0)
    """
    # Load scenario configuration
    loader = ScenarioLoader()
    config = loader.load("associative")

    # Initialize environment
    env = AssociativeLearningEnv(
        scenario_config=config,
        difficulty=difficulty,
        seed=seed
    )
    state = env.reset()

    # Exploration loop
    max_turns = 12
    for turn in range(max_turns):
        if state.budget_remaining <= 0:
            break

        prompt = f"""
You are exploring to discover associations between nodes.
Certain nodes appear together in pairs - your task is to find the pattern.

{env.get_available_actions(state)}

Your action:
"""
        response = llm.prompt(prompt)
        action = parse_action(response)

        if action and action.is_valid():
            success, obs = env.execute_action(state, action)

            if action.action_type == ActionType.SUBMIT:
                final_prompt = """
Based on your exploration, describe the association pattern you discovered.
"""
                final_answer = llm.prompt(final_prompt)
                scores = env.score_exploration(state, final_answer)
                return scores["final_score"]

    return 0.0


@kbench.task(name="reinforcement_learning")
def reinforcement_learning_task(
    llm,
    difficulty: int = 2,
    seed: int = 42
) -> float:
    """
    Track 1 Learning: Reinforcement Learning Test

    Model must learn from rewards and punishments.
    Scored 0.0 - 1.0.

    Args:
        llm: LLM to evaluate
        difficulty: Difficulty level (1-3)
        seed: Random seed

    Returns:
        Final score (0.0 - 1.0)
    """
    # Load scenario configuration
    loader = ScenarioLoader()
    config = loader.load("reinforcement")

    # Initialize environment
    env = ReinforcementLearningEnv(
        scenario_config=config,
        difficulty=difficulty,
        seed=seed
    )
    state = env.reset()

    # Exploration loop
    max_turns = 15
    for turn in range(max_turns):
        if state.budget_remaining <= 0:
            break

        prompt = f"""
You are navigating an environment with rewards and penalties.
Find the reward nodes and avoid penalty nodes.
Maximize your total reward.

{env.get_available_actions(state)}

Your action:
"""
        response = llm.prompt(prompt)
        action = parse_action(response)

        if action and action.is_valid():
            success, obs = env.execute_action(state, action)

            if action.action_type == ActionType.SUBMIT:
                final_prompt = """
Based on your exploration, describe the reward structure you discovered.
"""
                final_answer = llm.prompt(final_prompt)
                scores = env.score_exploration(state, final_answer)
                return scores["final_score"]

    return 0.0


@kbench.task(name="concept_formation_dataset")
def concept_formation_dataset_task(
    llm,
    difficulty: int,
    seed: int
) -> bool:
    """
    Single instance task for dataset evaluation.

    Returns True if score > 0.5, False otherwise.
    Used with .evaluate() for running multiple graph instances.

    Args:
        llm: LLM to evaluate
        difficulty: Difficulty level
        seed: Random seed

    Returns:
        bool: True if passed (score > 0.5)
    """
    score = concept_formation_task.run(llm, difficulty=difficulty, seed=seed)
    return score > 0.5
