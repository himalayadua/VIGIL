"""
Track 1: Learning — Kaggle Benchmark Tasks (thin wrapper).

Delegates to vigil_benchmark.py for all episode execution.
vigil_learning_benchmark filters to the "learning" cognitive_track.

Requirements: 15, 18
"""

from typing import Any

try:
    import kaggle_benchmarks as kbench
    _KBENCH_AVAILABLE = True
except ImportError:
    _KBENCH_AVAILABLE = False
    kbench = None

from vigil.tasks.vigil_benchmark import _vigil_benchmark_impl, _get_catalog


# ---------------------------------------------------------------------------
# vigil_learning_benchmark — Track 1 leaderboard task
# ---------------------------------------------------------------------------

def _vigil_learning_benchmark_impl(llm: Any, packs_dir: str = "vigil/scenarios/packs/") -> float:
    """
    Run vigil_benchmark filtered to the "learning" cognitive_track.

    Builds (scenario_id, seed) matrix for learning scenarios only,
    then delegates to the shared _vigil_benchmark_impl pipeline.
    """
    from vigil.environments.graph_scenario_env import GraphScenarioEnvironment
    from vigil.tasks.vigil_benchmark import _run_episode, _SCORER, _PROFILER

    catalog = _get_catalog(packs_dir)
    learning_ids = catalog.get_scenario_ids(track="learning")

    if not learning_ids:
        return 0.0

    rows = [
        {"scenario_id": sid, "seed": seed}
        for sid in learning_ids
        for seed in [0, 1, 2]
    ]

    all_results = []
    for row in rows:
        spec = catalog.load(row["scenario_id"], seed=row["seed"])
        env = GraphScenarioEnvironment(spec)
        result = _run_episode(llm, env, spec, seed=row["seed"])
        all_results.append(result)

    if not all_results:
        return 0.0

    scenario_aggregates = _PROFILER.aggregate_seeds(all_results)
    profiles = _PROFILER.build_profile(scenario_aggregates)
    return _PROFILER.benchmark_aggregate(profiles)


if _KBENCH_AVAILABLE:
    @kbench.task(name="vigil_learning_benchmark")
    def vigil_learning_benchmark(llm: Any) -> float:
        """
        Vigil: Don't Ask — Watch. Track 1: Learning.

        Thin wrapper over vigil_benchmark filtered to the "learning" track.
        Returns mean VIS score as the leaderboard float.
        """
        return _vigil_learning_benchmark_impl(llm)

else:
    def vigil_learning_benchmark(llm: Any) -> float:
        """Local fallback for vigil_learning_benchmark without Kaggle SDK."""
        return _vigil_learning_benchmark_impl(llm)
