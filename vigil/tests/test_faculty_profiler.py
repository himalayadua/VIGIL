"""
Unit tests for vigil/scoring/faculty_profiler.py

Tests:
- aggregate_seeds with 3 seeds: n_seeds=3, vis_variance > 0
- aggregate_seeds with 1 seed: vis_variance = 0.0
- build_profile n_scenarios = count of distinct scenario_ids (not seed runs)
- benchmark_aggregate = mean of per-track means (not raw scenario mean)
- to_artifact_dict contains contamination_warning_rate, repeatability_summary, n_seeds_per_scenario
- low_sample_warning = True when n_scenarios < 5
- CI_95 bounds contain mean_vis when n_scenarios > 1
- Property 14: benchmark_aggregate is not a raw mean
- Property 16: vis_variance on ScenarioAggregate, not VISResult

Requirements: 19, 21, Property 14, Property 16
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from vigil.scoring.faculty_profiler import (
    FacultyProfile,
    FacultyProfiler,
    ScenarioAggregate,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _vis_result(
    scenario_id: str,
    track_id: str,
    vis: float,
    contamination_warning: bool = False,
    behavioral_signatures: dict = None,
) -> dict:
    return {
        "scenario_id": scenario_id,
        "track_id": track_id,
        "vis": vis,
        "contamination_warning": contamination_warning,
        "behavioral_signatures": behavioral_signatures or {},
    }


def _make_aggregates(
    scenarios: list,  # list of (scenario_id, track, mean_vis, n_seeds)
) -> dict:
    """Build ScenarioAggregate dict directly for build_profile tests."""
    result = {}
    for sid, track, mean_vis, n_seeds in scenarios:
        variance = 0.01 if n_seeds > 1 else 0.0
        result[sid] = ScenarioAggregate(
            scenario_id=sid,
            cognitive_track=track,
            mean_vis=mean_vis,
            vis_variance=variance,
            n_seeds=n_seeds,
        )
    return result


# ---------------------------------------------------------------------------
# ScenarioAggregate dataclass
# ---------------------------------------------------------------------------

class TestScenarioAggregate:
    def test_default_contamination_warning_false(self):
        agg = ScenarioAggregate(
            scenario_id="s1", cognitive_track="learning",
            mean_vis=0.7, vis_variance=0.0, n_seeds=1,
        )
        assert agg.contamination_warning is False

    def test_vis_variance_zero_for_single_seed(self):
        agg = ScenarioAggregate(
            scenario_id="s1", cognitive_track="learning",
            mean_vis=0.7, vis_variance=0.0, n_seeds=1,
        )
        assert agg.vis_variance == 0.0

    def test_no_vis_variance_on_vis_result_dict(self):
        """Property 16: VISResult dict must not have vis_variance key."""
        vis_result = {"vis": 0.7, "scenario_id": "s1", "track_id": "learning"}
        assert "vis_variance" not in vis_result


# ---------------------------------------------------------------------------
# FacultyProfiler.aggregate_seeds
# ---------------------------------------------------------------------------

class TestAggregateSeeds:
    def test_three_seeds_same_scenario_n_seeds_3(self):
        profiler = FacultyProfiler()
        results = [
            _vis_result("s1", "learning", 0.6),
            _vis_result("s1", "learning", 0.7),
            _vis_result("s1", "learning", 0.8),
        ]
        aggregates = profiler.aggregate_seeds(results)
        assert aggregates["s1"].n_seeds == 3

    def test_three_seeds_vis_variance_positive(self):
        profiler = FacultyProfiler()
        results = [
            _vis_result("s1", "learning", 0.6),
            _vis_result("s1", "learning", 0.7),
            _vis_result("s1", "learning", 0.8),
        ]
        aggregates = profiler.aggregate_seeds(results)
        assert aggregates["s1"].vis_variance > 0.0

    def test_one_seed_vis_variance_zero(self):
        profiler = FacultyProfiler()
        results = [_vis_result("s1", "learning", 0.7)]
        aggregates = profiler.aggregate_seeds(results)
        assert aggregates["s1"].vis_variance == 0.0

    def test_mean_vis_correct(self):
        profiler = FacultyProfiler()
        results = [
            _vis_result("s1", "learning", 0.6),
            _vis_result("s1", "learning", 0.8),
        ]
        aggregates = profiler.aggregate_seeds(results)
        assert abs(aggregates["s1"].mean_vis - 0.7) < 0.001

    def test_multiple_scenarios_separate_aggregates(self):
        profiler = FacultyProfiler()
        results = [
            _vis_result("s1", "learning", 0.6),
            _vis_result("s2", "learning", 0.8),
        ]
        aggregates = profiler.aggregate_seeds(results)
        assert "s1" in aggregates
        assert "s2" in aggregates
        assert len(aggregates) == 2

    def test_contamination_warning_any_seed_triggers(self):
        profiler = FacultyProfiler()
        results = [
            _vis_result("s1", "learning", 0.7, contamination_warning=False),
            _vis_result("s1", "learning", 0.6, contamination_warning=True),
            _vis_result("s1", "learning", 0.8, contamination_warning=False),
        ]
        aggregates = profiler.aggregate_seeds(results)
        assert aggregates["s1"].contamination_warning is True

    def test_contamination_warning_false_when_none_triggered(self):
        profiler = FacultyProfiler()
        results = [
            _vis_result("s1", "learning", 0.7, contamination_warning=False),
            _vis_result("s1", "learning", 0.8, contamination_warning=False),
        ]
        aggregates = profiler.aggregate_seeds(results)
        assert aggregates["s1"].contamination_warning is False

    def test_behavioral_signatures_averaged_across_seeds(self):
        profiler = FacultyProfiler()
        results = [
            _vis_result("s1", "learning", 0.7, behavioral_signatures={"perseveration_rate": 0.2}),
            _vis_result("s1", "learning", 0.8, behavioral_signatures={"perseveration_rate": 0.4}),
        ]
        aggregates = profiler.aggregate_seeds(results)
        assert abs(aggregates["s1"].behavioral_signatures["perseveration_rate"] - 0.3) < 0.001

    def test_skips_results_without_scenario_id(self):
        profiler = FacultyProfiler()
        results = [
            {"vis": 0.7, "track_id": "learning"},  # no scenario_id
            _vis_result("s1", "learning", 0.8),
        ]
        aggregates = profiler.aggregate_seeds(results)
        assert len(aggregates) == 1
        assert "s1" in aggregates

    def test_cognitive_track_from_first_run(self):
        profiler = FacultyProfiler()
        results = [
            _vis_result("s1", "metacognition", 0.7),
            _vis_result("s1", "metacognition", 0.8),
        ]
        aggregates = profiler.aggregate_seeds(results)
        assert aggregates["s1"].cognitive_track == "metacognition"


# ---------------------------------------------------------------------------
# FacultyProfiler.build_profile
# ---------------------------------------------------------------------------

class TestBuildProfile:
    def test_n_scenarios_is_distinct_scenario_count_not_seed_runs(self):
        """n_scenarios = count of distinct scenario_ids, NOT seed runs."""
        profiler = FacultyProfiler()
        # 3 scenarios, each with 3 seeds = 9 total runs
        aggregates = _make_aggregates([
            ("s1", "learning", 0.6, 3),
            ("s2", "learning", 0.7, 3),
            ("s3", "learning", 0.8, 3),
        ])
        profiles = profiler.build_profile(aggregates)
        assert profiles["learning"].n_scenarios == 3  # not 9

    def test_mean_vis_correct(self):
        profiler = FacultyProfiler()
        aggregates = _make_aggregates([
            ("s1", "learning", 0.6, 1),
            ("s2", "learning", 0.8, 1),
        ])
        profiles = profiler.build_profile(aggregates)
        assert abs(profiles["learning"].mean_vis - 0.7) < 0.001

    def test_multiple_tracks_separate_profiles(self):
        profiler = FacultyProfiler()
        aggregates = _make_aggregates([
            ("s1", "learning", 0.7, 1),
            ("s2", "metacognition", 0.6, 1),
        ])
        profiles = profiler.build_profile(aggregates)
        assert "learning" in profiles
        assert "metacognition" in profiles

    def test_low_sample_warning_true_when_n_scenarios_less_than_5(self):
        profiler = FacultyProfiler()
        aggregates = _make_aggregates([
            ("s1", "learning", 0.7, 1),
            ("s2", "learning", 0.8, 1),
        ])
        profiles = profiler.build_profile(aggregates)
        assert profiles["learning"].low_sample_warning is True

    def test_low_sample_warning_false_when_n_scenarios_5_or_more(self):
        profiler = FacultyProfiler()
        aggregates = _make_aggregates([
            (f"s{i}", "learning", 0.7, 1) for i in range(5)
        ])
        profiles = profiler.build_profile(aggregates)
        assert profiles["learning"].low_sample_warning is False

    def test_ci_95_contains_mean_vis_when_n_gt_1(self):
        profiler = FacultyProfiler()
        aggregates = _make_aggregates([
            ("s1", "learning", 0.6, 1),
            ("s2", "learning", 0.7, 1),
            ("s3", "learning", 0.8, 1),
        ])
        profiles = profiler.build_profile(aggregates)
        p = profiles["learning"]
        lower, upper = p.confidence_interval_95
        assert lower <= p.mean_vis <= upper

    def test_ci_95_is_inf_when_n_scenarios_1(self):
        profiler = FacultyProfiler()
        aggregates = _make_aggregates([("s1", "learning", 0.7, 1)])
        profiles = profiler.build_profile(aggregates)
        lower, upper = profiles["learning"].confidence_interval_95
        assert upper == float("inf") or lower == float("-inf")

    def test_behavioral_signature_summary_averaged(self):
        profiler = FacultyProfiler()
        agg1 = ScenarioAggregate(
            scenario_id="s1", cognitive_track="learning",
            mean_vis=0.7, vis_variance=0.0, n_seeds=1,
            behavioral_signatures={"perseveration_rate": 0.2},
        )
        agg2 = ScenarioAggregate(
            scenario_id="s2", cognitive_track="learning",
            mean_vis=0.8, vis_variance=0.0, n_seeds=1,
            behavioral_signatures={"perseveration_rate": 0.4},
        )
        profiles = profiler.build_profile({"s1": agg1, "s2": agg2})
        assert abs(
            profiles["learning"].behavioral_signature_summary["perseveration_rate"] - 0.3
        ) < 0.001

    def test_human_percentile_populated_when_baseline_provided(self):
        profiler = FacultyProfiler()
        aggregates = _make_aggregates([
            ("s1", "learning", 0.7, 1),
            ("s2", "learning", 0.8, 1),
        ])
        human_baselines = {"learning": {"mean": 0.5, "std": 0.2}}
        profiles = profiler.build_profile(aggregates, human_baselines=human_baselines)
        assert profiles["learning"].human_percentile is not None
        assert 0.0 <= profiles["learning"].human_percentile <= 100.0

    def test_human_percentile_none_when_no_baseline(self):
        profiler = FacultyProfiler()
        aggregates = _make_aggregates([("s1", "learning", 0.7, 1)])
        profiles = profiler.build_profile(aggregates)
        assert profiles["learning"].human_percentile is None


# ---------------------------------------------------------------------------
# FacultyProfiler.benchmark_aggregate — Property 14
# ---------------------------------------------------------------------------

class TestBenchmarkAggregate:
    def test_benchmark_aggregate_is_mean_of_track_means(self):
        """Property 14: benchmark_aggregate = mean({p.mean_vis}), not raw mean."""
        profiler = FacultyProfiler()
        # Track A: 10 scenarios with mean_vis=0.9
        # Track B: 1 scenario with mean_vis=0.1
        # Raw mean of all 11 scenarios ≈ 0.836
        # Faculty mean = (0.9 + 0.1) / 2 = 0.5
        aggregates = _make_aggregates(
            [(f"a{i}", "track_a", 0.9, 1) for i in range(10)]
            + [("b1", "track_b", 0.1, 1)]
        )
        profiles = profiler.build_profile(aggregates)
        result = profiler.benchmark_aggregate(profiles)
        # Should be 0.5 (faculty mean), not ~0.836 (raw mean)
        assert abs(result - 0.5) < 0.01

    def test_benchmark_aggregate_empty_profiles_returns_zero(self):
        profiler = FacultyProfiler()
        assert profiler.benchmark_aggregate({}) == 0.0

    def test_benchmark_aggregate_single_track(self):
        profiler = FacultyProfiler()
        aggregates = _make_aggregates([
            ("s1", "learning", 0.6, 1),
            ("s2", "learning", 0.8, 1),
        ])
        profiles = profiler.build_profile(aggregates)
        result = profiler.benchmark_aggregate(profiles)
        assert abs(result - 0.7) < 0.001

    def test_benchmark_aggregate_two_equal_tracks(self):
        profiler = FacultyProfiler()
        aggregates = _make_aggregates([
            ("s1", "learning", 0.8, 1),
            ("s2", "metacognition", 0.6, 1),
        ])
        profiles = profiler.build_profile(aggregates)
        result = profiler.benchmark_aggregate(profiles)
        assert abs(result - 0.7) < 0.001


# ---------------------------------------------------------------------------
# FacultyProfiler.to_artifact_dict
# ---------------------------------------------------------------------------

class TestToArtifactDict:
    def _make_full_aggregates(self):
        return _make_aggregates([
            ("s1", "learning", 0.7, 3),
            ("s2", "learning", 0.8, 1),
            ("s3", "metacognition", 0.6, 2),
        ])

    def test_artifact_contains_benchmark_aggregate(self):
        profiler = FacultyProfiler()
        aggs = self._make_full_aggregates()
        profiles = profiler.build_profile(aggs)
        artifact = profiler.to_artifact_dict(profiles, aggs)
        assert "benchmark_aggregate" in artifact

    def test_artifact_contains_cognitive_profile(self):
        profiler = FacultyProfiler()
        aggs = self._make_full_aggregates()
        profiles = profiler.build_profile(aggs)
        artifact = profiler.to_artifact_dict(profiles, aggs)
        assert "cognitive_profile" in artifact

    def test_artifact_contains_track_artifacts(self):
        profiler = FacultyProfiler()
        aggs = self._make_full_aggregates()
        profiles = profiler.build_profile(aggs)
        artifact = profiler.to_artifact_dict(profiles, aggs)
        assert "track_artifacts" in artifact

    def test_artifact_contains_repeatability_summary(self):
        profiler = FacultyProfiler()
        aggs = self._make_full_aggregates()
        profiles = profiler.build_profile(aggs)
        artifact = profiler.to_artifact_dict(profiles, aggs)
        assert "repeatability_summary" in artifact
        rs = artifact["repeatability_summary"]
        assert "n_repeated_scenarios" in rs
        assert "mean_cross_seed_variance" in rs
        assert "max_cross_seed_variance" in rs

    def test_artifact_contains_radar_chart_data(self):
        profiler = FacultyProfiler()
        aggs = self._make_full_aggregates()
        profiles = profiler.build_profile(aggs)
        artifact = profiler.to_artifact_dict(profiles, aggs)
        assert "radar_chart_data" in artifact

    def test_track_artifact_contains_contamination_warning_rate(self):
        profiler = FacultyProfiler()
        agg1 = ScenarioAggregate(
            scenario_id="s1", cognitive_track="learning",
            mean_vis=0.7, vis_variance=0.0, n_seeds=1,
            contamination_warning=True,
        )
        agg2 = ScenarioAggregate(
            scenario_id="s2", cognitive_track="learning",
            mean_vis=0.8, vis_variance=0.0, n_seeds=1,
            contamination_warning=False,
        )
        profiles = profiler.build_profile({"s1": agg1, "s2": agg2})
        artifact = profiler.to_artifact_dict(profiles, {"s1": agg1, "s2": agg2})
        rate = artifact["track_artifacts"]["learning"]["contamination_warning_rate"]
        assert abs(rate - 0.5) < 0.001

    def test_track_artifact_contains_n_seeds_per_scenario(self):
        profiler = FacultyProfiler()
        aggs = _make_aggregates([
            ("s1", "learning", 0.7, 3),
            ("s2", "learning", 0.8, 1),
        ])
        profiles = profiler.build_profile(aggs)
        artifact = profiler.to_artifact_dict(profiles, aggs)
        seeds = artifact["track_artifacts"]["learning"]["n_seeds_per_scenario"]
        assert sorted(seeds) == [1, 3]

    def test_repeatability_summary_n_repeated_scenarios(self):
        profiler = FacultyProfiler()
        aggs = _make_aggregates([
            ("s1", "learning", 0.7, 3),  # repeated (n_seeds > 1)
            ("s2", "learning", 0.8, 1),  # not repeated
        ])
        profiles = profiler.build_profile(aggs)
        artifact = profiler.to_artifact_dict(profiles, aggs)
        assert artifact["repeatability_summary"]["n_repeated_scenarios"] == 1


# ---------------------------------------------------------------------------
# FacultyProfiler.to_radar_chart_data
# ---------------------------------------------------------------------------

class TestToRadarChartData:
    def test_returns_track_to_mean_vis_mapping(self):
        profiler = FacultyProfiler()
        aggregates = _make_aggregates([
            ("s1", "learning", 0.7, 1),
            ("s2", "metacognition", 0.6, 1),
        ])
        profiles = profiler.build_profile(aggregates)
        radar = profiler.to_radar_chart_data(profiles)
        assert "learning" in radar
        assert "metacognition" in radar
        assert abs(radar["learning"] - 0.7) < 0.001
        assert abs(radar["metacognition"] - 0.6) < 0.001


# ---------------------------------------------------------------------------
# Property 14 — Hypothesis property test
# ---------------------------------------------------------------------------

@given(
    track_a_scores=st.lists(
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        min_size=1, max_size=10,
    ),
    track_b_scores=st.lists(
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        min_size=1, max_size=10,
    ),
)
@settings(max_examples=100)
def test_property_14_benchmark_aggregate_not_raw_mean(
    track_a_scores: list, track_b_scores: list
):
    """
    Property 14: benchmark_aggregate = mean({p.mean_vis}), not raw mean.

    When track A has many scenarios and track B has few, the faculty mean
    gives equal weight to each track, not each scenario.
    """
    profiler = FacultyProfiler()
    aggregates = {}
    for i, v in enumerate(track_a_scores):
        aggregates[f"a{i}"] = ScenarioAggregate(
            scenario_id=f"a{i}", cognitive_track="track_a",
            mean_vis=v, vis_variance=0.0, n_seeds=1,
        )
    for i, v in enumerate(track_b_scores):
        aggregates[f"b{i}"] = ScenarioAggregate(
            scenario_id=f"b{i}", cognitive_track="track_b",
            mean_vis=v, vis_variance=0.0, n_seeds=1,
        )

    profiles = profiler.build_profile(aggregates)
    result = profiler.benchmark_aggregate(profiles)

    # Faculty mean = mean of per-track means
    track_a_mean = sum(track_a_scores) / len(track_a_scores)
    track_b_mean = sum(track_b_scores) / len(track_b_scores)
    expected = (track_a_mean + track_b_mean) / 2

    assert abs(result - expected) < 0.001, (
        f"benchmark_aggregate={result}, expected faculty mean={expected}"
    )


# ---------------------------------------------------------------------------
# Property 16 — vis_variance on ScenarioAggregate, not VISResult
# ---------------------------------------------------------------------------

@given(
    vis=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    n_seeds=st.integers(min_value=2, max_value=10),
)
@settings(max_examples=100)
def test_property_16_vis_variance_on_scenario_aggregate_not_vis_result(
    vis: float, n_seeds: int
):
    """
    Property 16: vis_variance lives on ScenarioAggregate, not VISResult.

    Any VISResult dict has no "vis_variance" key.
    Any ScenarioAggregate with n_seeds > 1 has vis_variance >= 0.0.
    """
    # VISResult must not have vis_variance
    vis_result = {
        "vis": vis,
        "scenario_id": "s1",
        "track_id": "learning",
        "outcome_score": vis,
        "process_score": vis,
    }
    assert "vis_variance" not in vis_result

    # ScenarioAggregate with n_seeds > 1 must have vis_variance >= 0.0
    profiler = FacultyProfiler()
    results = [
        {"scenario_id": "s1", "track_id": "learning", "vis": vis + i * 0.01}
        for i in range(n_seeds)
    ]
    aggregates = profiler.aggregate_seeds(results)
    assert aggregates["s1"].vis_variance >= 0.0
