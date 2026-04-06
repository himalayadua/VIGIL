"""
Unit tests for ScenarioLoader with Pydantic validation.

Tests:
- Valid JSON loads and validates correctly
- Missing required field raises ValueError with field name
- scoring_weights not summing to 1.0 raises ValueError
- Missing file raises FileNotFoundError
- All six production scenario files load without error

Requirements: 19.1, 19.2, 19.4
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from vigil.scenarios.loader import ScenarioLoader, ScenarioConfig


# ---------------------------------------------------------------------------
# Minimal valid scenario for testing
# ---------------------------------------------------------------------------

_VALID = {
    "scenario_id": "test_v1",
    "cognitive_track": "learning",
    "sub_ability": "concept_formation",
    "description": "test",
    "graph_config": {"num_nodes": 10},
    "hidden_rule": {
        "type": "test_rule",
        "description": "test description",
        "verification_pattern": ["test"],
    },
    "scoring_weights": {
        "correctness": 0.50,
        "efficiency": 0.20,
        "evidence_quality": 0.20,
        "calibration": 0.10,
    },
    "difficulty_levels": {
        "1": {"num_nodes": 6},
        "2": {"num_nodes": 10},
    },
    "budget": {"base": 10},
}


def _write_scenario(tmp_dir: Path, name: str, data: dict) -> ScenarioLoader:
    """Write a scenario JSON to a temp dir and return a loader for it."""
    (tmp_dir / f"{name}.json").write_text(json.dumps(data))
    return ScenarioLoader(scenarios_dir=str(tmp_dir))


# ---------------------------------------------------------------------------
# Valid loading
# ---------------------------------------------------------------------------

class TestValidLoading:
    def test_valid_scenario_loads(self, tmp_path):
        loader = _write_scenario(tmp_path, "test", _VALID)
        config = loader.load("test")
        assert config["scenario_id"] == "test_v1"
        assert config["cognitive_track"] == "learning"

    def test_returns_dict(self, tmp_path):
        loader = _write_scenario(tmp_path, "test", _VALID)
        config = loader.load("test")
        assert isinstance(config, dict)

    def test_all_required_fields_present(self, tmp_path):
        loader = _write_scenario(tmp_path, "test", _VALID)
        config = loader.load("test")
        for field in ["scenario_id", "cognitive_track", "sub_ability",
                      "graph_config", "hidden_rule", "scoring_weights",
                      "difficulty_levels", "budget"]:
            assert field in config, f"Missing field: {field}"

    def test_caching_returns_same_data(self, tmp_path):
        loader = _write_scenario(tmp_path, "test", _VALID)
        config1 = loader.load("test")
        config2 = loader.load("test")
        assert config1 == config2

    def test_reload_bypasses_cache(self, tmp_path):
        loader = _write_scenario(tmp_path, "test", _VALID)
        loader.load("test")
        config = loader.reload("test")
        assert config["scenario_id"] == "test_v1"

    def test_get_scenario_ids(self, tmp_path):
        _write_scenario(tmp_path, "test_a", _VALID)
        _write_scenario(tmp_path, "test_b", _VALID)
        loader = ScenarioLoader(scenarios_dir=str(tmp_path))
        ids = loader.get_scenario_ids()
        assert "test_a" in ids
        assert "test_b" in ids


# ---------------------------------------------------------------------------
# Missing required fields → ValueError with field name (Req 19.2)
# ---------------------------------------------------------------------------

class TestMissingRequiredFields:
    @pytest.mark.parametrize("missing_field", [
        "scenario_id",
        "cognitive_track",
        "sub_ability",
        "graph_config",
        "hidden_rule",
        "scoring_weights",
        "difficulty_levels",
        "budget",
    ])
    def test_missing_field_raises_value_error(self, tmp_path, missing_field):
        """Req 19.2: missing required field raises ValueError identifying the field."""
        bad = {k: v for k, v in _VALID.items() if k != missing_field}
        loader = _write_scenario(tmp_path, "bad", bad)
        with pytest.raises(ValueError) as exc_info:
            loader.load("bad")
        # Error message must identify the failing field
        assert missing_field in str(exc_info.value), (
            f"Expected '{missing_field}' in error message, got: {exc_info.value}"
        )

    def test_missing_hidden_rule_description_raises(self, tmp_path):
        """hidden_rule.description is required."""
        bad = dict(_VALID)
        bad["hidden_rule"] = {"type": "test_rule"}  # missing description
        loader = _write_scenario(tmp_path, "bad", bad)
        with pytest.raises(ValueError):
            loader.load("bad")


# ---------------------------------------------------------------------------
# scoring_weights not summing to 1.0 → ValueError (Req 19.4)
# ---------------------------------------------------------------------------

class TestScoringWeightsValidation:
    def test_weights_not_summing_to_one_raises(self, tmp_path):
        """Req 19.4: scoring_weights not summing to 1.0 raises ValueError."""
        bad = dict(_VALID)
        bad["scoring_weights"] = {
            "correctness": 0.50,
            "efficiency": 0.30,  # total = 0.80, not 1.0
        }
        loader = _write_scenario(tmp_path, "bad", bad)
        with pytest.raises(ValueError) as exc_info:
            loader.load("bad")
        assert "scoring_weights" in str(exc_info.value).lower() or "sum" in str(exc_info.value).lower()

    def test_weights_summing_to_one_passes(self, tmp_path):
        """Weights that sum to exactly 1.0 must not raise."""
        good = dict(_VALID)
        good["scoring_weights"] = {"correctness": 0.6, "efficiency": 0.4}
        loader = _write_scenario(tmp_path, "good", good)
        config = loader.load("good")
        assert config["scoring_weights"]["correctness"] == 0.6

    def test_weights_within_tolerance_passes(self, tmp_path):
        """Weights within 0.01 of 1.0 must not raise (floating point tolerance)."""
        good = dict(_VALID)
        good["scoring_weights"] = {"correctness": 0.501, "efficiency": 0.499}
        loader = _write_scenario(tmp_path, "good", good)
        config = loader.load("good")
        assert config is not None


# ---------------------------------------------------------------------------
# Missing file → FileNotFoundError (Req 19.1)
# ---------------------------------------------------------------------------

class TestMissingFile:
    def test_missing_file_raises_file_not_found(self, tmp_path):
        """Req 19.1: missing JSON file raises FileNotFoundError."""
        loader = ScenarioLoader(scenarios_dir=str(tmp_path))
        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load("nonexistent_scenario")
        assert "nonexistent_scenario" in str(exc_info.value)

    def test_error_includes_path(self, tmp_path):
        loader = ScenarioLoader(scenarios_dir=str(tmp_path))
        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load("missing")
        assert "missing" in str(exc_info.value)


# ---------------------------------------------------------------------------
# All six production scenario files load without error
# ---------------------------------------------------------------------------

class TestProductionScenarios:
    """All six production scenario JSONs must load and validate cleanly."""

    @pytest.mark.parametrize("scenario_name", [
        "concept_formation",
        "associative",
        "reinforcement",
        "observational",
        "procedural",
        "language",
    ])
    def test_production_scenario_loads(self, scenario_name):
        loader = ScenarioLoader()  # uses default schemas/ directory
        config = loader.load(scenario_name)
        assert config["cognitive_track"] == "learning"
        assert "scoring_weights" in config
        assert "difficulty_levels" in config

    def test_all_six_load_without_error(self):
        loader = ScenarioLoader()
        all_configs = loader.load_all()
        assert len(all_configs) == 6, (
            f"Expected 6 scenarios, got {len(all_configs)}: {list(all_configs.keys())}"
        )

    @pytest.mark.parametrize("scenario_name", [
        "concept_formation",
        "associative",
        "reinforcement",
        "observational",
        "procedural",
        "language",
    ])
    def test_scoring_weights_sum_to_one(self, scenario_name):
        loader = ScenarioLoader()
        config = loader.load(scenario_name)
        total = sum(config["scoring_weights"].values())
        assert abs(total - 1.0) <= 0.01, (
            f"{scenario_name}: scoring_weights sum to {total}, expected 1.0"
        )


# ---------------------------------------------------------------------------
# ScenarioConfig Pydantic model directly
# ---------------------------------------------------------------------------

class TestScenarioConfigModel:
    def test_valid_config_instantiates(self):
        config = ScenarioConfig(**_VALID)
        assert config.scenario_id == "test_v1"

    def test_to_dict_returns_dict(self):
        config = ScenarioConfig(**_VALID)
        d = config.to_dict()
        assert isinstance(d, dict)
        assert d["scenario_id"] == "test_v1"

    def test_weights_validator_raises_on_bad_sum(self):
        from pydantic import ValidationError
        bad = dict(_VALID)
        bad["scoring_weights"] = {"correctness": 0.3, "efficiency": 0.3}
        with pytest.raises(ValidationError):
            ScenarioConfig(**bad)
