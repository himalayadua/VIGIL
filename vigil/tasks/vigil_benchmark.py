"""
Vigil multi-track benchmark — Kaggle task functions.

Architecture:
  - vigil_episode (store_task=False): one scenario episode, returns VIS float
  - vigil_benchmark (store_task=True): runs all scenarios × 3 seeds via
    .evaluate(), aggregates via FacultyProfiler two-stage pipeline

Episode loop (mirrors existing _run_episode in track1_learning.py):
  - Hard 20-turn cap
  - Three independent limits: budget_remaining <= 0, episode_done, turn cap
  - Per-track action schema via TrackActionSchema.for_track()
  - Two-step scoring: env.score_episode() → ScoreCard → VISScorer → VISResult

Artifact retrieval:
  vigil_episode writes the full VISResult to the row's SDK artifact payload.
  vigil_benchmark reads those row artifacts after .evaluate() completes.
  This avoids relying on module-level in-memory state across parallel workers.

Requirements: 15, 19, 21
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
from vigil.environments.graph_scenario_env import GraphScenarioEnvironment
from vigil.scenarios.catalog import ScenarioCatalog
from vigil.scoring.faculty_profiler import FacultyProfiler
from vigil.scoring.vis import VISScorer

# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------

_SCORER = VISScorer()
_PROFILER = FacultyProfiler()

# Default packs directory — can be overridden for testing
_DEFAULT_PACKS_DIR = "vigil/scenarios/packs/"

# Lazy-initialised catalog (avoids import-time file I/O)
_catalog: Optional[ScenarioCatalog] = None


def _get_catalog(packs_dir: str = _DEFAULT_PACKS_DIR) -> ScenarioCatalog:
    """Return the module-level ScenarioCatalog, initialising on first call."""
    global _catalog
    if _catalog is None:
        _catalog = ScenarioCatalog(packs_dir=packs_dir)
    return _catalog


# ---------------------------------------------------------------------------
# TrackActionSchema — per-track action subset for llm.prompt()
# ---------------------------------------------------------------------------

def _get_action_schema(cognitive_track: str) -> Any:
    """
    Return the per-track action schema to pass as schema= to llm.prompt().

    Tries to import TrackActionSchema (added in task 10).
    Falls back to the base VigilAction union if not yet available.
    """
    try:
        from vigil.actions.schemas import TrackActionSchema
        return TrackActionSchema.for_track(cognitive_track)
    except (ImportError, AttributeError):
        return VigilAction


# ---------------------------------------------------------------------------
# Core episode runner
# ---------------------------------------------------------------------------

def _run_episode(
    llm: Any,
    env: GraphScenarioEnvironment,
    spec: Any,
    seed: int = 0,
    judge_llm: Any = None,
) -> Dict[str, Any]:
    """
    Run one episode of GraphScenarioEnvironment and return a full VISResult dict.

    Returns a dict (not just float) so FacultyProfiler can use behavioral_signatures
    and contamination_warning for two-stage aggregation.

    Three independent limits (Property 10):
      1. state.budget_remaining <= 0  → return 0.0 result
      2. state.episode_done           → proceed to scoring
      3. Hard 20-turn cap             → return 0.0 result

    None of these limits is derived from spec.optimal_steps.

    Args:
        llm:       LLM callable (kbench llm or local mock).
        env:       Initialised GraphScenarioEnvironment.
        spec:      RuntimeScenarioSpec for this episode.
        seed:      Seed used for this run (stored in result for FacultyProfiler).
        judge_llm: Optional judge LLM for two-stage MC scoring.

    Returns:
        VISResult dict with at minimum:
          vis, outcome_score, process_score, track_id, scenario_id, seed,
          behavioral_signatures, contamination_warning.
        Returns vis=0.0 on timeout or budget exhaustion without submit.
    """
    _null_result = {
        "vis": 0.0,
        "outcome_score": 0.0,
        "process_score": 0.0,
        "track_id": spec.cognitive_track,
        "scenario_id": spec.scenario_id,
        "seed": seed,
        "behavioral_signatures": {},
        "contamination_warning": False,
    }

    state = env.reset()
    final_answer = ""
    justification = ""
    action_schema = _get_action_schema(spec.cognitive_track)

    for _turn in range(20):  # Hard 20-turn cap (Req 15, Property 10)
        # Limit 1: budget exhausted
        if state.budget_remaining <= 0:
            return _null_result

        # Limit 2: episode already done (shouldn't happen mid-loop, but guard)
        if state.episode_done:
            break

        obs = env.render(state)

        # Pass per-track action schema to llm.prompt()
        if _KBENCH_AVAILABLE:
            action = llm.prompt(obs, schema=action_schema)
        else:
            # Local testing fallback: parse from string response
            response = llm.prompt(obs)
            action = parse_action(response)

        state = env.execute_action(state, action)

        if state.episode_done:
            # Extract answer and justification from last submit event
            from vigil.environments.base import EventType
            last = state.action_history[-1] if state.action_history else None
            if last and last.params:
                final_answer = last.params.get("answer", "")
                justification = last.params.get("justification", "")
            elif isinstance(action, SubmitAnswerAction):
                final_answer = action.answer
                justification = action.justification
            break

    # Limit 3: turn cap reached without submit
    if not state.episode_done:
        return _null_result

    # Two-step scoring:
    # Step 1: env returns ScoreCard (track dimensions, no vis key)
    scorecard = env.score_episode(state, final_answer, justification)

    # Step 2: VISScorer applies shared utilities + 0.3/0.7 formula
    vis_result = _SCORER.score_episode(
        state=state,
        final_answer=final_answer,
        justification=justification,
        scenario_config=spec.to_scenario_config_dict(),
        outcome_score=scorecard.get("outcome_score", 0.0),
        scorecard=scorecard,
        judge_llm=judge_llm,
    )

    # Ensure scenario_id and seed are in the result for FacultyProfiler
    vis_result["scenario_id"] = spec.scenario_id
    vis_result["seed"] = seed

    return vis_result


# ---------------------------------------------------------------------------
# vigil_episode — single scenario task
# ---------------------------------------------------------------------------

def _vigil_episode_impl(
    llm: Any,
    scenario_id: str,
    seed: int = 0,
    packs_dir: str = _DEFAULT_PACKS_DIR,
) -> float:
    """
    Core implementation of vigil_episode, separated for testability.

    Loads spec, runs episode, writes VISResult to row artifact, returns float.
    """
    catalog = _get_catalog(packs_dir)
    spec = catalog.load(scenario_id, seed=seed)
    env = GraphScenarioEnvironment(spec)
    judge = getattr(kbench, "judge_llm", None) if _KBENCH_AVAILABLE else None
    result = _run_episode(llm, env, spec, seed=seed, judge_llm=judge)

    # Write full VISResult to row artifact for vigil_benchmark to retrieve
    if _KBENCH_AVAILABLE:
        try:
            kbench.artifacts.log("vis_result", result)
        except Exception:
            pass  # artifact logging is best-effort

    return float(result.get("vis", 0.0))


# ---------------------------------------------------------------------------
# vigil_benchmark — multi-track benchmark task
# ---------------------------------------------------------------------------

def _vigil_benchmark_impl(
    llm: Any,
    packs_dir: str = _DEFAULT_PACKS_DIR,
) -> float:
    """
    Core implementation of vigil_benchmark, separated for testability.

    Builds (scenario_id, seed) matrix, runs via .evaluate(), aggregates
    via FacultyProfiler two-stage pipeline.
    """
    catalog = _get_catalog(packs_dir)

    # Build (scenario_id, seed) evaluation matrix — 3 seeds per scenario
    rows = [
        {"scenario_id": sid, "seed": seed}
        for sid in catalog.get_scenario_ids()
        for seed in [0, 1, 2]
    ]

    if not rows:
        return 0.0

    if not _KBENCH_AVAILABLE:
        # Local fallback: run episodes directly without .evaluate()
        all_results = []
        for row in rows:
            spec = catalog.load(row["scenario_id"], seed=row["seed"])
            env = GraphScenarioEnvironment(spec)
            result = _run_episode(llm, env, spec, seed=row["seed"])
            all_results.append(result)
    else:
        df = pd.DataFrame(rows)
        runs = vigil_episode.evaluate(llm=[llm], evaluation_data=df, n_jobs=2)

        # Retrieve full VISResult objects from row artifacts
        all_results = []
        for run in runs:
            try:
                vis_result = run.artifacts["vis_result"]
                all_results.append(vis_result)
            except (AttributeError, KeyError):
                # Fallback: reconstruct minimal result from float
                all_results.append({
                    "vis": float(run.result or 0.0),
                    "scenario_id": run.params.get("scenario_id", ""),
                    "track_id": "unknown",
                    "behavioral_signatures": {},
                    "contamination_warning": False,
                })

    # Two-stage aggregation
    scenario_aggregates = _PROFILER.aggregate_seeds(all_results)
    profiles = _PROFILER.build_profile(scenario_aggregates)
    artifact = _PROFILER.to_artifact_dict(profiles, scenario_aggregates)

    # Log full CognitiveProfile artifact (not leaderboard)
    if _KBENCH_AVAILABLE:
        try:
            kbench.artifacts.log("vigil_cognitive_profile", artifact)
        except Exception:
            pass

    return _PROFILER.benchmark_aggregate(profiles)


# ---------------------------------------------------------------------------
# Kaggle task decorators (guarded so module imports without SDK)
# ---------------------------------------------------------------------------

if _KBENCH_AVAILABLE:
    @kbench.task(store_task=False)
    def vigil_episode(llm: Any, scenario_id: str, seed: int = 0) -> float:
        """
        Single scenario episode. Returns VIS float to leaderboard.

        Also writes full VISResult to the row's SDK artifact payload so
        vigil_benchmark can retrieve it after .evaluate() completes.

        Args:
            llm:         LLM callable provided by Kaggle SDK.
            scenario_id: Unique scenario identifier.
            seed:        0 = no perturbation (default). Other values apply
                         deterministic node-order reordering.
        """
        return _vigil_episode_impl(llm, scenario_id, seed)

    @kbench.task(name="vigil_benchmark", store_task=True)
    def vigil_benchmark(llm: Any) -> float:
        """
        Vigil: Don't Ask — Watch. Multi-track cognitive benchmark.

        Runs all scenarios × 3 seeds via .evaluate(), then aggregates:
          Stage 1: FacultyProfiler.aggregate_seeds() → ScenarioAggregate per scenario
          Stage 2: FacultyProfiler.build_profile() → FacultyProfile per track
          Final:   benchmark_aggregate() → mean of per-track means (NOT raw mean)

        Full CognitiveProfile stored in run artifacts.
        Leaderboard sees only the aggregate float.
        """
        return _vigil_benchmark_impl(llm)

else:
    # Local fallback: plain functions without SDK decorators
    def vigil_episode(llm: Any, scenario_id: str, seed: int = 0) -> float:
        """Local fallback for vigil_episode without Kaggle SDK."""
        return _vigil_episode_impl(llm, scenario_id, seed)

    def vigil_benchmark(llm: Any) -> float:
        """Local fallback for vigil_benchmark without Kaggle SDK."""
        return _vigil_benchmark_impl(llm)
