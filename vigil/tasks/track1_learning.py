"""
Track 1: Learning — Kaggle Benchmark Tasks

Architecture (Req 17):
  - Six sub-tasks (store_task=False): one per learning sub-ability
  - One primary aggregated task (store_task=True): vigil_learning_benchmark
    Uses .evaluate() with a DataFrame of (scenario_type, difficulty, seed) rows.
    Returns aggregate float to the leaderboard.

SDK integration:
  - schema=VigilAction passed to llm.prompt() for structured output
  - Hard 20-turn cap (Req 17.8)
  - Returns 0.0 on budget exhaustion or timeout (Req 17.7)
  - Two-stage MC scoring: citation ratio + optional judge LLM (Req 10.8)
  - %choose vigil_learning_benchmark for leaderboard (Req 17.5)

Note: @kbench.task decorators are guarded by try/except so this module
can be imported locally without kaggle_benchmarks installed.
Task 11 is the final SDK integration — the decorators are active here.
"""

from typing import Any, Dict, Optional

try:
    import kaggle_benchmarks as kbench
    import pandas as pd
    _KBENCH_AVAILABLE = True
except ImportError:
    _KBENCH_AVAILABLE = False
    kbench = None

from vigil.actions.parser import parse_action
from vigil.actions.schemas import SubmitAnswerAction, VigilAction
from vigil.environments.associative import AssociativeLearningEnv
from vigil.environments.concept_formation import ConceptFormationEnv
from vigil.environments.language import LanguageLearningEnv
from vigil.environments.observational import ObservationalLearningEnv
from vigil.environments.procedural import ProceduralLearningEnv
from vigil.environments.reinforcement import ReinforcementLearningEnv
from vigil.scenarios.loader import ScenarioLoader
from vigil.scoring.vis import VISScorer

_SCORER = VISScorer()
_LOADER = ScenarioLoader()

# Map scenario_type string → (env_class, scenario_name)
_ENV_MAP = {
    "concept_formation":   (ConceptFormationEnv,   "concept_formation"),
    "associative":         (AssociativeLearningEnv, "associative"),
    "reinforcement":       (ReinforcementLearningEnv, "reinforcement"),
    "observational":       (ObservationalLearningEnv, "observational"),
    "procedural":          (ProceduralLearningEnv,  "procedural"),
    "language":            (LanguageLearningEnv,    "language"),
}


# ---------------------------------------------------------------------------
# Core episode runner (shared by all sub-tasks)
# ---------------------------------------------------------------------------

def _run_episode(llm: Any, env: Any, judge_llm: Any = None) -> float:
    """
    Run one episode of any CognitiveEnvironment.

    - Passes schema=VigilAction to llm.prompt() for structured output (Req 17.2)
    - Hard 20-turn cap (Req 17.8)
    - Returns 0.0 on budget exhaustion or timeout (Req 17.7)
    - Two-stage MC scoring via VISScorer (Req 10.8)
    """
    state = env.reset()
    final_answer = ""
    justification = ""

    for _turn in range(20):  # Hard 20-turn cap (Req 17.8)
        if state.episode_done or state.budget_remaining <= 0:
            break

        obs = env.render(state)

        # Req 17.2: pass schema=VigilAction for structured output
        if _KBENCH_AVAILABLE:
            action = llm.prompt(obs, schema=VigilAction)
        else:
            # Local testing fallback: parse from string response
            response = llm.prompt(obs)
            action = parse_action(response)

        state = env.execute_action(state, action)

        if state.episode_done:
            # Extract answer and justification from last submit event
            last = state.action_history[-1] if state.action_history else None
            if last and last.params:
                final_answer = last.params.get("answer", "")
                justification = last.params.get("justification", "")
            elif isinstance(action, SubmitAnswerAction):
                final_answer = action.answer
                justification = action.justification
            break

    if not state.episode_done:
        return 0.0  # Req 17.7: timeout/budget exhaustion → 0.0

    # Score the episode
    episode_scores = env.score_episode(state, final_answer, justification)
    outcome_score = episode_scores.get("correctness", 0.0)

    # VIS scoring with two-stage MC (Req 10.8, 17.3)
    scenario_config = env.scenario_config
    vis_result = _SCORER.score_episode(
        state=state,
        final_answer=final_answer,
        justification=justification,
        scenario_config=scenario_config,
        outcome_score=outcome_score,
        judge_llm=judge_llm,
    )
    return float(vis_result["vis"])


# ---------------------------------------------------------------------------
# Sub-task factory
# ---------------------------------------------------------------------------

def _make_sub_task(scenario_type: str):
    """Create a sub-task function for a given scenario type."""
    env_class, scenario_name = _ENV_MAP[scenario_type]

    def sub_task(llm, difficulty: int = 2, seed: int = 42) -> float:
        config = _LOADER.load(scenario_name)
        env = env_class(scenario_config=config, difficulty=difficulty, seed=seed)
        judge = getattr(kbench, "judge_llm", None) if _KBENCH_AVAILABLE else None
        return _run_episode(llm, env, judge_llm=judge)

    sub_task.__name__ = f"{scenario_type}_sub"
    sub_task.__doc__ = f"Track 1 Learning: {scenario_type.replace('_', ' ').title()} sub-task. Returns VIS float."
    return sub_task


