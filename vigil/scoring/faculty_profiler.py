"""
FacultyProfiler — benchmark-level two-stage aggregation.

Implements the DeepMind 3-stage protocol's "cognitive profile" output:
  Stage 1: aggregate_seeds()  — per (scenario_id, seed) → ScenarioAggregate
  Stage 2: build_profile()    — per cognitive_track → FacultyProfile
  Final:   benchmark_aggregate() — mean of per-track means (NOT raw scenario mean)

Key design principles:
  - VISResult is strictly per-episode (one run, one seed). No vis_variance.
  - ScenarioAggregate holds cross-seed variance for one scenario.
  - FacultyProfile holds cross-scenario variance for one cognitive track.
  - benchmark_aggregate() = mean({p.mean_vis}) — each faculty contributes equally
    regardless of how many scenarios it has.

Requirements: 19, 21
"""

from dataclasses import asdict, dataclass, field
from math import sqrt
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# ScenarioAggregate — per-scenario summary across seeds
# ---------------------------------------------------------------------------

@dataclass
class ScenarioAggregate:
    """
    Per-scenario summary across multiple seeds. NOT a single-run artifact.

    vis_variance is the cross-seed variance for this scenario.
    It is 0.0 when only one seed was run.

    Attributes:
        scenario_id:           Unique scenario identifier.
        cognitive_track:       Canonical track string.
        mean_vis:              Mean VIS across all seeds for this scenario.
        vis_variance:          Cross-seed variance; 0.0 when n_seeds == 1.
        n_seeds:               Number of seed runs aggregated.
        behavioral_signatures: Mean rate of each signature across seeds.
        contamination_warning: True if any seed triggered a contamination warning.
    """
    scenario_id: str
    cognitive_track: str
    mean_vis: float
    vis_variance: float
    n_seeds: int
    behavioral_signatures: Dict[str, float] = field(default_factory=dict)
    contamination_warning: bool = False


# ---------------------------------------------------------------------------
# FacultyProfile — per-track aggregate
# ---------------------------------------------------------------------------

@dataclass
class FacultyProfile:
    """
    Per-track aggregate produced by FacultyProfiler.build_profile().

    n_scenarios is the count of distinct scenario_ids — NOT seed runs.
    vis_variance is the variance of ScenarioAggregate.mean_vis values
    across scenarios in this track (different from cross-seed variance).

    Attributes:
        faculty:                    cognitive_track string.
        mean_vis:                   Mean of ScenarioAggregate.mean_vis values.
        vis_variance:               Variance of scenario-level mean_vis values.
        vis_std:                    Standard deviation of scenario-level means.
        n_scenarios:                Count of distinct scenario_ids (NOT seed runs).
        confidence_interval_95:     (lower, upper) 95% CI around mean_vis.
        human_percentile:           Populated when HumanBaseline available.
        behavioral_signature_summary: Mean rate per signature across scenarios.
        low_sample_warning:         True when n_scenarios < 5.
    """
    faculty: str
    mean_vis: float
    vis_variance: float
    vis_std: float
    n_scenarios: int
    confidence_interval_95: Tuple[float, float]
    human_percentile: Optional[float] = None
    behavioral_signature_summary: Dict[str, float] = field(default_factory=dict)
    low_sample_warning: bool = False


# ---------------------------------------------------------------------------
# FacultyProfiler
# ---------------------------------------------------------------------------

