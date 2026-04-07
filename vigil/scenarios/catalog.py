"""
ScenarioCatalog — authored pack ingestion and dispatch.

Ingests authored JSON packs (one file = many scenarios, or one file = one
scenario), validates each scenario against the correct per-track Pydantic
schema, compiles it into a RuntimeScenarioSpec, and caches the result.

The catalog dispatches by cognitive_track string value — never by file name
or folder number. This is the sole dispatch key.

Requirements: 1, 2, 3, 16
"""

import json
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vigil.scenarios.runtime_spec import (
    EvaluationConditions,
    RuntimeConfig,
    RuntimeEdge,
    RuntimeNode,
    RuntimeScenarioSpec,
)
from vigil.scenarios.adapters.learning_adapter import LearningAdapter
from vigil.scenarios.adapters.metacognition_adapter import MetacognitionAdapter
from vigil.scenarios.adapters.attention_adapter import AttentionAdapter
from vigil.scenarios.adapters.executive_adapter import ExecutiveAdapter
from vigil.scenarios.adapters.social_adapter import SocialAdapter


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ScenarioNotFoundError(KeyError):
    """Raised when a scenario_id is not found in any discovered pack."""
    pass


# ---------------------------------------------------------------------------
# Per-track authored schema validators (Pydantic-lite, inline)
# ---------------------------------------------------------------------------

# LearningAdapter is the canonical Track 1 adapter (extracted module).
# MetacognitionAdapter is the canonical Track 2 adapter.
# Other tracks use inline validators/compilers until their adapters are built.
_LEARNING_ADAPTER = LearningAdapter()
_METACOGNITION_ADAPTER = MetacognitionAdapter()
_ATTENTION_ADAPTER = AttentionAdapter()
_EXECUTIVE_ADAPTER = ExecutiveAdapter()
_SOCIAL_ADAPTER = SocialAdapter()


def _validate_learning(raw: Dict[str, Any], scenario_id: str) -> None:
    """Delegate to LearningAdapter.validate()."""
    _LEARNING_ADAPTER.validate(raw, scenario_id)


def _validate_metacognition(raw: Dict[str, Any], scenario_id: str) -> None:
    """Delegate to MetacognitionAdapter.validate()."""
    _METACOGNITION_ADAPTER.validate(raw, scenario_id)


def _validate_attention(raw: Dict[str, Any], scenario_id: str) -> None:
    """Delegate to AttentionAdapter.validate()."""
    _ATTENTION_ADAPTER.validate(raw, scenario_id)


def _validate_executive_functions(raw: Dict[str, Any], scenario_id: str) -> None:
    """Delegate to ExecutiveAdapter.validate()."""
    _EXECUTIVE_ADAPTER.validate(raw, scenario_id)


def _validate_social_cognition(raw: Dict[str, Any], scenario_id: str) -> None:
    """Delegate to SocialAdapter.validate()."""
    _SOCIAL_ADAPTER.validate(raw, scenario_id)


_VALIDATORS: Dict[str, Any] = {
    "learning": _validate_learning,
    "metacognition": _validate_metacognition,
    "attention": _validate_attention,
    "executive_functions": _validate_executive_functions,
    "social_cognition": _validate_social_cognition,
}


# ---------------------------------------------------------------------------
# Per-track compilers: raw dict → RuntimeScenarioSpec
# ---------------------------------------------------------------------------

def _compile_learning(raw: Dict[str, Any]) -> RuntimeScenarioSpec:
    """Delegate to LearningAdapter.compile()."""
    return _LEARNING_ADAPTER.compile(raw)


def _compile_metacognition(raw: Dict[str, Any]) -> RuntimeScenarioSpec:
    """Delegate to MetacognitionAdapter.compile()."""
    return _METACOGNITION_ADAPTER.compile(raw)


def _compile_attention(raw: Dict[str, Any]) -> RuntimeScenarioSpec:
    """Delegate to AttentionAdapter.compile()."""
    return _ATTENTION_ADAPTER.compile(raw)


def _compile_executive_functions(raw: Dict[str, Any]) -> RuntimeScenarioSpec:
    """Delegate to ExecutiveAdapter.compile()."""
    return _EXECUTIVE_ADAPTER.compile(raw)



