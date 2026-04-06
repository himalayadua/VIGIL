"""
Scenario loader for cognitive benchmark configurations.

Loads scenario definitions from JSON files and provides them to
environment implementations.
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


class ScenarioLoader:
    """
    Loads and validates scenario configurations from JSON files.

    Scenarios define the graph structure, hidden rules, and scoring
    parameters for cognitive tests. The loader supports:
    - Loading from JSON files
    - Validation against expected schema
    - Hot-swapping scenario definitions
    - Multiple difficulty levels

    Example usage:
        loader = ScenarioLoader("path/to/scenarios")
        config = loader.load("concept_formation")
        env = ConceptFormationEnv(scenario_config=config)
    """

    def __init__(
        self,
        scenarios_dir: Optional[str] = None,
        validate_on_load: bool = True
    ):
        """
        Initialize the scenario loader.

        Args:
            scenarios_dir: Directory containing scenario JSON files.
                Defaults to ./scenarios/schemas/ relative to vigil package.
            validate_on_load: Whether to validate loaded configs.
        """
        if scenarios_dir:
            self.scenarios_dir = Path(scenarios_dir)
        else:
            # Default to package location
            self.scenarios_dir = Path(__file__).parent / "schemas"

        self.validate_on_load = validate_on_load
        self._cache: Dict[str, Dict[str, Any]] = {}

    def load(self, scenario_name: str) -> Dict[str, Any]:
        """
        Load a scenario configuration by name.

        Args:
            scenario_name: Name of the scenario (without .json extension)

        Returns:
            Dictionary containing scenario configuration.

        Raises:
            FileNotFoundError: If scenario JSON doesn't exist
            ValueError: If scenario fails validation
        """
        # Check cache first
        if scenario_name in self._cache:
            return self._cache[scenario_name].copy()

        # Load from file
        scenario_path = self.scenarios_dir / f"{scenario_name}.json"

        if not scenario_path.exists():
            raise FileNotFoundError(
                f"Scenario '{scenario_name}' not found at {scenario_path}"
            )

        with open(scenario_path, 'r') as f:
            config = json.load(f)

        # Validate if enabled
        if self.validate_on_load:
            self._validate_config(config, scenario_name)

        # Cache and return
        self._cache[scenario_name] = config
        return config.copy()

    def load_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all scenario configurations from the scenarios directory.

        Returns:
            Dictionary mapping scenario names to their configurations.
        """
        scenarios = {}

        if not self.scenarios_dir.exists():
            return scenarios

        for path in self.scenarios_dir.glob("*.json"):
            scenario_name = path.stem
            try:
                scenarios[scenario_name] = self.load(scenario_name)
            except (FileNotFoundError, ValueError) as e:
                # Skip invalid scenarios
                print(f"Warning: Could not load {scenario_name}: {e}")

        return scenarios

    def get_scenario_ids(self) -> List[str]:
        """
        Get list of available scenario IDs.

        Returns:
            List of scenario names (without .json extension).
        """
        if not self.scenarios_dir.exists():
            return []

        return [p.stem for p in self.scenarios_dir.glob("*.json")]

    def _validate_config(
        self,
        config: Dict[str, Any],
        scenario_name: str
    ) -> None:
        """
        Validate a scenario configuration.

        Args:
            config: Configuration dictionary to validate
            scenario_name: Name of the scenario (for error messages)

        Raises:
            ValueError: If configuration is invalid
        """
        required_fields = [
            "scenario_id",
            "cognitive_track",
            "sub_ability"
        ]

        for field in required_fields:
            if field not in config:
                raise ValueError(
                    f"Scenario '{scenario_name}' missing required field: {field}"
                )

        # Validate graph_config if present
        if "graph_config" in config:
            graph_config = config["graph_config"]
            if not isinstance(graph_config, dict):
                raise ValueError(
                    f"Scenario '{scenario_name}': graph_config must be a dictionary"
                )

        # Validate scoring_weights if present
        if "scoring_weights" in config:
            weights = config["scoring_weights"]
            if not isinstance(weights, dict):
                raise ValueError(
                    f"Scenario '{scenario_name}': scoring_weights must be a dictionary"
                )

            # Check weights sum to ~1.0
            total = sum(weights.values())
            if abs(total - 1.0) > 0.01:
                print(
                    f"Warning: Scenario '{scenario_name}' scoring weights "
                    f"sum to {total}, expected 1.0"
                )

    def reload(self, scenario_name: str) -> Dict[str, Any]:
        """
        Reload a scenario configuration (bypass cache).

        Args:
            scenario_name: Name of the scenario to reload

        Returns:
            Fresh configuration dictionary.
        """
        if scenario_name in self._cache:
            del self._cache[scenario_name]
        return self.load(scenario_name)

    def clear_cache(self) -> None:
        """Clear all cached scenarios."""
        self._cache.clear()
