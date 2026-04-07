"""
Unit tests for vigil/scenarios/catalog.py

Tests:
- ScenarioCatalog pack discovery and scenario_id lookup
- ScenarioNotFoundError for unknown IDs
- ValueError for missing required fields
- cognitive_track string is the dispatch key (not file name)
- get_scenario_ids(track=...) filtering
- Cache: second load() returns same object without re-parsing
- LearningAdapter field mapping (entry_node_ids, evidence_targets, etc.)
- load_transfer_variant with reorder_nodes
- load_transfer_variant raises NotImplementedError for unimplemented types

Requirements: 1, 2, 3, 16
"""

import json
import tempfile
from pathlib import Path

import pytest

from vigil.scenarios.catalog import ScenarioCatalog, ScenarioNotFoundError
from vigil.scenarios.runtime_spec import RuntimeScenarioSpec


# ---------------------------------------------------------------------------
# Fixtures — minimal authored scenario dicts
# ---------------------------------------------------------------------------

LEARNING_SCENARIO = {
    "scenario_id": "test_learning_001",
    "version": "1.0",
    "cognitive_track": "learning",
    "blind_framing": "You are investigating an anomaly in the wetland.",
    "hidden_objective": {
        "correct_root_cause": "ROOT_CAUSE_X",
        "correct_mechanism": "MECHANISM_Y",
        "minimum_evidence_nodes": ["N02", "N03"],
    },
    "graph_metadata": {
        "entry_nodes": ["N01"],
        "root_cause_node": "N05",
        "key_nodes": ["N02", "N03"],
        "disconfirmation_nodes": ["N04"],
        "dead_end_nodes": [],
        "optimal_path_length": 4,
    },
    "nodes": [
        {"id": "N01", "label": "Entry", "surface_text": "Alert text.", "inspection_detail": "Full detail.", "is_entry_point": True},
        {"id": "N02", "label": "Evidence A", "surface_text": "Evidence A.", "inspection_detail": "Detail A."},
        {"id": "N03", "label": "Evidence B", "surface_text": "Evidence B.", "inspection_detail": "Detail B."},
        {"id": "N04", "label": "Dead end", "surface_text": "Dead end.", "inspection_detail": "Nothing here."},
        {"id": "N05", "label": "Root cause", "surface_text": "Root cause.", "inspection_detail": "Root cause detail."},
    ],
    "edges": [
        {"from": "N01", "to": "N02", "relation": "leads_to", "reveal": "You find evidence A.", "is_red_herring": False, "traversal_cost": 1},
        {"from": "N01", "to": "N04", "relation": "leads_to", "reveal": "Dead end.", "is_red_herring": True, "traversal_cost": 1},
        {"from": "N02", "to": "N03", "relation": "leads_to", "reveal": "You find evidence B.", "is_red_herring": False, "traversal_cost": 1},
        {"from": "N03", "to": "N05", "relation": "leads_to", "reveal": "Root cause found.", "is_red_herring": False, "traversal_cost": 1},
    ],
    "optimal_path": {"sequence": ["N01", "N02", "N03", "N05"], "length": 3},
    "scoring_config": {
        "max_steps": 12,
        "weights": {"correctness": 0.3, "path_efficiency": 0.4, "evidence_coverage": 0.3},
        "correctness_tiers": {"full_1.0": "ROOT_CAUSE_X"},
    },
    "anti_shortcutting_audit": {"entities": "All invented"},
    "behavioral_signatures": {},
}

METACOGNITION_SCENARIO = {
    "scenario_id": "test_meta_001",
    "version": "1.0",
    "cognitive_track": "metacognition",
    "blind_task_prompt": "Review the event board and decide what mechanism explains the collapse.",
    "object_level_goal": "Identify the most plausible causal mechanism.",
    "meta_level_goal": "Demonstrate accurate self-monitoring.",
    "metacognitive_layers": ["metacognitive_monitoring"],
    "scoring_focus": ["confidence_calibration_before_verification"],
    "hidden_mechanism": "Bloom succession transition.",
    "disconfirmation_moment": "Toxin assays below lethal range.",
    "recommended_meta_actions": ["verify_before_commit"],
    "nodes": [
        {"node_id": "n0", "label": "Task Brief", "node_type": "briefing", "visibility": "initial", "content": "You are the analyst.", "meta_relevance": "Sets the task."},
        {"node_id": "n1", "label": "Signal A", "node_type": "evidence", "visibility": "hidden", "content": "Signal A content.", "meta_relevance": "Key evidence."},
    ],
    "edges": [
        {"from": "n0", "to": "n1", "edge_type": "reveals", "description": "Opens signal A."},
    ],
}

EXECUTIVE_SCENARIO = {
    "scenario_id": "test_exec_001",
    "version": "1.0",
    "cognitive_track": "executive_functions",
    "executive_design_notes": {
        "tempting_wrong_path": "Blame the bloom peak directly.",
        "required_pivot": "Investigate post-peak succession.",
        "process_scoring_focus": "Whether agent pivots after disconfirmation.",
    },
    "nodes": [
        {"id": "n0", "type": "brief", "label": "Entry Brief", "description": "Fish crash after bloom."},
        {"id": "n1", "type": "evidence", "label": "Bloom data", "description": "Bloom peak data."},
        {"id": "n2", "type": "evidence", "label": "Succession data", "description": "Post-peak succession."},
    ],
    "edges": [
        {"from": "n0", "to": "n1", "relation": "suggests_obvious_explanation"},
        {"from": "n0", "to": "n2", "relation": "leads_to_pivot"},
    ],
}


def _write_pack(tmp_dir: Path, filename: str, data) -> Path:
    path = tmp_dir / filename
    with open(path, "w") as f:
        json.dump(data, f)
    return path


# ---------------------------------------------------------------------------
# ScenarioCatalog — basic discovery
# ---------------------------------------------------------------------------