# ---------------------------------------------------------------------------
# Six sub-tasks (store_task=False — internal, not leaderboard entries)
# ---------------------------------------------------------------------------

if _KBENCH_AVAILABLE:
    concept_formation_sub = kbench.task(
        name="concept_formation_sub", store_task=False
    )(_make_sub_task("concept_formation"))

    associative_sub = kbench.task(
        name="associative_sub", store_task=False
    )(_make_sub_task("associative"))

    reinforcement_sub = kbench.task(
        name="reinforcement_sub", store_task=False
    )(_make_sub_task("reinforcement"))

    observational_sub = kbench.task(
        name="observational_sub", store_task=False
    )(_make_sub_task("observational"))

    procedural_sub = kbench.task(
        name="procedural_sub", store_task=False
    )(_make_sub_task("procedural"))

    language_sub = kbench.task(
        name="language_sub", store_task=False
    )(_make_sub_task("language"))

    _SUB_TASKS = {
        "concept_formation": concept_formation_sub,
        "associative":       associative_sub,
        "reinforcement":     reinforcement_sub,
        "observational":     observational_sub,
        "procedural":        procedural_sub,
        "language":          language_sub,
    }

    # -----------------------------------------------------------------------
    # Primary aggregated leaderboard task (store_task=True)
    # -----------------------------------------------------------------------

    @kbench.task(name="vigil_learning_benchmark")
    def vigil_learning_benchmark(llm) -> float:
        """
        Vigil: Don't Ask — Watch. Track 1: Learning.

        Aggregates all 6 learning sub-ability environments across multiple
        difficulty levels and seeds. Returns mean VIS score as the leaderboard float.

        Req 17.4: uses .evaluate() with a (scenario_type, difficulty, seed) DataFrame.
        Req 17.5: %choose vigil_learning_benchmark for leaderboard submission.
        """
        # Build evaluation DataFrame: 3 seeds × 2 difficulties × 6 scenarios = 36 runs
        rows = []
        for scenario_type in _ENV_MAP:
            for difficulty in [1, 2]:
                for seed in [42, 137, 999]:
                    rows.append({
                        "scenario_type": scenario_type,
                        "difficulty": difficulty,
                        "seed": seed,
                    })
        df = pd.DataFrame(rows)

        # Run all sub-tasks via .evaluate()
        all_scores = []
        for scenario_type, sub_task in _SUB_TASKS.items():
            scenario_df = df[df["scenario_type"] == scenario_type][["difficulty", "seed"]]
            with kbench.client.enable_cache():
                runs = sub_task.evaluate(
                    llm=[llm],
                    evaluation_data=scenario_df,
                    n_jobs=2,
                    timeout=300,
                )
            eval_df = runs.as_dataframe()
            if len(eval_df) > 0:
                all_scores.extend(eval_df["result"].tolist())

        if not all_scores:
            return 0.0
        return float(sum(all_scores) / len(all_scores))

else:
    # Local fallback: plain functions without SDK decorators
    def concept_formation_sub(llm, difficulty: int = 2, seed: int = 42) -> float:
        config = _LOADER.load("concept_formation")
        env = ConceptFormationEnv(scenario_config=config, difficulty=difficulty, seed=seed)
        return _run_episode(llm, env)

    def associative_sub(llm, difficulty: int = 2, seed: int = 42) -> float:
        config = _LOADER.load("associative")
        env = AssociativeLearningEnv(scenario_config=config, difficulty=difficulty, seed=seed)
        return _run_episode(llm, env)

    def reinforcement_sub(llm, difficulty: int = 2, seed: int = 42) -> float:
        config = _LOADER.load("reinforcement")
        env = ReinforcementLearningEnv(scenario_config=config, difficulty=difficulty, seed=seed)
        return _run_episode(llm, env)

    def observational_sub(llm, difficulty: int = 2, seed: int = 42) -> float:
        config = _LOADER.load("observational")
        env = ObservationalLearningEnv(scenario_config=config, difficulty=difficulty, seed=seed)
        return _run_episode(llm, env)

    def procedural_sub(llm, difficulty: int = 2, seed: int = 42) -> float:
        config = _LOADER.load("procedural")
        env = ProceduralLearningEnv(scenario_config=config, difficulty=difficulty, seed=seed)
        return _run_episode(llm, env)

    def language_sub(llm, difficulty: int = 2, seed: int = 42) -> float:
        config = _LOADER.load("language")
        env = LanguageLearningEnv(scenario_config=config, difficulty=difficulty, seed=seed)
        return _run_episode(llm, env)

    _SUB_TASKS = {
        "concept_formation": concept_formation_sub,
        "associative":       associative_sub,
        "reinforcement":     reinforcement_sub,
        "observational":     observational_sub,
        "procedural":        procedural_sub,
        "language":          language_sub,
    }

    def vigil_learning_benchmark(llm) -> float:
        """Local fallback: runs all 6 sub-tasks with default params."""
        scores = [fn(llm) for fn in _SUB_TASKS.values()]
        return sum(scores) / len(scores) if scores else 0.0
