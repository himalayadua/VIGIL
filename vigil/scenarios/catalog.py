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


def _validate_metacognition(raw: Dict[str, Any], scenario_id: str) -> None:
    """Validate Track 2 (metacognition) authored schema."""
    required = [
        "scenario_id", "cognitive_track", "blind_task_prompt",
        "object_level_goal", "meta_level_goal", "metacognitive_layers",
        "scoring_focus", "nodes", "edges",
    ]
    for field in required:
        if field not in raw:
            raise ValueError(
                f"Scenario '{scenario_id}' (metacognition) missing required field '{field}'"
            )


def _validate_attention(raw: Dict[str, Any], scenario_id: str) -> None:
    """Validate Track 3 (attention) authored schema."""
    required = [
        "scenario_id", "cognitive_track", "blind_task_prompt",
        "attention_design", "critical_evidence_node_ids",
        "target_conclusion", "nodes", "edges",
    ]
    for field in required:
        if field not in raw:
            raise ValueError(
                f"Scenario '{scenario_id}' (attention) missing required field '{field}'"
            )


def _validate_executive_functions(raw: Dict[str, Any], scenario_id: str) -> None:
    """Validate Track 4 (executive_functions) authored schema."""
    required = ["scenario_id", "cognitive_track", "executive_design_notes", "nodes", "edges"]
    for field in required:
        if field not in raw:
            raise ValueError(
                f"Scenario '{scenario_id}' (executive_functions) missing required field '{field}'"
            )
    ed = raw["executive_design_notes"]
    for sub in ("tempting_wrong_path", "required_pivot", "process_scoring_focus"):
        if sub not in ed:
            raise ValueError(
                f"Scenario '{scenario_id}' executive_design_notes missing '{sub}'"
            )


def _validate_social_cognition(raw: Dict[str, Any], scenario_id: str) -> None:
    """Validate Track 5 (social_cognition) authored schema."""
    required = [
        "scenario_id", "cognitive_track", "blind_task_prompt",
        "agent_nodes", "nodes", "edges",
    ]
    for field in required:
        if field not in raw:
            raise ValueError(
                f"Scenario '{scenario_id}' (social_cognition) missing required field '{field}'"
            )
    # Safety check: deceptive agents require safety_sandboxed
    metadata = raw.get("metadata", {})
    for agent in raw.get("agent_nodes", []):
        profile = agent.get("agent_profile", {})
        if profile.get("deceptive") is True:
            if not metadata.get("safety_sandboxed"):
                raise ValueError(
                    f"Scenario '{scenario_id}': agent node with 'deceptive: true' "
                    f"requires metadata.safety_sandboxed = true"
                )


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


def _compile_metacognition(raw: Dict[str, Any]) -> RuntimeScenarioSpec:
    """Compile a metacognition scenario into RuntimeScenarioSpec."""
    nodes = [
        RuntimeNode(
            node_id=n["node_id"],
            label=n.get("label", n["node_id"]),
            summary_text=n.get("content", ""),
            inspection_detail=n.get("content", ""),
            node_type=n.get("node_type", "standard"),
            initial_visibility=_map_visibility(n.get("visibility", "hidden")),
            metadata={"meta_relevance": n.get("meta_relevance", "")},
        )
        for n in raw["nodes"]
    ]

    edges = [
        RuntimeEdge(
            from_id=e["from"],
            to_id=e["to"],
            relation=e.get("edge_type", e.get("relation", "")),
            reveal_text=e.get("description", ""),
        )
        for e in raw["edges"]
    ]

    entry_nodes = [n.node_id for n in nodes if n.initial_visibility in ("visible", "initial")]
    if not entry_nodes:
        entry_nodes = [nodes[0].node_id] if nodes else []

    return RuntimeScenarioSpec(
        scenario_id=raw["scenario_id"],
        cognitive_track="metacognition",
        opening_prompt=raw["blind_task_prompt"],
        nodes=nodes,
        edges=edges,
        entry_node_ids=entry_nodes,
        answer_targets={
            "object_level_goal": raw["object_level_goal"],
            "meta_level_goal": raw["meta_level_goal"],
        },
        evidence_targets=[],
        optimal_path=[],
        optimal_steps=0,
        runtime_config=RuntimeConfig(action_budget=20),
        scoring_weights={
            "object_score": 0.3,
            "meta_score": 0.7,
        },
        track_metadata={
            "metacognitive_layers": raw.get("metacognitive_layers", []),
            "scoring_focus": raw.get("scoring_focus", []),
            "hidden_mechanism": raw.get("hidden_mechanism", ""),
            "disconfirmation_moment": raw.get("disconfirmation_moment", ""),
            "recommended_meta_actions": raw.get("recommended_meta_actions", []),
        },
    )