class FacultyProfiler:
    """
    Benchmark-level two-stage aggregation.

    Usage:
        profiler = FacultyProfiler()

        # Stage 1: group raw VISResult dicts by scenario_id
        aggregates = profiler.aggregate_seeds(vis_results)

        # Stage 2: group ScenarioAggregates by cognitive_track
        profiles = profiler.build_profile(aggregates)

        # Leaderboard float
        score = profiler.benchmark_aggregate(profiles)

        # Full artifact for run artifacts
        artifact = profiler.to_artifact_dict(profiles, aggregates)
    """

    def aggregate_seeds(
        self, vis_results: List[Dict[str, Any]]
    ) -> Dict[str, ScenarioAggregate]:
        """
        Stage 1: group raw VISResult dicts by scenario_id.

        Each VISResult dict must contain:
          - "scenario_id" (str)
          - "track_id" (str)  — cognitive_track
          - "vis" (float)
          - "behavioral_signatures" (dict, optional)
          - "contamination_warning" (bool, optional)

        Returns:
            {scenario_id → ScenarioAggregate}
        """
        by_scenario: Dict[str, List[Dict[str, Any]]] = {}
        for r in vis_results:
            sid = r.get("scenario_id", "")
            if not sid:
                continue
            by_scenario.setdefault(sid, []).append(r)

        aggregates: Dict[str, ScenarioAggregate] = {}
        for sid, runs in by_scenario.items():
            scores = [float(r.get("vis", 0.0)) for r in runs]
            n = len(scores)
            mean = sum(scores) / n

            # Cross-seed variance: 0.0 when n == 1
            if n > 1:
                variance = sum((s - mean) ** 2 for s in scores) / (n - 1)
            else:
                variance = 0.0

            # Aggregate behavioral signatures: mean rate across seeds
            sig_keys: set = set()
            for r in runs:
                sig_keys.update(r.get("behavioral_signatures", {}).keys())
            sig_summary: Dict[str, float] = {}
            for k in sig_keys:
                vals = []
                for r in runs:
                    v = r.get("behavioral_signatures", {}).get(k, 0.0)
                    try:
                        vals.append(float(v))
                    except (TypeError, ValueError):
                        vals.append(0.0)
                sig_summary[k] = sum(vals) / n

            contamination = any(
                r.get("contamination_warning", False) for r in runs
            )

            aggregates[sid] = ScenarioAggregate(
                scenario_id=sid,
                cognitive_track=runs[0].get("track_id", "unknown"),
                mean_vis=round(mean, 4),
                vis_variance=round(variance, 4),
                n_seeds=n,
                behavioral_signatures=sig_summary,
                contamination_warning=contamination,
            )

        return aggregates

    def build_profile(
        self,
        scenario_aggregates: Dict[str, ScenarioAggregate],
        human_baselines: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, FacultyProfile]:
        """
        Stage 2: group ScenarioAggregates by cognitive_track.

        n_scenarios = count of distinct scenario_ids (NOT seed runs).
        CI_95 = mean ± 1.96 × (std / sqrt(n_scenarios))

        Args:
            scenario_aggregates: Output of aggregate_seeds().
            human_baselines:     Optional dict keyed by cognitive_track,
                                 each value a dict with "mean" and "std".

        Returns:
            {cognitive_track → FacultyProfile}
        """
        by_track: Dict[str, List[ScenarioAggregate]] = {}
        for agg in scenario_aggregates.values():
            by_track.setdefault(agg.cognitive_track, []).append(agg)

        profiles: Dict[str, FacultyProfile] = {}
        for track, aggs in by_track.items():
            scores = [a.mean_vis for a in aggs]
            n = len(scores)
            mean = sum(scores) / n

            if n > 1:
                variance = sum((s - mean) ** 2 for s in scores) / (n - 1)
            else:
                variance = 0.0
            std = sqrt(variance)

            # CI_95 = mean ± 1.96 × (std / sqrt(n))
            if n > 1:
                ci_half = 1.96 * std / sqrt(n)
            else:
                ci_half = float("inf")
            ci = (round(mean - ci_half, 4), round(mean + ci_half, 4))

            # Aggregate behavioral signatures across scenarios
            sig_keys: set = set()
            for a in aggs:
                sig_keys.update(a.behavioral_signatures.keys())
            sig_summary: Dict[str, float] = {}
            for k in sig_keys:
                vals = [float(a.behavioral_signatures.get(k, 0.0)) for a in aggs]
                sig_summary[k] = round(sum(vals) / n, 4)

            # Human percentile
            human_pct: Optional[float] = None
            if human_baselines and track in human_baselines:
                hb = human_baselines[track]
                if "mean" in hb and "std" in hb:
                    from vigil.scoring.vis import VISScorer
                    human_pct = VISScorer._compute_percentile(
                        mean, hb["mean"], hb["std"]
                    )

            profiles[track] = FacultyProfile(
                faculty=track,
                mean_vis=round(mean, 4),
                vis_variance=round(variance, 4),
                vis_std=round(std, 4),
                n_scenarios=n,
                confidence_interval_95=ci,
                human_percentile=human_pct,
                behavioral_signature_summary=sig_summary,
                low_sample_warning=(n < 5),
            )

        return profiles

    def benchmark_aggregate(
        self, profiles: Dict[str, FacultyProfile]
    ) -> float:
        """
        Overall benchmark float = mean of per-track mean_vis.

        NOT a raw mean of all VISResult scores — each faculty contributes
        equally regardless of how many scenarios it has.

        Property 14: benchmark_aggregate(profiles) = mean({p.mean_vis})
        """
        if not profiles:
            return 0.0
        return round(sum(p.mean_vis for p in profiles.values()) / len(profiles), 4)

    def to_radar_chart_data(
        self, profiles: Dict[str, FacultyProfile]
    ) -> Dict[str, float]:
        """Return {cognitive_track: mean_vis} for radar chart visualization."""
        return {track: p.mean_vis for track, p in profiles.items()}

    def to_artifact_dict(
        self,
        profiles: Dict[str, FacultyProfile],
        scenario_aggregates: Dict[str, ScenarioAggregate],
    ) -> Dict[str, Any]:
        """
        Produce the full benchmark artifact dict for storage in run artifacts.

        Includes all fields required by Req 21:
          - contamination_warning_rate per track
          - n_seeds_per_scenario per track
          - repeatability_summary across all scenarios
          - confidence_interval_95 per track
          - behavioral_signature_summary per track
          - radar_chart_data for visualization

        Returns:
            Dict suitable for kbench.artifacts.log("vigil_cognitive_profile", ...)
        """
        # Per-track artifact entries
        track_artifacts: Dict[str, Any] = {}
        for track, profile in profiles.items():
            track_aggs = [
                a for a in scenario_aggregates.values()
                if a.cognitive_track == track
            ]
            contamination_rate = (
                sum(1 for a in track_aggs if a.contamination_warning)
                / max(len(track_aggs), 1)
            )
            seeds_per_scenario = [a.n_seeds for a in track_aggs]
            track_artifacts[track] = {
                "mean_vis": profile.mean_vis,
                "vis_std": profile.vis_std,
                "confidence_interval_95": list(profile.confidence_interval_95),
                "n_scenarios": profile.n_scenarios,
                "n_seeds_per_scenario": seeds_per_scenario,
                "contamination_warning_rate": round(contamination_rate, 4),
                "human_percentile": profile.human_percentile,
                "behavioral_signature_summary": profile.behavioral_signature_summary,
                "low_sample_warning": profile.low_sample_warning,
            }

        # Repeatability summary across all scenarios
        repeated = [
            a.vis_variance
            for a in scenario_aggregates.values()
            if a.n_seeds > 1
        ]
        repeatability_summary = {
            "n_repeated_scenarios": len(repeated),
            "mean_cross_seed_variance": round(
                sum(repeated) / max(len(repeated), 1), 4
            ),
            "max_cross_seed_variance": round(
                max(repeated) if repeated else 0.0, 4
            ),
        }

        return {
            "benchmark_aggregate": self.benchmark_aggregate(profiles),
            "cognitive_profile": {
                t: asdict(p) for t, p in profiles.items()
            },
            "track_artifacts": track_artifacts,
            "repeatability_summary": repeatability_summary,
            "radar_chart_data": self.to_radar_chart_data(profiles),
        }
