# Vigil: Multi-Track Cognitive Graph Benchmark

**Tracks 1–5: Learning, Metacognition, Attention, Executive Function, Social Cognition**
Google DeepMind × Kaggle "Measuring AGI" Hackathon

## Overview

Vigil is a benchmark framework that places AI models in **stateful cognitive graph environments** where they must explore, reason, and demonstrate cognitive abilities through their actions — not just answer questions.

### Core Innovation

Instead of static QA benchmarks, Vigil places models in interactive graph environments where they must:
- Navigate through authored scenario graphs
- Collect evidence and form hypotheses
- Submit conclusions with justification
- Be scored on both outcome and process quality

### Cognitive Tracks (Kaggle Official)

| Track | Cognitive Ability | Status |
|-------|------------------|--------|
| 1 | Learning | ✅ Implemented |
| 2 | Metacognition | ✅ Implemented |
| 3 | Attention | ✅ Implemented |
| 4 | Executive Function | ✅ Implemented |
| 5 | Social Cognition | ✅ Implemented |

## Quick Start

### On Kaggle

```python
import kaggle_benchmarks as kbench
from vigil.tasks.vigil_benchmark import vigil_benchmark

# Run the full multi-track benchmark
%choose vigil_benchmark
```

### Local Testing

```bash
# Run full test suite
python -m pytest vigil/tests/ -q

# Run a single Track 1 scenario end-to-end
python -c "
from vigil.scenarios.catalog import ScenarioCatalog
from vigil.environments.graph_scenario_env import GraphScenarioEnvironment
catalog = ScenarioCatalog('vigil/scenarios/packs/')
spec = catalog.load('vigil_eco_01_kethara_succession')
env = GraphScenarioEnvironment(spec)
state = env.reset()
print('Reset OK, budget:', state.budget_remaining)
"
```

## Architecture

### Directory Structure

```
vigil/
├── environments/
│   ├── base.py                  # CognitiveEnvironment ABC, EnvironmentState, EventType
│   └── graph_scenario_env.py    # GraphScenarioEnvironment (shared runtime for all tracks)
├── graphs/
│   ├── core.py                  # CognitiveGraph, from_spec()
│   └── generators.py            # ProceduralGenerator (transfer perturbations)
├── scenarios/
│   ├── runtime_spec.py          # RuntimeScenarioSpec, RuntimeConfig, EvaluationConditions
│   ├── catalog.py               # ScenarioCatalog — authored pack ingestion and dispatch
│   ├── loader.py                # ScenarioLoader (backward-compat shim → catalog)
│   ├── adapters/
│   │   ├── learning_adapter.py      # Track 1
│   │   ├── metacognition_adapter.py # Track 2
│   │   ├── attention_adapter.py     # Track 3
│   │   ├── executive_adapter.py     # Track 4
│   │   └── social_adapter.py        # Track 5
│   └── packs/                   # Authored JSON scenario packs
├── actions/
│   ├── parser.py                # Parse model actions from JSON or string
│   └── schemas.py               # VigilAction union, TrackActionSchema
├── scoring/
│   ├── vis.py                   # VISScorer (0.3 × outcome + 0.7 × process)
│   ├── track_scorers.py         # TrackScorer ABC + per-track implementations
│   ├── faculty_profiler.py      # FacultyProfiler — two-stage aggregation
│   ├── metrics.py               # Shared scoring utilities
│   └── profile.py               # HumanBaseline, CognitiveProfile
├── tasks/
│   ├── vigil_benchmark.py       # vigil_episode + vigil_benchmark (leaderboard)
│   └── track1_learning.py       # vigil_learning_benchmark (Track 1 wrapper)
├── baselines/
│   └── collector.py             # Human baseline collection
└── tests/                       # Full test suite (760 tests)
```

### Key Components

#### GraphScenarioEnvironment
Shared runtime for all five tracks. Accepts a `RuntimeScenarioSpec` and handles:
- Graph traversal with per-edge costs
- Budget tracking (separate from `optimal_steps`)
- System event firing (CONTRADICTION, RELEVANCE_SHIFT, etc.)
- `evaluation_conditions` enforcement (tool policy, allowed tools)
- `score_episode()` → `ScoreCard` (no `vis` key)

#### ScenarioCatalog
Ingests authored JSON packs, dispatches by `cognitive_track` string, validates per-track schemas, compiles to `RuntimeScenarioSpec`, and caches results.

```python
from vigil.scenarios.catalog import ScenarioCatalog

catalog = ScenarioCatalog("vigil/scenarios/packs/")
spec = catalog.load("vigil_eco_01_kethara_succession")
spec_seed2 = catalog.load("vigil_eco_01_kethara_succession", seed=2)
ids = catalog.get_scenario_ids(track="learning")
```

#### VISScorer
Computes the final VIS score: `0.3 × outcome_score + 0.7 × process_score`.
Accepts an optional `scorecard` from `TrackScorer` for per-track dimension scores.

#### FacultyProfiler
Two-stage aggregation:
1. `aggregate_seeds()` → `ScenarioAggregate` per scenario (cross-seed variance)
2. `build_profile()` → `FacultyProfile` per track (mean VIS, CI_95, human percentile)
3. `benchmark_aggregate()` → mean of per-track means (not raw scenario mean)

#### TrackActionSchema
Per-track action subsets passed to `llm.prompt(schema=...)`:
- Tracks 1, 3, 4: base 4 actions (explore, inspect, get_context, submit_answer)
- Track 2: base + ask_for_help
- Track 5: base + send_message + make_commitment

## Scoring

### VIS Formula
```
VIS = 0.3 × outcome_score + 0.7 × process_score
```

### Two-Step Scoring Pipeline
```
env.score_episode() → ScoreCard (track dimensions, no vis key)
VISScorer.score_episode(scorecard=scorecard) → VISResult (has vis key)
```

### Benchmark Aggregation
```
benchmark_aggregate = mean({track.mean_vis for track in profiles})
```
Each faculty contributes equally regardless of scenario count.

## Authored Scenario Format

Scenarios are JSON files in `vigil/scenarios/packs/`. Each track has its own schema:

**Track 1 (Learning):**
```json
{
  "scenario_id": "vigil_eco_01_kethara_succession",
  "cognitive_track": "learning",
  "blind_framing": "You are investigating...",
  "hidden_objective": {
    "correct_root_cause": "...",
    "minimum_evidence_nodes": ["n3", "n7"]
  },
  "nodes": [...],
  "edges": [...],
  "optimal_path": {"sequence": ["n0", "n3", "n7"], "length": 2},
  "scoring_config": {"max_steps": 15, "weights": {...}}
}
```

## Testing

```bash
# Full suite
python -m pytest vigil/tests/ -q

# Property-based tests only
python -m pytest vigil/tests/properties/ -q

# Single test file
python -m pytest vigil/tests/test_catalog.py -v
```

## References

- [DeepMind AGI Cognitive Framework](https://arxiv.org/abs/2312.02439)
- [Kaggle Benchmarks SDK](https://github.com/Kaggle/kaggle-benchmarks)
- [Chollet's Measure of Intelligence](https://arxiv.org/abs/1911.01547)

## License

Apache 2.0