def _compile_attention(raw: Dict[str, Any]) -> RuntimeScenarioSpec:
    """Compile an attention scenario into RuntimeScenarioSpec."""
    nodes = [
        RuntimeNode(
            node_id=n["id"],
            label=n.get("label", n["id"]),
            summary_text=n.get("content", ""),
            inspection_detail=n.get("content", ""),
            node_type=n.get("kind", "standard"),
            initial_visibility=_map_visibility(n.get("initial_visibility", "hidden")),
            metadata={
                "salience": n.get("salience", ""),
                "diagnosticity": n.get("diagnosticity", ""),
            },
        )
        for n in raw["nodes"]
    ]

    edges = [
        RuntimeEdge(
            from_id=e["source"],
            to_id=e["target"],
            relation=e.get("relation", ""),
            metadata={"attention_role": e.get("attention_role", "")},
        )
        for e in raw["edges"]
    ]

    entry_nodes = [n.node_id for n in nodes if n.initial_visibility in ("visible", "initial")]
    if not entry_nodes:
        entry_nodes = [nodes[0].node_id] if nodes else []

    return RuntimeScenarioSpec(
        scenario_id=raw["scenario_id"],
        cognitive_track="attention",
        opening_prompt=raw["blind_task_prompt"],
        nodes=nodes,
        edges=edges,
        entry_node_ids=entry_nodes,
        answer_targets={"target_conclusion": raw["target_conclusion"]},
        evidence_targets=list(raw.get("critical_evidence_node_ids", [])),
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
        track_metadata={
            "attention_design": raw.get("attention_design", {}),
            "hidden_mechanism": raw.get("hidden_mechanism", ""),
            "disconfirmation_moment": raw.get("disconfirmation_moment", ""),
        },
    )


def _compile_executive_functions(raw: Dict[str, Any]) -> RuntimeScenarioSpec:
    """Compile an executive_functions scenario into RuntimeScenarioSpec."""
    nodes = [
        RuntimeNode(
            node_id=n["id"],
            label=n.get("label", n["id"]),
            summary_text=n.get("description", ""),
            inspection_detail=n.get("description", ""),
            node_type=n.get("type", "standard"),
            initial_visibility="hidden",
        )
        for n in raw["nodes"]
    ]

    edges = [
        RuntimeEdge(
            from_id=e["from"],
            to_id=e["to"],
            relation=e.get("relation", ""),
        )
        for e in raw["edges"]
    ]

    # Entry node is the first node (entry brief)
    entry_nodes = [nodes[0].node_id] if nodes else []

    return RuntimeScenarioSpec(
        scenario_id=raw["scenario_id"],
        cognitive_track="executive_functions",
        opening_prompt=nodes[0].summary_text if nodes else "",
        nodes=nodes,
        edges=edges,
        entry_node_ids=entry_nodes,
        answer_targets={
            "required_pivot": raw["executive_design_notes"].get("required_pivot", ""),
        },
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
        track_metadata={"executive_design_notes": raw["executive_design_notes"]},
    )


def _compile_social_cognition(raw: Dict[str, Any]) -> RuntimeScenarioSpec:
    """Compile a social_cognition scenario into RuntimeScenarioSpec."""
    nodes = [
        RuntimeNode(
            node_id=n.get("id", n.get("node_id", "")),
            label=n.get("label", ""),
            summary_text=n.get("content", n.get("description", "")),
            inspection_detail=n.get("content", n.get("description", "")),
            node_type=n.get("node_type", n.get("type", "standard")),
            initial_visibility=_map_visibility(n.get("visibility", "hidden")),
            metadata=n.get("metadata", {}),
        )
        for n in raw["nodes"]
    ]

    edges = [
        RuntimeEdge(
            from_id=e.get("from", e.get("source", "")),
            to_id=e.get("to", e.get("target", "")),
            relation=e.get("relation", e.get("edge_type", "")),
            reveal_text=e.get("description", e.get("reveal", "")),
        )
        for e in raw["edges"]
    ]

    entry_nodes = [n.node_id for n in nodes if n.initial_visibility in ("visible", "initial")]
    if not entry_nodes:
        entry_nodes = [nodes[0].node_id] if nodes else []

    return RuntimeScenarioSpec(
        scenario_id=raw["scenario_id"],
        cognitive_track="social_cognition",
        opening_prompt=raw.get("blind_task_prompt", ""),
        nodes=nodes,
        edges=edges,
        entry_node_ids=entry_nodes,
        answer_targets={},
        evidence_targets=[],
        optimal_path=[],
        optimal_steps=0,
        runtime_config=RuntimeConfig(action_budget=20),
        scoring_weights={
            "partner_model_accuracy": 0.25,
            "social_repair_quality": 0.2,
            "trust_calibration": 0.2,
            "communication_appropriateness": 0.2,
            "information_asymmetry_exploitation": 0.15,
        },
        track_metadata={
            "agent_nodes": raw.get("agent_nodes", []),
            "private_knowledge": raw.get("private_knowledge", {}),
            "agent_responses": raw.get("agent_responses", {}),
        },
    )


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

        if array_idx is not None:
            return data[array_idx]
        return data

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
