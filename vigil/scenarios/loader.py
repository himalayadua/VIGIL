"""
Scenario loader with Pydantic validation.

Loads scenario JSON files and validates them against ScenarioConfig.
Raises descriptive errors on missing fields or invalid weights.

This module maintains backward compatibility with the old filename-stem interface.
Internally, load() now delegates to ScenarioCatalog when the scenario_id is found
in the authored packs. Falls back to the old file-based approach for test fixtures
in vigil/scenarios/schemas/*.json.

Requirements: 18, 19.1, 19.2, 19.3, 19.4
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator, model_validator


# ---------------------------------------------------------------------------
# Pydantic schema (Req 19.3)
# ---------------------------------------------------------------------------

class HiddenRule(BaseModel):
    type: str
    description: str
    verification_pattern: List[str] = []


class ScenarioConfig(BaseModel):
    """
    Validated scenario configuration.

    Required fields: scenario_id, cognitive_track, sub_ability,
    graph_config, hidden_rule, scoring_weights, difficulty_levels, budget.
    """
    scenario_id: str
    cognitive_track: str
    sub_ability: str
    description: str = ""
    graph_config: Dict[str, Any]
    hidden_rule: HiddenRule
    scoring_weights: Dict[str, float]
    difficulty_levels: Dict[str, Dict[str, Any]]
    budget: Dict[str, Any]
    optimal_steps: int = 6
    metadata: Dict[str, Any] = {}

    @field_validator("scoring_weights")
    @classmethod
    def weights_must_sum_to_one(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Req 19.4: scoring_weights must sum to 1.0."""
        total = sum(v.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(
                f"scoring_weights must sum to 1.0, got {total:.4f}. "
                f"Weights: {v}"
            )
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Return as plain dict for backward compatibility with environments."""
        return self.model_dump()


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

class ScenarioLoader:
    """
    Loads and Pydantic-validates scenario configurations from JSON files.

    Usage:
        loader = ScenarioLoader()
        config = loader.load("concept_formation")  # returns dict
        env = ConceptFormationEnv(scenario_config=config)
    """

    def __init__(
        self,
        scenarios_dir: Optional[str] = None,
        validate_on_load: bool = True,
    ):
        if scenarios_dir:
            self.scenarios_dir = Path(scenarios_dir)
        else:
            self.scenarios_dir = Path(__file__).parent / "schemas"

        self.validate_on_load = validate_on_load
        self._cache: Dict[str, Dict[str, Any]] = {}

    def load(self, scenario_name: str) -> Dict[str, Any]:
        """
        Load and validate a scenario by name.

        Delegation order:
          1. Try ScenarioCatalog.load(scenario_name) — returns RuntimeScenarioSpec
             converted to dict via to_scenario_config_dict() for backward compat.
          2. Fall back to the old file-based approach (vigil/scenarios/schemas/*.json)
             for test fixtures and legacy scenarios not in the authored packs.

        Args:
            scenario_name: Filename stem (without .json) or scenario_id

        Returns:
            Plain dict of the validated scenario config.

        Raises:
            FileNotFoundError: If the JSON file does not exist (Req 19.1)
            ValueError: If a required field is missing or weights don't sum to 1.0 (Req 19.2, 19.4)
        """
        if scenario_name in self._cache:
            return self._cache[scenario_name].copy()

        # Try catalog first (authored packs)
        try:
            from vigil.scenarios.catalog import ScenarioCatalog
            catalog = ScenarioCatalog()
            spec = catalog.load(scenario_name)
            # Convert RuntimeScenarioSpec to dict for backward compat
            raw = spec.to_scenario_config_dict()
            # Add fields expected by old environments
            raw.setdefault("scenario_id", spec.scenario_id)
            raw.setdefault("cognitive_track", spec.cognitive_track)
            raw.setdefault("sub_ability", spec.cognitive_track)
            raw.setdefault("graph_config", {})
            raw.setdefault("hidden_rule", {"type": "unknown", "description": ""})
            raw.setdefault("scoring_weights", spec.scoring_weights)
            raw.setdefault("difficulty_levels", {"medium": {}})
            raw.setdefault("budget", {"max_steps": spec.runtime_config.action_budget})
            raw.setdefault("optimal_steps", spec.optimal_steps)
            self._cache[scenario_name] = raw
            return raw.copy()
        except Exception:
            pass  # Fall through to file-based approach

        # Fall back: load from vigil/scenarios/schemas/*.json (test fixtures)
        scenario_path = self.scenarios_dir / f"{scenario_name}.json"

        if not scenario_path.exists():
            raise FileNotFoundError(
                f"Scenario '{scenario_name}' not found at {scenario_path}"
            )

        with open(scenario_path, "r") as f:
            raw = json.load(f)

        if self.validate_on_load:
            raw = self._validate(raw, scenario_name)

        self._cache[scenario_name] = raw
        return raw.copy()

    def _validate(self, raw: Dict[str, Any], scenario_name: str) -> Dict[str, Any]:
        """
        Validate raw dict against ScenarioConfig.

        Converts Pydantic ValidationError into a descriptive ValueError
        that identifies the failing field (Req 19.2).
        """
        from pydantic import ValidationError
        try:
            validated = ScenarioConfig(**raw)
            return validated.to_dict()
        except ValidationError as e:
            # Extract the first error's field path for a clear message
            errors = e.errors()
            if errors:
                field = " → ".join(str(loc) for loc in errors[0]["loc"])
                msg = errors[0]["msg"]
                raise ValueError(
                    f"Scenario '{scenario_name}' validation failed on field '{field}': {msg}"
                ) from e
            raise ValueError(f"Scenario '{scenario_name}' validation failed: {e}") from e

    def load_all(self) -> Dict[str, Dict[str, Any]]:
        """Load all scenario JSON files from the schemas directory."""
        scenarios = {}
        if not self.scenarios_dir.exists():
            return scenarios
        for path in self.scenarios_dir.glob("*.json"):
            name = path.stem
            try:
                scenarios[name] = self.load(name)
            except (FileNotFoundError, ValueError) as exc:
                print(f"Warning: Could not load '{name}': {exc}")
        return scenarios

    def get_scenario_ids(self) -> List[str]:
        """Return list of available scenario names (without .json)."""
        if not self.scenarios_dir.exists():
            return []
        return [p.stem for p in self.scenarios_dir.glob("*.json")]

    def reload(self, scenario_name: str) -> Dict[str, Any]:
        """Reload a scenario bypassing the cache."""
        self._cache.pop(scenario_name, None)
        return self.load(scenario_name)

    def clear_cache(self) -> None:
        """Clear all cached scenarios."""
        self._cache.clear()