def _compile_social_cognition(raw: Dict[str, Any]) -> RuntimeScenarioSpec:
    """Delegate to SocialAdapter.compile()."""
    return _SOCIAL_ADAPTER.compile(raw)


_COMPILERS: Dict[str, Any] = {
    "learning": _compile_learning,
    "metacognition": _compile_metacognition,
    "attention": _compile_attention,
    "executive_functions": _compile_executive_functions,
    "social_cognition": _compile_social_cognition,
}


def _map_visibility(raw_vis: str) -> str:
    """Map authored visibility strings to canonical RuntimeNode values."""
    mapping = {
        "visible": "visible",
        "initial": "initial",
        "hidden": "hidden",
        "expanded": "visible",   # treat expanded as visible at start
        "discovered": "hidden",  # treat discovered as hidden (will be revealed)
        "unexplored": "hidden",
    }
    return mapping.get(raw_vis.lower(), "hidden")


# ---------------------------------------------------------------------------
# ScenarioCatalog
# ---------------------------------------------------------------------------

class ScenarioCatalog:
    """
    Ingests authored JSON packs, validates per-track schemas, compiles to
    RuntimeScenarioSpec, and caches results.

    Dispatch is always by cognitive_track string — never by file name.

    Usage:
        catalog = ScenarioCatalog(packs_dir="vigil/scenarios/packs/")
        spec = catalog.load("vigil_eco_01_kethara_succession")
        spec_seed2 = catalog.load("vigil_eco_01_kethara_succession", seed=2)
        ids = catalog.get_scenario_ids(track="learning")
    """

    def __init__(self, packs_dir: Optional[str] = None) -> None:
        if packs_dir:
            self._packs_dir = Path(packs_dir)
        else:
            self._packs_dir = Path(__file__).parent / "packs"

        # Index: scenario_id → (file_path, array_index_or_None)
        self._index: Dict[str, Tuple[Path, Optional[int]]] = {}
        # Cache: (scenario_id, seed) → RuntimeScenarioSpec
        self._cache: Dict[Tuple[str, int], RuntimeScenarioSpec] = {}

        self._build_index()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, scenario_id: str, seed: int = 0) -> RuntimeScenarioSpec:
        """
        Load, validate, compile, and return a RuntimeScenarioSpec.

        Args:
            scenario_id: The scenario's unique identifier.
            seed:        0 = no perturbation (default). Other values apply
                         a deterministic node-order reordering.

        Returns:
            Compiled RuntimeScenarioSpec (cached after first call).

        Raises:
            ScenarioNotFoundError: If scenario_id is not in any pack.
            ValueError:            If the authored schema is invalid.
        """
        cache_key = (scenario_id, seed)
        if cache_key in self._cache:
            return self._cache[cache_key]

        raw = self._load_raw(scenario_id)
        spec = self._compile(raw, scenario_id)

        if seed != 0:
            spec = spec.apply_seed_perturbation(seed)

        self._cache[cache_key] = spec
        return spec

    def load_track(self, track: str) -> List[RuntimeScenarioSpec]:
        """Return all compiled specs for a given cognitive_track string."""
        return [self.load(sid) for sid in self.get_scenario_ids(track=track)]

    def get_scenario_ids(self, track: Optional[str] = None) -> List[str]:
        """
        Return all known scenario IDs, optionally filtered by cognitive_track.

        Args:
            track: If provided, only return IDs for this cognitive_track.
        """
        if track is None:
            return sorted(self._index.keys())

        result = []
        for sid in self._index:
            raw = self._load_raw(sid)
            if raw.get("cognitive_track") == track:
                result.append(sid)
        return sorted(result)

    def load_transfer_variant(
        self,
        scenario_id: str,
        perturbation_type: str,
        seed: int,
    ) -> RuntimeScenarioSpec:
        """
        Apply a perturbation to produce a transfer variant.

        Args:
            scenario_id:       Base scenario to perturb.
            perturbation_type: One of "reorder_nodes", "rename_entities",
                               "reskin_domain".
            seed:              Seed for deterministic perturbation.

        Returns:
            Perturbed RuntimeScenarioSpec.

        Raises:
            NotImplementedError: For perturbation types not yet implemented.
        """
        if perturbation_type == "reorder_nodes":
            return self.load(scenario_id, seed=seed)
        elif perturbation_type in ("rename_entities", "reskin_domain"):
            raise NotImplementedError(
                f"perturbation_type='{perturbation_type}' is not yet implemented. "
                f"Only 'reorder_nodes' is currently supported."
            )
        else:
            raise ValueError(
                f"Unknown perturbation_type '{perturbation_type}'. "
                f"Valid values: 'reorder_nodes', 'rename_entities', 'reskin_domain'."
            )

    def reload(self, scenario_id: Optional[str] = None) -> None:
        """
        Invalidate cache. If scenario_id is given, only that entry is cleared.
        Otherwise the entire cache is cleared and the index is rebuilt.
        """
        if scenario_id is not None:
            keys_to_remove = [k for k in self._cache if k[0] == scenario_id]
            for k in keys_to_remove:
                del self._cache[k]
        else:
            self._cache.clear()
            self._build_index()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_index(self) -> None:
        """Scan packs_dir and build scenario_id → (file, array_index) index."""
        self._index.clear()
        if not self._packs_dir.exists():
            return

        for path in sorted(self._packs_dir.glob("*.json")):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                warnings.warn(f"ScenarioCatalog: could not parse {path}", stacklevel=2)
                continue

            if isinstance(data, list):
                for idx, item in enumerate(data):
                    if isinstance(item, dict) and "scenario_id" in item:
                        sid = item["scenario_id"]
                        if sid in self._index:
                            warnings.warn(
                                f"ScenarioCatalog: duplicate scenario_id '{sid}' "
                                f"in {path} (index {idx}); keeping first occurrence.",
                                stacklevel=2,
                            )
                        else:
                            self._index[sid] = (path, idx)
            elif isinstance(data, dict) and "scenario_id" in data:
                sid = data["scenario_id"]
                if sid not in self._index:
                    self._index[sid] = (path, None)
            elif isinstance(data, dict):
                # Handle wrapper dicts like {"scenarios": [...]}
                # Find the first key whose value is a list of scenario dicts
                for key, val in data.items():
                    if isinstance(val, list):
                        for idx, item in enumerate(val):
                            if isinstance(item, dict) and "scenario_id" in item:
                                sid = item["scenario_id"]
                                if sid in self._index:
                                    warnings.warn(
                                        f"ScenarioCatalog: duplicate scenario_id '{sid}' "
                                        f"in {path} (index {idx}); keeping first occurrence.",
                                        stacklevel=2,
                                    )
                                else:
                                    self._index[sid] = (path, (key, idx))
                        break

    def _load_raw(self, scenario_id: str) -> Dict[str, Any]:
        """Load the raw dict for a scenario_id from disk."""
        if scenario_id not in self._index:
            raise ScenarioNotFoundError(
                f"Scenario '{scenario_id}' not found in any pack under "
                f"'{self._packs_dir}'. "
                f"Available IDs: {sorted(self._index.keys())[:5]}..."
                if self._index else
                f"Scenario '{scenario_id}' not found. No packs loaded from '{self._packs_dir}'."
            )

        path, array_idx = self._index[scenario_id]
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if array_idx is None:
            # Single-scenario dict
            return data
        elif isinstance(array_idx, tuple):
            # Wrapped array: (key, idx) e.g. ("scenarios", 3)
            key, idx = array_idx
            return data[key][idx]
        else:
            # Bare array: integer index
            return data[array_idx]

    def _compile(self, raw: Dict[str, Any], scenario_id: str) -> RuntimeScenarioSpec:
        """Validate and compile a raw dict into a RuntimeScenarioSpec."""
        track = raw.get("cognitive_track", "")
        if not track:
            raise ValueError(
                f"Scenario '{scenario_id}' is missing 'cognitive_track' field."
            )

        validator = _VALIDATORS.get(track)
        if validator is None:
            raise ValueError(
                f"Scenario '{scenario_id}' has unknown cognitive_track '{track}'. "
                f"Known tracks: {sorted(_VALIDATORS.keys())}"
            )

        validator(raw, scenario_id)

        compiler = _COMPILERS[track]
        return compiler(raw)