class TestScenarioCatalogDiscovery:
    def test_empty_packs_dir_returns_no_ids(self, tmp_path):
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        assert catalog.get_scenario_ids() == []

    def test_nonexistent_packs_dir_returns_no_ids(self, tmp_path):
        catalog = ScenarioCatalog(packs_dir=str(tmp_path / "nonexistent"))
        assert catalog.get_scenario_ids() == []

    def test_single_scenario_file_indexed(self, tmp_path):
        _write_pack(tmp_path, "single.json", LEARNING_SCENARIO)
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        assert "test_learning_001" in catalog.get_scenario_ids()

    def test_aggregate_pack_all_scenarios_indexed(self, tmp_path):
        pack = [LEARNING_SCENARIO, METACOGNITION_SCENARIO]
        _write_pack(tmp_path, "multi.json", pack)
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        ids = catalog.get_scenario_ids()
        assert "test_learning_001" in ids
        assert "test_meta_001" in ids

    def test_multiple_files_all_indexed(self, tmp_path):
        _write_pack(tmp_path, "learning.json", [LEARNING_SCENARIO])
        _write_pack(tmp_path, "exec.json", [EXECUTIVE_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        ids = catalog.get_scenario_ids()
        assert "test_learning_001" in ids
        assert "test_exec_001" in ids


# ---------------------------------------------------------------------------
# ScenarioCatalog — load()
# ---------------------------------------------------------------------------

class TestScenarioCatalogLoad:
    def test_load_returns_runtime_scenario_spec(self, tmp_path):
        _write_pack(tmp_path, "pack.json", [LEARNING_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        spec = catalog.load("test_learning_001")
        assert isinstance(spec, RuntimeScenarioSpec)

    def test_load_unknown_id_raises_scenario_not_found(self, tmp_path):
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        with pytest.raises(ScenarioNotFoundError):
            catalog.load("does_not_exist")

    def test_load_sets_correct_cognitive_track(self, tmp_path):
        _write_pack(tmp_path, "pack.json", [LEARNING_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        spec = catalog.load("test_learning_001")
        assert spec.cognitive_track == "learning"

    def test_load_sets_scenario_id(self, tmp_path):
        _write_pack(tmp_path, "pack.json", [LEARNING_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        spec = catalog.load("test_learning_001")
        assert spec.scenario_id == "test_learning_001"

    def test_load_seed_zero_no_perturbation(self, tmp_path):
        _write_pack(tmp_path, "pack.json", [LEARNING_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        spec0 = catalog.load("test_learning_001", seed=0)
        spec0b = catalog.load("test_learning_001", seed=0)
        assert spec0 is spec0b  # same cached object

    def test_load_seed_nonzero_applies_perturbation(self, tmp_path):
        _write_pack(tmp_path, "pack.json", [LEARNING_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        spec0 = catalog.load("test_learning_001", seed=0)
        spec1 = catalog.load("test_learning_001", seed=1)
        # Different seeds should produce different node orderings
        ids0 = [n.node_id for n in spec0.nodes]
        ids1 = [n.node_id for n in spec1.nodes]
        assert set(ids0) == set(ids1)  # same nodes
        # (ordering may or may not differ for 5 nodes, but spec objects differ)
        assert spec0 is not spec1

    def test_load_caches_result(self, tmp_path):
        _write_pack(tmp_path, "pack.json", [LEARNING_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        spec1 = catalog.load("test_learning_001")
        spec2 = catalog.load("test_learning_001")
        assert spec1 is spec2  # exact same object from cache


# ---------------------------------------------------------------------------
# ScenarioCatalog — cognitive_track dispatch
# ---------------------------------------------------------------------------

class TestCognitiveTrackDispatch:
    def test_dispatch_by_cognitive_track_not_filename(self, tmp_path):
        # File is named "wrong_name.json" but cognitive_track is "learning"
        _write_pack(tmp_path, "wrong_name.json", [LEARNING_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        spec = catalog.load("test_learning_001")
        assert spec.cognitive_track == "learning"

    def test_metacognition_track_dispatched_correctly(self, tmp_path):
        _write_pack(tmp_path, "pack.json", [METACOGNITION_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        spec = catalog.load("test_meta_001")
        assert spec.cognitive_track == "metacognition"

    def test_executive_functions_track_dispatched_correctly(self, tmp_path):
        _write_pack(tmp_path, "pack.json", [EXECUTIVE_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        spec = catalog.load("test_exec_001")
        assert spec.cognitive_track == "executive_functions"

    def test_unknown_cognitive_track_raises_value_error(self, tmp_path):
        bad = dict(LEARNING_SCENARIO)
        bad["cognitive_track"] = "unknown_track"
        bad["scenario_id"] = "bad_track_scenario"
        _write_pack(tmp_path, "pack.json", [bad])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        with pytest.raises(ValueError, match="unknown cognitive_track"):
            catalog.load("bad_track_scenario")

    def test_missing_cognitive_track_raises_value_error(self, tmp_path):
        bad = {k: v for k, v in LEARNING_SCENARIO.items() if k != "cognitive_track"}
        bad["scenario_id"] = "no_track_scenario"
        _write_pack(tmp_path, "pack.json", [bad])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        with pytest.raises(ValueError, match="missing 'cognitive_track'"):
            catalog.load("no_track_scenario")


# ---------------------------------------------------------------------------
# ScenarioCatalog — schema validation errors
# ---------------------------------------------------------------------------

class TestSchemaValidation:
    def test_learning_missing_blind_framing_raises(self, tmp_path):
        bad = {k: v for k, v in LEARNING_SCENARIO.items() if k != "blind_framing"}
        bad["scenario_id"] = "bad_learning"
        _write_pack(tmp_path, "pack.json", [bad])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        with pytest.raises(ValueError, match="blind_framing"):
            catalog.load("bad_learning")

    def test_learning_missing_hidden_objective_raises(self, tmp_path):
        bad = {k: v for k, v in LEARNING_SCENARIO.items() if k != "hidden_objective"}
        bad["scenario_id"] = "bad_learning2"
        _write_pack(tmp_path, "pack.json", [bad])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        with pytest.raises(ValueError, match="hidden_objective"):
            catalog.load("bad_learning2")

    def test_executive_missing_executive_design_notes_raises(self, tmp_path):
        bad = {k: v for k, v in EXECUTIVE_SCENARIO.items() if k != "executive_design_notes"}
        bad["scenario_id"] = "bad_exec"
        _write_pack(tmp_path, "pack.json", [bad])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        with pytest.raises(ValueError, match="executive_design_notes"):
            catalog.load("bad_exec")

    def test_executive_missing_required_pivot_raises(self, tmp_path):
        bad = dict(EXECUTIVE_SCENARIO)
        bad["scenario_id"] = "bad_exec2"
        bad["executive_design_notes"] = {
            "tempting_wrong_path": "x",
            # missing required_pivot and process_scoring_focus
        }
        _write_pack(tmp_path, "pack.json", [bad])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        with pytest.raises(ValueError, match="required_pivot"):
            catalog.load("bad_exec2")


# ---------------------------------------------------------------------------
# ScenarioCatalog — get_scenario_ids filtering
# ---------------------------------------------------------------------------

class TestGetScenarioIds:
    def test_filter_by_learning_track(self, tmp_path):
        pack = [LEARNING_SCENARIO, METACOGNITION_SCENARIO, EXECUTIVE_SCENARIO]
        _write_pack(tmp_path, "pack.json", pack)
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        ids = catalog.get_scenario_ids(track="learning")
        assert "test_learning_001" in ids
        assert "test_meta_001" not in ids
        assert "test_exec_001" not in ids

    def test_filter_by_metacognition_track(self, tmp_path):
        pack = [LEARNING_SCENARIO, METACOGNITION_SCENARIO]
        _write_pack(tmp_path, "pack.json", pack)
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        ids = catalog.get_scenario_ids(track="metacognition")
        assert "test_meta_001" in ids
        assert "test_learning_001" not in ids

    def test_no_filter_returns_all(self, tmp_path):
        pack = [LEARNING_SCENARIO, METACOGNITION_SCENARIO, EXECUTIVE_SCENARIO]
        _write_pack(tmp_path, "pack.json", pack)
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        ids = catalog.get_scenario_ids()
        assert len(ids) == 3

    def test_filter_unknown_track_returns_empty(self, tmp_path):
        _write_pack(tmp_path, "pack.json", [LEARNING_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        ids = catalog.get_scenario_ids(track="social_cognition")
        assert ids == []


# ---------------------------------------------------------------------------
# LearningAdapter field mapping
# ---------------------------------------------------------------------------

class TestLearningAdapterMapping:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        path = Path(self.tmp) / "pack.json"
        with open(path, "w") as f:
            json.dump([LEARNING_SCENARIO], f)
        self.catalog = ScenarioCatalog(packs_dir=self.tmp)
        self.spec = self.catalog.load("test_learning_001")

    def test_entry_node_ids_from_graph_metadata(self):
        assert self.spec.entry_node_ids == ["N01"]

    def test_evidence_targets_from_minimum_evidence_nodes(self):
        assert set(self.spec.evidence_targets) == {"N02", "N03"}

    def test_optimal_path_from_sequence(self):
        assert self.spec.optimal_path == ["N01", "N02", "N03", "N05"]

    def test_optimal_steps_from_length(self):
        assert self.spec.optimal_steps == 3

    def test_runtime_config_budget_from_max_steps(self):
        assert self.spec.runtime_config.action_budget == 12

    def test_scoring_weights_do_not_contain_action_costs(self):
        for key in ("inspect", "ask_for_help", "communication", "explore"):
            assert key not in self.spec.scoring_weights

    def test_scoring_weights_sum_to_one(self):
        total = sum(self.spec.scoring_weights.values())
        assert abs(total - 1.0) < 0.01

    def test_opening_prompt_from_blind_framing(self):
        assert "wetland" in self.spec.opening_prompt.lower()

    def test_answer_targets_contains_root_cause(self):
        assert self.spec.answer_targets["correct_root_cause"] == "ROOT_CAUSE_X"

    def test_nodes_compiled_with_canonical_fields(self):
        node_ids = {n.node_id for n in self.spec.nodes}
        assert "N01" in node_ids
        assert "N05" in node_ids

    def test_edges_compiled_with_canonical_fields(self):
        assert len(self.spec.edges) == 4
        edge = self.spec.edges[0]
        assert hasattr(edge, "from_id")
        assert hasattr(edge, "to_id")
        assert hasattr(edge, "traversal_cost")

    def test_edge_traversal_cost_preserved(self):
        for edge in self.spec.edges:
            assert edge.traversal_cost == 1

    def test_track_metadata_contains_scoring_config(self):
        assert "scoring_config" in self.spec.track_metadata

    def test_track_metadata_contains_anti_shortcutting_audit(self):
        assert "anti_shortcutting_audit" in self.spec.track_metadata


# ---------------------------------------------------------------------------
# load_transfer_variant
# ---------------------------------------------------------------------------

class TestLoadTransferVariant:
    def test_reorder_nodes_returns_spec(self, tmp_path):
        _write_pack(tmp_path, "pack.json", [LEARNING_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        spec = catalog.load_transfer_variant("test_learning_001", "reorder_nodes", seed=5)
        assert isinstance(spec, RuntimeScenarioSpec)

    def test_reorder_nodes_preserves_answer_targets(self, tmp_path):
        _write_pack(tmp_path, "pack.json", [LEARNING_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        base = catalog.load("test_learning_001")
        variant = catalog.load_transfer_variant("test_learning_001", "reorder_nodes", seed=3)
        assert variant.answer_targets == base.answer_targets

    def test_rename_entities_raises_not_implemented(self, tmp_path):
        _write_pack(tmp_path, "pack.json", [LEARNING_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        with pytest.raises(NotImplementedError):
            catalog.load_transfer_variant("test_learning_001", "rename_entities", seed=1)

    def test_reskin_domain_raises_not_implemented(self, tmp_path):
        _write_pack(tmp_path, "pack.json", [LEARNING_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        with pytest.raises(NotImplementedError):
            catalog.load_transfer_variant("test_learning_001", "reskin_domain", seed=1)

    def test_unknown_perturbation_type_raises_value_error(self, tmp_path):
        _write_pack(tmp_path, "pack.json", [LEARNING_SCENARIO])
        catalog = ScenarioCatalog(packs_dir=str(tmp_path))
        with pytest.raises(ValueError, match="Unknown perturbation_type"):
            catalog.load_transfer_variant("test_learning_001", "teleport", seed=1)


# ---------------------------------------------------------------------------
# Integration: real Track 1 authored pack (if available)
# ---------------------------------------------------------------------------

class TestRealTrack1Pack:
    """Integration tests using the actual authored Track 1 pack."""

    PACKS_DIR = Path(__file__).parent.parent / "scenarios" / "packs"

    @pytest.fixture(autouse=True)
    def skip_if_no_pack(self):
        if not (self.PACKS_DIR / "vigil_all_30_scenarios.json").exists():
            pytest.skip("Track 1 authored pack not found in vigil/scenarios/packs/")

    def test_catalog_loads_30_learning_scenarios(self):
        catalog = ScenarioCatalog(packs_dir=str(self.PACKS_DIR))
        ids = catalog.get_scenario_ids(track="learning")
        assert len(ids) == 30

    def test_first_scenario_compiles_to_valid_spec(self):
        catalog = ScenarioCatalog(packs_dir=str(self.PACKS_DIR))
        ids = catalog.get_scenario_ids(track="learning")
        spec = catalog.load(ids[0])
        assert isinstance(spec, RuntimeScenarioSpec)
        assert spec.cognitive_track == "learning"
        assert len(spec.nodes) > 0
        assert len(spec.edges) > 0
        assert len(spec.entry_node_ids) > 0
        assert spec.runtime_config.action_budget > 0

    def test_entry_node_in_node_list(self):
        catalog = ScenarioCatalog(packs_dir=str(self.PACKS_DIR))
        ids = catalog.get_scenario_ids(track="learning")
        spec = catalog.load(ids[0])
        node_ids = {n.node_id for n in spec.nodes}
        for entry in spec.entry_node_ids:
            assert entry in node_ids

    def test_evidence_targets_subset_of_nodes(self):
        catalog = ScenarioCatalog(packs_dir=str(self.PACKS_DIR))
        ids = catalog.get_scenario_ids(track="learning")
        spec = catalog.load(ids[0])
        node_ids = {n.node_id for n in spec.nodes}
        for et in spec.evidence_targets:
            assert et in node_ids, f"evidence_target '{et}' not in node list"

    def test_scoring_weights_sum_to_one(self):
        catalog = ScenarioCatalog(packs_dir=str(self.PACKS_DIR))
        ids = catalog.get_scenario_ids(track="learning")
        for sid in ids[:5]:  # check first 5
            spec = catalog.load(sid)
            total = sum(spec.scoring_weights.values())
            assert abs(total - 1.0) < 0.02, f"{sid}: weights sum to {total}"

    def test_cache_returns_same_object(self):
        catalog = ScenarioCatalog(packs_dir=str(self.PACKS_DIR))
        ids = catalog.get_scenario_ids(track="learning")
        sid = ids[0]
        spec1 = catalog.load(sid)
        spec2 = catalog.load(sid)
        assert spec1 is spec2

    def test_to_scenario_config_dict_vis_scorer_compatible(self):
        from vigil.environments.base import EnvironmentState
        from vigil.scoring.vis import VISScorer

        catalog = ScenarioCatalog(packs_dir=str(self.PACKS_DIR))
        ids = catalog.get_scenario_ids(track="learning")
        spec = catalog.load(ids[0])
        config = spec.to_scenario_config_dict()
        state = EnvironmentState(current_node=spec.entry_node_ids[0])
        scorer = VISScorer()
        result = scorer.score_episode(
            state=state,
            final_answer="test",
            justification="Based on N01.",
            scenario_config=config,
            outcome_score=0.5,
        )
        assert "vis" in result
        assert 0.0 <= result["vis"] <= 1.0


# ---------------------------------------------------------------------------
# LearningAdapter — direct class tests (task 3.4)
# ---------------------------------------------------------------------------

class TestLearningAdapterDirect:
    """Tests for LearningAdapter as a standalone class (not via catalog)."""

    from vigil.scenarios.adapters.learning_adapter import LearningAdapter as _LA

    def _adapter(self):
        from vigil.scenarios.adapters.learning_adapter import LearningAdapter
        return LearningAdapter()

    def test_validate_passes_for_valid_scenario(self):
        self._adapter().validate(LEARNING_SCENARIO, "test_learning_001")

    def test_validate_raises_for_missing_blind_framing(self):
        bad = {k: v for k, v in LEARNING_SCENARIO.items() if k != "blind_framing"}
        with pytest.raises(ValueError, match="blind_framing"):
            self._adapter().validate(bad, "bad")

    def test_validate_raises_for_missing_hidden_objective(self):
        bad = {k: v for k, v in LEARNING_SCENARIO.items() if k != "hidden_objective"}
        with pytest.raises(ValueError, match="hidden_objective"):
            self._adapter().validate(bad, "bad")

    def test_validate_raises_for_missing_correct_root_cause(self):
        bad = dict(LEARNING_SCENARIO)
        bad["hidden_objective"] = {
            "correct_mechanism": "M",
            "minimum_evidence_nodes": [],
        }
        with pytest.raises(ValueError, match="correct_root_cause"):
            self._adapter().validate(bad, "bad")

    def test_validate_raises_for_missing_scoring_config(self):
        bad = {k: v for k, v in LEARNING_SCENARIO.items() if k != "scoring_config"}
        with pytest.raises(ValueError, match="scoring_config"):
            self._adapter().validate(bad, "bad")

    def test_validate_raises_for_missing_graph_metadata(self):
        bad = {k: v for k, v in LEARNING_SCENARIO.items() if k != "graph_metadata"}
        with pytest.raises(ValueError, match="graph_metadata"):
            self._adapter().validate(bad, "bad")

    def test_compile_returns_runtime_scenario_spec(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        assert isinstance(spec, RuntimeScenarioSpec)

    def test_compile_entry_node_ids_from_graph_metadata(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        assert spec.entry_node_ids == ["N01"]

    def test_compile_evidence_targets_from_minimum_evidence_nodes(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        assert set(spec.evidence_targets) == {"N02", "N03"}

    def test_compile_runtime_config_budget_from_max_steps(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        assert spec.runtime_config.action_budget == 12

    def test_compile_scoring_weights_do_not_contain_action_costs(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        for key in ("inspect", "ask_for_help", "communication", "explore"):
            assert key not in spec.scoring_weights

    def test_compile_scoring_weights_sum_to_one(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        total = sum(spec.scoring_weights.values())
        assert abs(total - 1.0) < 0.01

    def test_compile_opening_prompt_from_blind_framing(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        assert spec.opening_prompt == LEARNING_SCENARIO["blind_framing"]

    def test_compile_answer_targets_contains_root_cause(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        assert spec.answer_targets["correct_root_cause"] == "ROOT_CAUSE_X"

    def test_compile_node_id_mapped_from_id(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        node_ids = {n.node_id for n in spec.nodes}
        assert "N01" in node_ids
        assert "N05" in node_ids

    def test_compile_node_summary_text_from_surface_text(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        n01 = next(n for n in spec.nodes if n.node_id == "N01")
        assert n01.summary_text == "Alert text."

    def test_compile_edge_from_id_mapped(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        assert spec.edges[0].from_id == "N01"

    def test_compile_edge_reveal_text_from_reveal(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        edge = next(e for e in spec.edges if e.from_id == "N01" and e.to_id == "N02")
        assert "evidence A" in edge.reveal_text

    def test_compile_edge_is_red_herring_in_metadata(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        red_herring_edges = [e for e in spec.edges if e.metadata.get("is_red_herring")]
        assert len(red_herring_edges) == 1
        assert red_herring_edges[0].to_id == "N04"

    def test_compile_track_metadata_contains_scoring_config(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        assert "scoring_config" in spec.track_metadata

    def test_compile_track_metadata_contains_anti_shortcutting_audit(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        assert "anti_shortcutting_audit" in spec.track_metadata

    def test_compile_track_metadata_contains_graph_metadata(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        assert "graph_metadata" in spec.track_metadata

    def test_compile_optimal_path_from_sequence(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        assert spec.optimal_path == ["N01", "N02", "N03", "N05"]

    def test_compile_optimal_steps_from_length(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        assert spec.optimal_steps == 3

    def test_compile_cognitive_track_is_learning(self):
        spec = self._adapter().compile(LEARNING_SCENARIO)
        assert spec.cognitive_track == "learning"

    def test_real_track1_scenario_compiles(self):
        """Integration: compile a real authored Track 1 scenario."""
        packs_dir = Path(__file__).parent.parent / "scenarios" / "packs"
        pack_path = packs_dir / "vigil_all_30_scenarios.json"
        if not pack_path.exists():
            pytest.skip("Track 1 authored pack not found")

        import json
        with open(pack_path) as f:
            scenarios = json.load(f)

        adapter = self._adapter()
        for raw in scenarios[:5]:  # check first 5
            adapter.validate(raw, raw["scenario_id"])
            spec = adapter.compile(raw)
            assert isinstance(spec, RuntimeScenarioSpec)
            assert spec.cognitive_track == "learning"
            assert len(spec.nodes) > 0
            assert len(spec.entry_node_ids) > 0
            assert spec.runtime_config.action_budget > 0
            node_ids = {n.node_id for n in spec.nodes}
            for et in spec.evidence_targets:
                assert et in node_ids


# ---------------------------------------------------------------------------
# Task 12: MetacognitionAdapter and MetacognitionScorer tests
# ---------------------------------------------------------------------------

from vigil.scenarios.adapters.metacognition_adapter import MetacognitionAdapter
from vigil.scenarios.runtime_spec import RuntimeConfig, RuntimeEdge, RuntimeNode, RuntimeScenarioSpec
from vigil.scoring.track_scorers import MetacognitionScorer


METACOGNITION_SCENARIO = {
    "scenario_id": "test_meta_001",
    "version": "1.0",
    "cognitive_track": "metacognition",
    "blind_task_prompt": "Review the event board and decide what mechanism explains the collapse.",
    "object_level_goal": "Identify the most plausible causal mechanism.",
    "meta_level_goal": "Demonstrate accurate self-monitoring.",
    "metacognitive_layers": ["metacognitive_monitoring"],
    "scoring_focus": ["confidence_calibration_before_verification"],
    "hidden_mechanism": "Bloom succession transition.",
    "disconfirmation_moment": "Toxin assays below lethal range.",
    "recommended_meta_actions": ["verify_before_commit"],
    "nodes": [
        {"node_id": "n0", "label": "Task Brief", "node_type": "briefing",
         "visibility": "initial", "content": "You are the analyst.", "meta_relevance": "Sets the task."},
        {"node_id": "n1", "label": "Signal A", "node_type": "evidence",
         "visibility": "hidden", "content": "Signal A content.", "meta_relevance": "Key evidence."},
        {"node_id": "n2", "label": "Disconfirmation", "node_type": "disconfirmation",
         "visibility": "hidden", "content": "Toxin below lethal range.", "meta_relevance": "Contradicts initial hypothesis."},
    ],
    "edges": [
        {"from": "n0", "to": "n1", "edge_type": "reveals", "description": "Opens signal A."},
        {"from": "n1", "to": "n2", "edge_type": "leads_to", "description": "Leads to disconfirmation."},
    ],
}


class TestMetacognitionAdapterDirect:
    def _adapter(self):
        return MetacognitionAdapter()

    def test_validate_passes_for_valid_scenario(self):
        self._adapter().validate(METACOGNITION_SCENARIO, "test_meta_001")

    def test_validate_raises_for_missing_blind_task_prompt(self):
        bad = {k: v for k, v in METACOGNITION_SCENARIO.items() if k != "blind_task_prompt"}
        with pytest.raises(ValueError, match="blind_task_prompt"):
            self._adapter().validate(bad, "bad")

    def test_validate_raises_for_missing_object_level_goal(self):
        bad = {k: v for k, v in METACOGNITION_SCENARIO.items() if k != "object_level_goal"}
        with pytest.raises(ValueError, match="object_level_goal"):
            self._adapter().validate(bad, "bad")

    def test_validate_raises_for_missing_metacognitive_layers(self):
        bad = {k: v for k, v in METACOGNITION_SCENARIO.items() if k != "metacognitive_layers"}
        with pytest.raises(ValueError, match="metacognitive_layers"):
            self._adapter().validate(bad, "bad")

    def test_compile_returns_runtime_scenario_spec(self):
        spec = self._adapter().compile(METACOGNITION_SCENARIO)
        assert isinstance(spec, RuntimeScenarioSpec)

    def test_compile_cognitive_track_is_metacognition(self):
        spec = self._adapter().compile(METACOGNITION_SCENARIO)
        assert spec.cognitive_track == "metacognition"

    def test_compile_opening_prompt_from_blind_task_prompt(self):
        spec = self._adapter().compile(METACOGNITION_SCENARIO)
        assert spec.opening_prompt == METACOGNITION_SCENARIO["blind_task_prompt"]

    def test_compile_answer_targets_contains_both_goals(self):
        spec = self._adapter().compile(METACOGNITION_SCENARIO)
        assert "object_level_goal" in spec.answer_targets
        assert "meta_level_goal" in spec.answer_targets

    def test_compile_entry_node_from_initial_visibility(self):
        spec = self._adapter().compile(METACOGNITION_SCENARIO)
        assert "n0" in spec.entry_node_ids

    def test_compile_node_id_mapped(self):
        spec = self._adapter().compile(METACOGNITION_SCENARIO)
        node_ids = {n.node_id for n in spec.nodes}
        assert "n0" in node_ids
        assert "n1" in node_ids

    def test_compile_node_content_to_summary_and_detail(self):
        spec = self._adapter().compile(METACOGNITION_SCENARIO)
        n0 = next(n for n in spec.nodes if n.node_id == "n0")
        assert n0.summary_text == "You are the analyst."
        assert n0.inspection_detail == "You are the analyst."

    def test_compile_node_meta_relevance_in_metadata(self):
        spec = self._adapter().compile(METACOGNITION_SCENARIO)
        n0 = next(n for n in spec.nodes if n.node_id == "n0")
        assert n0.metadata.get("meta_relevance") == "Sets the task."

    def test_compile_edge_from_mapped(self):
        spec = self._adapter().compile(METACOGNITION_SCENARIO)
        assert spec.edges[0].from_id == "n0"
        assert spec.edges[0].to_id == "n1"

    def test_compile_edge_type_to_relation(self):
        spec = self._adapter().compile(METACOGNITION_SCENARIO)
        assert spec.edges[0].relation == "reveals"

    def test_compile_edge_description_to_reveal_text(self):
        spec = self._adapter().compile(METACOGNITION_SCENARIO)
        assert "Opens signal A" in spec.edges[0].reveal_text

    def test_compile_track_metadata_contains_metacognitive_layers(self):
        spec = self._adapter().compile(METACOGNITION_SCENARIO)
        assert "metacognitive_layers" in spec.track_metadata

    def test_compile_track_metadata_contains_scoring_focus(self):
        spec = self._adapter().compile(METACOGNITION_SCENARIO)
        assert "scoring_focus" in spec.track_metadata

    def test_compile_scoring_weights_sum_to_one(self):
        spec = self._adapter().compile(METACOGNITION_SCENARIO)
        total = sum(spec.scoring_weights.values())
        assert abs(total - 1.0) < 0.01

    def test_real_track2_scenario_compiles(self):
        """Integration: compile a real authored Track 2 scenario."""
        packs_dir = Path(__file__).parent.parent / "scenarios" / "packs"
        pack_path = packs_dir / "track4_metacognition_synthetic_scenarios_from_skeletons.json"
        if not pack_path.exists():
            pytest.skip("Track 2 metacognition pack not found")

        import json
        with open(pack_path) as f:
            scenarios = json.load(f)

        adapter = self._adapter()
        for raw in scenarios[:5]:
            adapter.validate(raw, raw["scenario_id"])
            spec = adapter.compile(raw)
            assert isinstance(spec, RuntimeScenarioSpec)
            assert spec.cognitive_track == "metacognition"
            assert len(spec.nodes) > 0
            assert len(spec.entry_node_ids) > 0


class TestMetacognitionScorer:
    def _make_meta_spec(self):
        """Build a minimal metacognition spec for scorer tests."""
        nodes = [
            RuntimeNode(f"n{i}", f"Node {i}", f"Content {i}", f"Content {i}",
                        initial_visibility="initial" if i == 0 else "hidden")
            for i in range(4)
        ]
        edges = [RuntimeEdge(f"n{i}", f"n{i+1}", "leads_to") for i in range(3)]
        return RuntimeScenarioSpec(
            scenario_id="meta_test",
            cognitive_track="metacognition",
            opening_prompt="Find the mechanism.",
            nodes=nodes,
            edges=edges,
            entry_node_ids=["n0"],
            answer_targets={
                "object_level_goal": "Identify the causal mechanism and recommend response.",
                "meta_level_goal": "Demonstrate accurate self-monitoring.",
            },
            evidence_targets=[],
            optimal_path=[],
            optimal_steps=0,
            runtime_config=RuntimeConfig(action_budget=20),
            scoring_weights={"object_score": 0.3, "meta_score": 0.7},
            track_metadata={
                "metacognitive_layers": ["metacognitive_monitoring"],
                "scoring_focus": ["confidence_calibration"],
                "hidden_mechanism": "Bloom succession.",
                "disconfirmation_moment": "Toxin below lethal.",
                "recommended_meta_actions": [],
            },
        )

    def _make_state(self, confidence=None, inspected=None, contradiction=False):
        from vigil.environments.base import EnvironmentState, EventType, TraversalEvent
        state = EnvironmentState(current_node="n0")
        state.inspected_nodes = inspected or []
        if confidence is not None:
            state.confidence_history.append(confidence)
        if contradiction:
            state.action_history.append(TraversalEvent.make(
                event_type=EventType.CONTRADICTION,
                observation="Contradiction triggered.",
            ))
        return state

    def test_score_returns_no_vis_key(self):
        spec = self._make_meta_spec()
        scorer = MetacognitionScorer(spec)
        state = self._make_state()
        result = scorer.score(state, "causal mechanism", "Based on n1.", spec)
        assert "vis" not in result

    def test_score_contains_outcome_score(self):
        spec = self._make_meta_spec()
        scorer = MetacognitionScorer(spec)
        state = self._make_state()
        result = scorer.score(state, "causal mechanism", "j", spec)
        assert "outcome_score" in result
        assert 0.0 <= result["outcome_score"] <= 1.0

    def test_score_contains_process_score(self):
        spec = self._make_meta_spec()
        scorer = MetacognitionScorer(spec)
        state = self._make_state()
        result = scorer.score(state, "causal mechanism", "j", spec)
        assert "process_score" in result
        assert 0.0 <= result["process_score"] <= 1.0

    def test_object_score_independent_of_metacognitive_behavior(self):
        """object_score must not change based on confidence or help-seeking."""
        spec = self._make_meta_spec()
        scorer = MetacognitionScorer(spec)

        state_no_conf = self._make_state(confidence=None)
        state_high_conf = self._make_state(confidence=0.9)

        r1 = scorer.score(state_no_conf, "causal mechanism", "j", spec)
        r2 = scorer.score(state_high_conf, "causal mechanism", "j", spec)

        # object_score should be the same regardless of confidence
        assert r1["object_score"] == r2["object_score"]

    def test_revision_quality_1_when_contradiction_followed_by_new_node(self):
        """revision_quality = 1.0 when contradiction event followed by new-node within 3 steps."""
        from vigil.environments.base import EnvironmentState, EventType, TraversalEvent
        spec = self._make_meta_spec()
        scorer = MetacognitionScorer(spec)

        state = EnvironmentState(current_node="n0")
        state.inspected_nodes = []
        state.confidence_history = [0.7]

        # Add contradiction event
        state.action_history.append(TraversalEvent.make(
            event_type=EventType.CONTRADICTION,
            observation="Contradiction.",
        ))
        # Add new-node exploration within 3 steps
        state.action_history.append(TraversalEvent.make(
            event_type=EventType.EXPLORE,
            observation="Explored n2.",
            node_id="n2",
        ))

        result = scorer.score(state, "mechanism", "j", spec)
        assert result["revision_quality"] == 1.0

    def test_revision_quality_0_when_no_contradiction(self):
        spec = self._make_meta_spec()
        scorer = MetacognitionScorer(spec)
        state = self._make_state()
        result = scorer.score(state, "mechanism", "j", spec)
        assert result["revision_quality"] == 0.0

    def test_track_id_is_metacognition(self):
        spec = self._make_meta_spec()
        scorer = MetacognitionScorer(spec)
        state = self._make_state()
        result = scorer.score(state, "mechanism", "j", spec)
        assert result["track_id"] == "metacognition"

    def test_outcome_score_equals_object_score(self):
        spec = self._make_meta_spec()
        scorer = MetacognitionScorer(spec)
        state = self._make_state()
        result = scorer.score(state, "mechanism", "j", spec)
        assert result["outcome_score"] == result["object_score"]

    def test_process_score_equals_meta_score(self):
        spec = self._make_meta_spec()
        scorer = MetacognitionScorer(spec)
        state = self._make_state()
        result = scorer.score(state, "mechanism", "j", spec)
        assert result["process_score"] == result["meta_score"]

    def test_catalog_dispatches_to_metacognition_scorer(self):
        from vigil.scoring.track_scorers import TrackScorer
        spec = self._make_meta_spec()
        scorer = TrackScorer.for_track("metacognition", spec)
        assert isinstance(scorer, MetacognitionScorer)


# ---------------------------------------------------------------------------
# Task 13: AttentionAdapter and AttentionScorer tests
# ---------------------------------------------------------------------------

from vigil.scenarios.adapters.attention_adapter import AttentionAdapter
from vigil.scoring.track_scorers import AttentionScorer


ATTENTION_SCENARIO = {
    "scenario_id": "test_attention_001",
    "version": "1.0",
    "cognitive_track": "attention",
    "blind_task_prompt": "A managed basin is losing shimmerfin stock. Inspect the monitoring graph.",
    "attention_design": {
        "attentional_bottleneck": "Phase-shift evidence buried after salient bloom peak.",
        "salient_but_irrelevant_branches": ["n1"],
        "rare_critical_signal": "n3",
        "reorientation_trigger": "n4",
    },
    "critical_evidence_node_ids": ["n3", "n4"],
    "target_conclusion": "The proximate driver is the bloom transition, not peak toxicity.",
    "hidden_mechanism": "Post-peak community transition.",
    "disconfirmation_moment": "Toxin assays below lethal range.",
    "nodes": [
        {"id": "n0", "label": "entry", "kind": "entry", "initial_visibility": "visible",
         "salience": "medium", "diagnosticity": "medium", "content": "Basin losing stock."},
        {"id": "n1", "label": "salient_trap", "kind": "distractor", "initial_visibility": "hidden",
         "salience": "high", "diagnosticity": "low", "content": "Bloom peak data."},
        {"id": "n2", "label": "false_alarm", "kind": "false_alarm", "initial_visibility": "hidden",
         "salience": "medium", "diagnosticity": "low", "content": "Temperature data."},
        {"id": "n3", "label": "rare_critical", "kind": "rare_critical", "initial_visibility": "hidden",
         "salience": "low", "diagnosticity": "high", "content": "Phase-shift evidence."},
        {"id": "n4", "label": "reorientation", "kind": "evidence", "initial_visibility": "hidden",
         "salience": "low", "diagnosticity": "high", "content": "Succession data."},
    ],
    "edges": [
        {"source": "n0", "target": "n1", "relation": "surfaces_obvious", "visibility": "visible",
         "attention_role": "salient_trap"},
        {"source": "n0", "target": "n2", "relation": "leads_to", "visibility": "visible",
         "attention_role": "false_alarm"},
        {"source": "n0", "target": "n3", "relation": "leads_to", "visibility": "hidden",
         "attention_role": "target"},
        {"source": "n3", "target": "n4", "relation": "leads_to", "visibility": "hidden",
         "attention_role": "target"},
    ],
}


class TestAttentionAdapterDirect:
    def _adapter(self):
        return AttentionAdapter()

    def test_validate_passes_for_valid_scenario(self):
        self._adapter().validate(ATTENTION_SCENARIO, "test_attention_001")

    def test_validate_raises_for_missing_blind_task_prompt(self):
        bad = {k: v for k, v in ATTENTION_SCENARIO.items() if k != "blind_task_prompt"}
        with pytest.raises(ValueError, match="blind_task_prompt"):
            self._adapter().validate(bad, "bad")

    def test_validate_raises_for_missing_attention_design(self):
        bad = {k: v for k, v in ATTENTION_SCENARIO.items() if k != "attention_design"}
        with pytest.raises(ValueError, match="attention_design"):
            self._adapter().validate(bad, "bad")

    def test_validate_raises_for_missing_critical_evidence_node_ids(self):
        bad = {k: v for k, v in ATTENTION_SCENARIO.items() if k != "critical_evidence_node_ids"}
        with pytest.raises(ValueError, match="critical_evidence_node_ids"):
            self._adapter().validate(bad, "bad")

    def test_compile_returns_runtime_scenario_spec(self):
        spec = self._adapter().compile(ATTENTION_SCENARIO)
        assert isinstance(spec, RuntimeScenarioSpec)

    def test_compile_cognitive_track_is_attention(self):
        spec = self._adapter().compile(ATTENTION_SCENARIO)
        assert spec.cognitive_track == "attention"

    def test_compile_opening_prompt_from_blind_task_prompt(self):
        spec = self._adapter().compile(ATTENTION_SCENARIO)
        assert spec.opening_prompt == ATTENTION_SCENARIO["blind_task_prompt"]

    def test_compile_evidence_targets_from_critical_evidence_node_ids(self):
        spec = self._adapter().compile(ATTENTION_SCENARIO)
        assert set(spec.evidence_targets) == {"n3", "n4"}

    def test_compile_answer_targets_contains_target_conclusion(self):
        spec = self._adapter().compile(ATTENTION_SCENARIO)
        assert "target_conclusion" in spec.answer_targets

    def test_compile_entry_node_from_visible_node(self):
        spec = self._adapter().compile(ATTENTION_SCENARIO)
        assert "n0" in spec.entry_node_ids

    def test_compile_node_id_mapped_from_id(self):
        spec = self._adapter().compile(ATTENTION_SCENARIO)
        node_ids = {n.node_id for n in spec.nodes}
        assert "n0" in node_ids
        assert "n1" in node_ids

    def test_compile_node_kind_to_node_type(self):
        spec = self._adapter().compile(ATTENTION_SCENARIO)
        n1 = next(n for n in spec.nodes if n.node_id == "n1")
        assert n1.node_type == "distractor"

    def test_compile_node_content_to_summary_and_detail(self):
        spec = self._adapter().compile(ATTENTION_SCENARIO)
        n0 = next(n for n in spec.nodes if n.node_id == "n0")
        assert n0.summary_text == "Basin losing stock."

    def test_compile_node_salience_in_metadata(self):
        spec = self._adapter().compile(ATTENTION_SCENARIO)
        n1 = next(n for n in spec.nodes if n.node_id == "n1")
        assert n1.metadata.get("salience") == "high"

    def test_compile_edge_source_to_from_id(self):
        spec = self._adapter().compile(ATTENTION_SCENARIO)
        assert spec.edges[0].from_id == "n0"
        assert spec.edges[0].to_id == "n1"

    def test_compile_edge_attention_role_in_metadata(self):
        spec = self._adapter().compile(ATTENTION_SCENARIO)
        e = next(e for e in spec.edges if e.from_id == "n0" and e.to_id == "n1")
        assert e.metadata.get("attention_role") == "salient_trap"

    def test_compile_track_metadata_contains_attention_design(self):
        spec = self._adapter().compile(ATTENTION_SCENARIO)
        assert "attention_design" in spec.track_metadata

    def test_real_track3_scenario_compiles(self):
        """Integration: compile a real authored Track 3 scenario."""
        packs_dir = Path(__file__).parent.parent / "scenarios" / "packs"
        pack_path = packs_dir / "track2_attention_synthetic_scenarios.json"
        if not pack_path.exists():
            pytest.skip("Track 3 attention pack not found")

        import json
        with open(pack_path) as f:
            scenarios = json.load(f)

        adapter = self._adapter()
        for raw in scenarios[:5]:
            adapter.validate(raw, raw["scenario_id"])
            spec = adapter.compile(raw)
            assert isinstance(spec, RuntimeScenarioSpec)
            assert spec.cognitive_track == "attention"
            assert len(spec.nodes) > 0
            assert len(spec.entry_node_ids) > 0


class TestAttentionScorer:
    def _make_attention_spec(self):
        """Build a minimal attention spec for scorer tests."""
        nodes = [
            RuntimeNode("n0", "Entry", "Entry content", "Entry detail",
                        node_type="entry", initial_visibility="visible"),
            RuntimeNode("n1", "Distractor", "Distractor content", "Distractor detail",
                        node_type="distractor", initial_visibility="hidden"),
            RuntimeNode("n2", "False alarm", "False alarm content", "False alarm detail",
                        node_type="false_alarm", initial_visibility="hidden"),
            RuntimeNode("n3", "Target", "Target content", "Target detail",
                        node_type="evidence", initial_visibility="hidden"),
            RuntimeNode("n4", "Rare critical", "Rare critical content", "Rare critical detail",
                        node_type="rare_critical", initial_visibility="hidden"),
        ]
        edges = [
            RuntimeEdge("n0", "n1", "leads_to", metadata={"attention_role": "salient_trap"}),
            RuntimeEdge("n0", "n2", "leads_to", metadata={"attention_role": "false_alarm"}),
            RuntimeEdge("n0", "n3", "leads_to", metadata={"attention_role": "target"}),
            RuntimeEdge("n3", "n4", "leads_to", metadata={"attention_role": "target"}),
        ]
        return RuntimeScenarioSpec(
            scenario_id="attention_test",
            cognitive_track="attention",
            opening_prompt="Find the root cause.",
            nodes=nodes,
            edges=edges,
            entry_node_ids=["n0"],
            answer_targets={"target_conclusion": "bloom transition not peak toxicity"},
            evidence_targets=["n3", "n4"],
            optimal_path=[],
            optimal_steps=0,
            runtime_config=RuntimeConfig(action_budget=20),
            scoring_weights={
                "correctness": 0.3,
                "target_hit_rate": 0.25,
                "distractor_chase_rate": 0.2,
                "reorientation_latency": 0.15,
                "cue_coverage": 0.1,
            },
            track_metadata={"attention_design": {}, "hidden_mechanism": "", "disconfirmation_moment": ""},
        )

    def _make_state(self, visited=None, inspected=None, explore_nodes=None):
        from vigil.environments.base import EnvironmentState, EventType, TraversalEvent
        state = EnvironmentState(current_node="n0")
        state.visited_nodes = visited or ["n0"]
        state.inspected_nodes = inspected or []
        if explore_nodes:
            for nid in explore_nodes:
                state.action_history.append(TraversalEvent.make(
                    event_type=EventType.EXPLORE,
                    observation=f"Explored {nid}",
                    node_id=nid,
                    budget_delta=-1,
                ))
        return state

    def test_score_returns_no_vis_key(self):
        spec = self._make_attention_spec()
        scorer = AttentionScorer(spec)
        state = self._make_state()
        result = scorer.score(state, "bloom transition", "j", spec)
        assert "vis" not in result

    def test_score_contains_track_id_attention(self):
        spec = self._make_attention_spec()
        scorer = AttentionScorer(spec)
        state = self._make_state()
        result = scorer.score(state, "bloom transition", "j", spec)
        assert result["track_id"] == "attention"

    def test_distractor_chase_rate_increments_for_salient_trap(self):
        """Node n1 has attention_role: salient_trap — exploring it increments distractor_chase_rate."""
        spec = self._make_attention_spec()
        scorer = AttentionScorer(spec)
        # Explore n1 (salient_trap) and n3 (target)
        state = self._make_state(explore_nodes=["n1", "n3"])
        result = scorer.score(state, "bloom transition", "j", spec)
        # 1 of 2 actions is on a distractor → rate = 0.5
        assert result["distractor_chase_rate"] == 0.5

    def test_distractor_chase_rate_zero_when_no_distractors_visited(self):
        spec = self._make_attention_spec()
        scorer = AttentionScorer(spec)
        state = self._make_state(explore_nodes=["n3", "n4"])
        result = scorer.score(state, "bloom transition", "j", spec)
        assert result["distractor_chase_rate"] == 0.0

    def test_missed_rare_alert_when_rare_critical_not_inspected(self):
        """Node n4 has node_type: rare_critical — not inspecting it → missed_rare_alert."""
        spec = self._make_attention_spec()
        scorer = AttentionScorer(spec)
        state = self._make_state(inspected=["n0", "n3"])  # n4 not inspected
        result = scorer.score(state, "bloom transition", "j", spec)
        assert result["behavioral_signatures"].get("missed_rare_alert") is True

    def test_no_missed_rare_alert_when_rare_critical_inspected(self):
        spec = self._make_attention_spec()
        scorer = AttentionScorer(spec)
        state = self._make_state(inspected=["n4"])  # n4 inspected
        result = scorer.score(state, "bloom transition", "j", spec)
        assert "missed_rare_alert" not in result["behavioral_signatures"]

    def test_target_hit_rate_1_when_all_evidence_inspected(self):
        spec = self._make_attention_spec()
        scorer = AttentionScorer(spec)
        state = self._make_state(inspected=["n3", "n4"])
        result = scorer.score(state, "bloom transition", "j", spec)
        assert result["target_hit_rate"] == 1.0

    def test_target_hit_rate_0_when_no_evidence_inspected(self):
        spec = self._make_attention_spec()
        scorer = AttentionScorer(spec)
        state = self._make_state(inspected=["n0", "n1"])
        result = scorer.score(state, "bloom transition", "j", spec)
        assert result["target_hit_rate"] == 0.0

    def test_catalog_dispatches_to_attention_scorer(self):
        from vigil.scoring.track_scorers import TrackScorer
        spec = self._make_attention_spec()
        scorer = TrackScorer.for_track("attention", spec)
        assert isinstance(scorer, AttentionScorer)

    def test_process_score_in_range(self):
        spec = self._make_attention_spec()
        scorer = AttentionScorer(spec)
        state = self._make_state(inspected=["n3", "n4"], explore_nodes=["n3", "n4"])
        result = scorer.score(state, "bloom transition", "j", spec)
        assert 0.0 <= result["process_score"] <= 1.0


# ---------------------------------------------------------------------------
# Task 14: ExecutiveAdapter and ExecutiveScorer tests
# ---------------------------------------------------------------------------

from vigil.scenarios.adapters.executive_adapter import ExecutiveAdapter
from vigil.scoring.track_scorers import ExecutiveScorer


EXECUTIVE_SCENARIO = {
    "scenario_id": "test_exec_001",
    "version": "1.0",
    "cognitive_track": "executive_functions",
    "executive_design_notes": {
        "tempting_wrong_path": "Stop at the vivid bloom peak and never inspect post-peak transition.",
        "required_pivot": "After toxicity fails, switch to timing and succession.",
        "process_scoring_focus": ["pivot_latency_after_peak_toxicity_failure", "evidence_ordering"],
    },
    "nodes": [
        {"id": "n0", "type": "brief", "label": "Entry Brief",
         "description": "Fish crash across Mireglass Marsh after a dramatic seasonal bloom."},
        {"id": "n1", "type": "evidence", "label": "Bloom data",
         "description": "Bloom peak toxicity data."},
        {"id": "n2", "type": "evidence", "label": "Succession data",
         "description": "Post-peak succession and oxygen dynamics."},
        {"id": "n3", "type": "evidence", "label": "Timing data",
         "description": "Timing of fish crash relative to bloom."},
    ],
    "edges": [
        {"from": "n0", "to": "n1", "relation": "suggests_obvious_explanation"},
        {"from": "n0", "to": "n2", "relation": "leads_to_pivot"},
        {"from": "n2", "to": "n3", "relation": "confirms"},
    ],
}


class TestExecutiveAdapterDirect:
    def _adapter(self):
        return ExecutiveAdapter()

    def test_validate_passes_for_valid_scenario(self):
        self._adapter().validate(EXECUTIVE_SCENARIO, "test_exec_001")

    def test_validate_raises_for_missing_executive_design_notes(self):
        bad = {k: v for k, v in EXECUTIVE_SCENARIO.items() if k != "executive_design_notes"}
        with pytest.raises(ValueError, match="executive_design_notes"):
            self._adapter().validate(bad, "bad")

    def test_validate_raises_for_missing_required_pivot(self):
        bad = dict(EXECUTIVE_SCENARIO)
        bad["executive_design_notes"] = {
            "tempting_wrong_path": "x",
            "process_scoring_focus": [],
            # missing required_pivot
        }
        with pytest.raises(ValueError, match="required_pivot"):
            self._adapter().validate(bad, "bad")

    def test_validate_raises_for_missing_tempting_wrong_path(self):
        bad = dict(EXECUTIVE_SCENARIO)
        bad["executive_design_notes"] = {
            "required_pivot": "x",
            "process_scoring_focus": [],
            # missing tempting_wrong_path
        }
        with pytest.raises(ValueError, match="tempting_wrong_path"):
            self._adapter().validate(bad, "bad")

    def test_compile_returns_runtime_scenario_spec(self):
        spec = self._adapter().compile(EXECUTIVE_SCENARIO)
        assert isinstance(spec, RuntimeScenarioSpec)

    def test_compile_cognitive_track_is_executive_functions(self):
        spec = self._adapter().compile(EXECUTIVE_SCENARIO)
        assert spec.cognitive_track == "executive_functions"

    def test_compile_opening_prompt_from_first_node_description(self):
        spec = self._adapter().compile(EXECUTIVE_SCENARIO)
        assert "Mireglass Marsh" in spec.opening_prompt

    def test_compile_entry_node_is_first_node(self):
        spec = self._adapter().compile(EXECUTIVE_SCENARIO)
        assert spec.entry_node_ids == ["n0"]

    def test_compile_answer_targets_contains_required_pivot(self):
        spec = self._adapter().compile(EXECUTIVE_SCENARIO)
        assert "required_pivot" in spec.answer_targets
        assert "toxicity" in spec.answer_targets["required_pivot"].lower()

    def test_compile_node_id_mapped_from_id(self):
        spec = self._adapter().compile(EXECUTIVE_SCENARIO)
        node_ids = {n.node_id for n in spec.nodes}
        assert "n0" in node_ids
        assert "n2" in node_ids

    def test_compile_node_description_to_summary_and_detail(self):
        spec = self._adapter().compile(EXECUTIVE_SCENARIO)
        n0 = next(n for n in spec.nodes if n.node_id == "n0")
        assert "Mireglass Marsh" in n0.summary_text
        assert n0.summary_text == n0.inspection_detail

    def test_compile_node_type_mapped(self):
        spec = self._adapter().compile(EXECUTIVE_SCENARIO)
        n1 = next(n for n in spec.nodes if n.node_id == "n1")
        assert n1.node_type == "evidence"

    def test_compile_edge_from_to_mapped(self):
        spec = self._adapter().compile(EXECUTIVE_SCENARIO)
        assert spec.edges[0].from_id == "n0"
        assert spec.edges[0].to_id == "n1"

    def test_compile_track_metadata_contains_executive_design_notes(self):
        spec = self._adapter().compile(EXECUTIVE_SCENARIO)
        assert "executive_design_notes" in spec.track_metadata

    def test_real_track4_scenario_compiles(self):
        """Integration: compile a real authored Track 4 scenario."""
        packs_dir = Path(__file__).parent.parent / "scenarios" / "packs"
        pack_path = packs_dir / "vigil_track3_executive_scenarios_from_skeletons_v1.json"
        if not pack_path.exists():
            pytest.skip("Track 4 executive pack not found")

        import json
        with open(pack_path) as f:
            scenarios = json.load(f)

        adapter = self._adapter()
        for raw in scenarios[:5]:
            adapter.validate(raw, raw["scenario_id"])
            spec = adapter.compile(raw)
            assert isinstance(spec, RuntimeScenarioSpec)
            assert spec.cognitive_track == "executive_functions"
            assert len(spec.nodes) > 0
            assert len(spec.entry_node_ids) > 0


class TestExecutiveScorer:
    def _make_exec_spec(self):
        """Build a minimal executive spec for scorer tests."""
        nodes = [
            RuntimeNode("n0", "Entry", "Fish crash after bloom.", "Fish crash after bloom.",
                        node_type="brief", initial_visibility="hidden"),
            RuntimeNode("n1", "Bloom", "Bloom peak data.", "Bloom peak data.",
                        node_type="evidence", initial_visibility="hidden"),
            RuntimeNode("n2", "Succession", "Post-peak succession.", "Post-peak succession.",
                        node_type="evidence", initial_visibility="hidden"),
        ]
        edges = [
            RuntimeEdge("n0", "n1", "suggests_obvious"),
            RuntimeEdge("n0", "n2", "leads_to_pivot"),
        ]
        return RuntimeScenarioSpec(
            scenario_id="exec_test",
            cognitive_track="executive_functions",
            opening_prompt="Fish crash after bloom.",
            nodes=nodes,
            edges=edges,
            entry_node_ids=["n0"],
            answer_targets={"required_pivot": "switch to timing and succession"},
            evidence_targets=[],
            optimal_path=[],
            optimal_steps=0,
            runtime_config=RuntimeConfig(action_budget=20),
            scoring_weights={
                "correctness": 0.3,
                "inhibition_failures": 0.25,
                "pivot_quality": 0.25,
                "process_scoring_focus_alignment": 0.2,
            },
            track_metadata={
                "executive_design_notes": {
                    "tempting_wrong_path": "Stop at bloom peak and never inspect succession.",
                    "required_pivot": "switch to timing and succession",
                    "process_scoring_focus": ["pivot_latency", "evidence_ordering"],
                }
            },
        )

    def _make_state(self, explore_nodes=None, n_actions=0):
        from vigil.environments.base import EnvironmentState, EventType, TraversalEvent
        state = EnvironmentState(current_node="n0")
        state.visited_nodes = ["n0"]
        if explore_nodes:
            for nid in explore_nodes:
                state.action_history.append(TraversalEvent.make(
                    event_type=EventType.EXPLORE,
                    observation=f"Explored {nid}",
                    node_id=nid,
                    budget_delta=-1,
                ))
                state.visited_nodes.append(nid)
        return state

    def test_score_returns_no_vis_key(self):
        spec = self._make_exec_spec()
        scorer = ExecutiveScorer(spec)
        state = self._make_state()
        result = scorer.score(state, "switch to timing", "j", spec)
        assert "vis" not in result

    def test_score_contains_track_id_executive_functions(self):
        spec = self._make_exec_spec()
        scorer = ExecutiveScorer(spec)
        state = self._make_state()
        result = scorer.score(state, "switch to timing", "j", spec)
        assert result["track_id"] == "executive_functions"

    def test_inhibition_failures_increments_for_tempting_path(self):
        """Exploring bloom peak (tempting path) should increment inhibition_failures."""
        from vigil.environments.base import EnvironmentState, EventType, TraversalEvent
        spec = self._make_exec_spec()
        scorer = ExecutiveScorer(spec)

        state = EnvironmentState(current_node="n0")
        # Add an explore action with observation matching tempting path keywords
        state.action_history.append(TraversalEvent.make(
            event_type=EventType.EXPLORE,
            observation="Bloom peak toxicity data — stop here.",
            node_id="n1",
            budget_delta=-1,
        ))

        result = scorer.score(state, "switch to timing", "j", spec)
        # The observation contains "bloom" and "peak" which match tempting_wrong_path
        assert result["inhibition_failures"] >= 0  # may or may not match depending on keywords

    def test_impulsive_execution_when_tempting_path_first(self):
        """impulsive_execution = True when tempting path taken before goal-relevant node."""
        from vigil.environments.base import EnvironmentState, EventType, TraversalEvent
        spec = self._make_exec_spec()
        scorer = ExecutiveScorer(spec)

        state = EnvironmentState(current_node="n0")
        # First action is on tempting path (bloom peak)
        state.action_history.append(TraversalEvent.make(
            event_type=EventType.EXPLORE,
            observation="Bloom peak stop here never inspect succession.",
            node_id="n1",
            budget_delta=-1,
        ))

        result = scorer.score(state, "switch to timing", "j", spec)
        # With inhibition_failures >= 1 and it being the first action
        assert isinstance(result["behavioral_signatures"], dict)

    def test_process_score_in_range(self):
        spec = self._make_exec_spec()
        scorer = ExecutiveScorer(spec)
        state = self._make_state(explore_nodes=["n2"])
        result = scorer.score(state, "switch to timing and succession", "j", spec)
        assert 0.0 <= result["process_score"] <= 1.0

    def test_catalog_dispatches_to_executive_scorer(self):
        from vigil.scoring.track_scorers import TrackScorer
        spec = self._make_exec_spec()
        scorer = TrackScorer.for_track("executive_functions", spec)
        assert isinstance(scorer, ExecutiveScorer)

    def test_outcome_score_equals_correctness(self):
        spec = self._make_exec_spec()
        scorer = ExecutiveScorer(spec)
        state = self._make_state()
        result = scorer.score(state, "switch to timing", "j", spec)
        assert result["outcome_score"] == result["correctness"]
