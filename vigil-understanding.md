# Vigil: Don't Ask — Watch
## Complete Benchmark Reference

Vigil is a stateful cognitive graph benchmark for the Google DeepMind × Kaggle "Measuring Progress Toward AGI" hackathon. It measures five cognitive faculties by placing an AI model inside an interactive graph environment and watching how it navigates — not what it says it can do.

---

## The Core Idea

Most benchmarks ask a model a question and check the answer. Vigil does something different: it gives the model a partially-visible graph, a budget of actions, and a task framing that deliberately hides the answer. The model must explore, gather evidence, and reason about what it finds before submitting a conclusion.

The benchmark measures **both** what the model concludes (outcome) **and** how it got there (process). A model that guesses the right answer without exploring the evidence scores lower than one that systematically investigates and arrives at the same answer.

---

## The Five Cognitive Tracks

Each track tests a different cognitive faculty. The `cognitive_track` string in the scenario JSON is the sole dispatch key — file names and folder numbers are non-semantic.

| Kaggle Track | `cognitive_track` string | What it measures | Scenarios |
|---|---|---|---|
| Track 1 | `"learning"` | Causal inference from evidence | 30 |
| Track 2 | `"metacognition"` | Self-monitoring and calibration | 30 |
| Track 3 | `"attention"` | Signal vs. distractor discrimination | 30 |
| Track 4 | `"executive_functions"` | Inhibition and goal-directed switching | 30 |
| Track 5 | `"social_cognition"` | Social causal reasoning | 30 |

**Total: 150 authored scenarios × 3 seeds = 450 episodes per full benchmark run.**

---

## Scenario Packs

All scenarios live in `vigil/scenarios/packs/`. Each pack is a JSON file:

| File | Track | Format |
|---|---|---|
| `vigil_all_30_scenarios.json` | `learning` | bare array `[...]` |
| `track4_metacognition_synthetic_scenarios_from_skeletons.json` | `metacognition` | bare array `[...]` |
| `track2_attention_synthetic_scenarios.json` | `attention` | bare array `[...]` |
| `vigil_track3_executive_scenarios_from_skeletons_v1.json` | `executive_functions` | bare array `[...]` |
| `vigil_track5_social_scenarios_from_skeletons_v1.json` | `social_cognition` | wrapped `{"scenarios": [...]}` |

The catalog handles all three formats transparently.

---

## How a Scenario Is Loaded

```
JSON pack file
    ↓
ScenarioCatalog._build_index()        — scans packs/, builds scenario_id → file index
    ↓
ScenarioCatalog.load(scenario_id)
    ↓
TrackAdapter.validate(raw)            — checks required fields for this track
    ↓
TrackAdapter.compile(raw)             — normalises raw JSON → RuntimeScenarioSpec
    ↓
RuntimeScenarioSpec                   — canonical internal representation
    ↓
(optional) apply_seed_perturbation()  — reorders node IDs deterministically
    ↓
cached by (scenario_id, seed)
```

### The Five Adapters

Each track has a dedicated adapter in `vigil/scenarios/adapters/`:

| Adapter | Track | Key field mappings |
|---|---|---|
| `LearningAdapter` | `learning` | `blind_framing` → `opening_prompt`; `hidden_objective` → `answer_targets`; `scoring_config.max_steps` → `action_budget` |
| `MetacognitionAdapter` | `metacognition` | `blind_task_prompt` → `opening_prompt`; `object_level_goal` + `meta_level_goal` → `answer_targets` |
| `AttentionAdapter` | `attention` | `blind_task_prompt` → `opening_prompt`; `critical_evidence_node_ids` → `evidence_targets`; `attention_role` on edges → `metadata` |
| `ExecutiveAdapter` | `executive_functions` | first node's `description` → `opening_prompt`; `executive_design_notes` → `track_metadata` |
| `SocialAdapter` | `social_cognition` | `task_frame` → `opening_prompt`; `hidden_mechanism` → `answer_targets`; `causal_chain` + `red_herrings` → `track_metadata` |

### RuntimeScenarioSpec — the canonical contract

Every scenario, regardless of track, becomes a `RuntimeScenarioSpec` with three strictly separate sections:

```python
RuntimeScenarioSpec(
    scenario_id = "vigil_eco_01_kethara_succession",
    cognitive_track = "learning",
    opening_prompt = "You are investigating...",   # shown to model at step 0
    nodes = [...],                                  # RuntimeNode list
    edges = [...],                                  # RuntimeEdge list
    entry_node_ids = ["n1"],                        # where the model starts
    answer_targets = {"correct_root_cause": "..."},
    evidence_targets = ["n3", "n7"],                # nodes that count as evidence

    # --- runtime mechanics (NOT scoring) ---
    runtime_config = RuntimeConfig(
        action_budget = 15,          # starting budget
        action_costs = {"inspect": 1, "ask_for_help": 1, "communication": 1},
        turn_cap = 20,               # hard Kaggle cost-control cap
    ),

    # --- scoring math (NOT action costs) ---
    scoring_weights = {"correctness": 0.3, "path_efficiency": 0.4, ...},

    # --- matched AI/human evaluation contract ---
    evaluation_conditions = EvaluationConditions(
        tool_policy = "none",
        allowed_tools = [],
        response_format = "structured_json",
        interface_mode = "graph_traversal",
    ),

    track_metadata = {...},   # track-specific fields for the scorer
)
```

---

## What the Model Sees: The Fog-of-War Graph

The graph has three visibility states per node:

- **UNEXPLORED** — the model doesn't know this node exists
- **DISCOVERED** — the model knows the node exists (it appeared as a neighbor) but hasn't seen its content
- **EXPANDED** — the model has explored or inspected this node and can see its content

At episode start, only nodes with `initial_visibility: "visible"` or `"initial"` are EXPANDED. Everything else is UNEXPLORED. The model must navigate to discover the graph.

---

## What the Model Can Do: Actions

### Base actions (all five tracks)

| Action | Cost | Effect |
|---|---|---|
| `explore(node_id)` | `edge.traversal_cost` (default 1) | Move to a neighboring node; reveals its neighbors as DISCOVERED |
| `inspect(node_id)` | 1 (from `runtime_config.action_costs`) | Reveals full `inspection_detail` of a DISCOVERED/EXPANDED node; may add to evidence |
| `get_context()` | 0 | Returns compressed state summary (position, budget, counts) |
| `submit_answer(answer, justification, confidence)` | 0 | Ends the episode |

### Track-specific actions

| Action | Track | Cost | Effect |
|---|---|---|---|
| `ask_for_help(question, help_type)` | Track 2 (metacognition) | 1 | Records in `state.help_requests`; fires `HELP_REQUESTED` event |
| `send_message(target_agent_id, content, message_type)` | Track 5 (social_cognition) | 1 | Records in `state.messages_sent`; fires `MESSAGE_SENT` event |
| `make_commitment(target_agent_id, commitment_text, commitment_type)` | Track 5 (social_cognition) | 1 | Records in `state.commitments`; fires `COMMITMENT_MADE` event |

The model only sees the actions relevant to its track. `TrackActionSchema.for_track(cognitive_track)` returns the correct per-track union passed as `schema=` to `llm.prompt()`.

---

## What Happens During an Episode

```
env = GraphScenarioEnvironment(spec)
state = env.reset()
# state.current_node = entry_node_ids[0]
# state.budget_remaining = spec.runtime_config.action_budget

for _turn in range(20):          # hard 20-turn cap
    if state.budget_remaining <= 0:
        return 0.0               # budget exhausted → score 0.0

    obs = env.render(state)      # model sees: opening_prompt (turn 0),
                                 # current node, budget, visible neighbors,
                                 # recent action history

    action = llm.prompt(obs, schema=TrackActionSchema.for_track(track))

    state = env.execute_action(state, action)
    # Each call appends ONE primary TraversalEvent + zero or more system events
    # System events (CONTRADICTION, RELEVANCE_SHIFT, etc.) never consume budget

    if state.episode_done:
        break                    # submit_answer was called

if not state.episode_done:
    return 0.0                   # turn cap reached → score 0.0
```

### Three independent termination conditions

1. `state.budget_remaining <= 0` — budget exhausted without submit → `vis = 0.0`
2. `state.episode_done == True` — model called `submit_answer` → proceed to scoring
3. Turn counter reaches 20 — hard cap regardless of budget → `vis = 0.0`

None of these is derived from `spec.optimal_steps`. That field is used only by `VISScorer.compute_stopping_quality()`.

---

## How Scoring Works

Scoring is a two-step pipeline. The environment and the VIS scorer are deliberately separated.

### Step 1: TrackScorer → ScoreCard

`env.score_episode(state, final_answer, justification)` delegates to the track's scorer and returns a `ScoreCard` dict. The ScoreCard **never contains a `"vis"` key**.

| Track | Scorer | Key dimensions |
|---|---|---|
| `learning` | `LearningScorer` | `correctness` (graded tiers), `path_efficiency`, `evidence_coverage`, `justification_quality` |
| `metacognition` | `MetacognitionScorer` | `object_score`, `calibration_score`, `revision_quality`, `verification_efficiency`, `help_seeking_appropriateness` |
| `attention` | `AttentionScorer` | `target_hit_rate`, `distractor_chase_rate`, `false_alarm_rate`, `reorientation_latency`, `cue_coverage` |
| `executive_functions` | `ExecutiveScorer` | `inhibition_failures`, `pivot_quality`, `process_scoring_focus_alignment` |
| `social_cognition` | `SocialScorer` | `correctness`, `evidence_coverage`, `causal_chain_coverage`, `red_herring_avoidance`, `disconfirmation_use` |

Each scorer also produces `behavioral_signatures` (named patterns in the trace) and `contamination_warning`.

### Step 2: VISScorer → VISResult

```python
vis_result = VISScorer().score_episode(
    state=state,
    final_answer=final_answer,
    justification=justification,
    scenario_config=spec.to_scenario_config_dict(),
    outcome_score=scorecard["outcome_score"],
    scorecard=scorecard,
)
```

The VIS formula is invariant across all tracks:

```
VIS = 0.3 × outcome_score + 0.7 × process_score
```

The VISScorer also runs contamination risk detection and citation grounding on every episode, regardless of track.

The `VISResult` dict contains `"vis"` (the leaderboard float), plus all dimension scores, `behavioral_signatures`, `contamination_warning`, `track_id`, `scenario_id`, and `seed`.

---

## How the Full Benchmark Runs

### On Kaggle

```python
# In your Kaggle notebook:
from vigil.tasks.vigil_benchmark import vigil_benchmark

%choose vigil_benchmark
```

This triggers `vigil_benchmark(llm)` which:

1. Builds a `(scenario_id, seed)` DataFrame — 150 scenarios × 3 seeds = 450 rows
2. Calls `vigil_episode.evaluate(llm=[llm], evaluation_data=df, n_jobs=2)` — runs all 450 episodes in parallel
3. Each `vigil_episode` call writes its full `VISResult` to the row's SDK artifact payload
4. After `.evaluate()` completes, reads all 450 `VISResult` objects from row artifacts
5. Runs two-stage aggregation via `FacultyProfiler`
6. Logs the full `CognitiveProfile` artifact
7. Returns the benchmark aggregate float to the leaderboard

### Locally (no Kaggle SDK)

```python
from vigil.tasks.vigil_benchmark import _vigil_benchmark_impl

class MyLLM:
    def prompt(self, obs: str, schema=None):
        # your model here
        return {"action_type": "submit_answer", "answer": "...", "justification": "...", "confidence": 0.7}

score = _vigil_benchmark_impl(MyLLM(), packs_dir="vigil/scenarios/packs/")
print(f"Benchmark score: {score:.4f}")
```

### Running a single scenario

```python
from vigil.scenarios.catalog import ScenarioCatalog
from vigil.environments.graph_scenario_env import GraphScenarioEnvironment
from vigil.tasks.vigil_benchmark import _run_episode
from vigil.scoring.vis import VISScorer

catalog = ScenarioCatalog("vigil/scenarios/packs/")
spec = catalog.load("vigil_eco_01_kethara_succession")
env = GraphScenarioEnvironment(spec)

result = _run_episode(my_llm, env, spec, seed=0)
print(f"VIS: {result['vis']:.4f}")
print(f"Outcome: {result['outcome_score']:.4f}")
print(f"Process: {result['process_score']:.4f}")
print(f"Behavioral signatures: {result['behavioral_signatures']}")
```

---

## Two-Stage Aggregation

The benchmark score is **not** a raw mean of all 450 VIS scores. It uses a two-stage pipeline that gives each cognitive faculty equal weight.

### Stage 1: aggregate_seeds()

Groups the 450 `VISResult` dicts by `scenario_id`. For each scenario (3 seeds), computes:
- `mean_vis` — mean VIS across the 3 seeds
- `vis_variance` — cross-seed variance (0.0 if only 1 seed)
- `behavioral_signatures` — mean rate of each signature across seeds
- `contamination_warning` — True if any seed triggered it

Output: 150 `ScenarioAggregate` objects.

### Stage 2: build_profile()

Groups the 150 `ScenarioAggregate` objects by `cognitive_track`. For each track (30 scenarios), computes:
- `mean_vis` — mean of the 30 scenario-level means
- `vis_variance` — variance across scenario means
- `confidence_interval_95` — `mean ± 1.96 × (std / sqrt(30))`
- `behavioral_signature_summary` — mean rate per signature across scenarios
- `low_sample_warning` — True if fewer than 5 scenarios

Output: 5 `FacultyProfile` objects (one per track).

### benchmark_aggregate()

```
benchmark_score = mean(track.mean_vis for track in profiles)
```

Each of the 5 tracks contributes equally. A track with 30 scenarios has the same weight as a track with 5 scenarios.

### The full CognitiveProfile artifact

Stored in run artifacts (not on the leaderboard):

```json
{
  "benchmark_aggregate": 0.6234,
  "cognitive_profile": {
    "learning": {"mean_vis": 0.71, "vis_std": 0.12, "n_scenarios": 30, ...},
    "metacognition": {"mean_vis": 0.58, ...},
    "attention": {"mean_vis": 0.64, ...},
    "executive_functions": {"mean_vis": 0.55, ...},
    "social_cognition": {"mean_vis": 0.60, ...}
  },
  "track_artifacts": {
    "learning": {
      "contamination_warning_rate": 0.03,
      "n_seeds_per_scenario": [3, 3, 3, ...],
      "behavioral_signature_summary": {"perseveration_rate": 0.12, ...},
      ...
    }
  },
  "repeatability_summary": {
    "n_repeated_scenarios": 150,
    "mean_cross_seed_variance": 0.008,
    "max_cross_seed_variance": 0.041
  },
  "radar_chart_data": {
    "learning": 0.71, "metacognition": 0.58, ...
  }
}
```

---

## Seed Semantics

`seed=0` runs the scenario exactly as authored. Seeds 1 and 2 apply a deterministic node-order reordering (`apply_seed_perturbation`) that preserves graph structure, answer targets, and evidence targets but changes the surface presentation. This tests whether the model's behavior is stable across equivalent graph presentations.

---

## Running the Tests

```bash
# Full test suite (760 tests)
.venv/bin/python -m pytest vigil/tests/ -q

# Property-based tests only
.venv/bin/python -m pytest vigil/tests/properties/ -q

# Single track
.venv/bin/python -m pytest vigil/tests/test_track_scorers.py -v

# Social adapter/scorer
.venv/bin/python -m pytest vigil/tests/test_social_adapter_scorer.py -v
```

### Test coverage by area

| Test file | What it covers |
|---|---|
| `test_catalog.py` | ScenarioCatalog discovery, load, validate, compile, cache |
| `test_runtime_spec.py` | RuntimeScenarioSpec field normalization, seed perturbation |
| `test_graph_scenario_env.py` | GraphScenarioEnvironment reset, execute, score_episode |
| `test_track_scorers.py` | LearningScorer dimensions and ScoreCard structure |
| `test_social_adapter_scorer.py` | SocialAdapter + SocialScorer against real Track 5 pack |
| `test_vis_scorer_extended.py` | VISScorer with and without scorecard parameter |
| `test_faculty_profiler.py` | Two-stage aggregation, CI, benchmark_aggregate |
| `test_tasks.py` | vigil_episode, vigil_benchmark, _run_episode |
| `test_evaluation_conditions.py` | tool_policy enforcement |
| `test_new_actions.py` | AskForHelp, SendMessage, MakeCommitment parse and execute |
| `properties/test_track_props.py` | Properties 1–8, 11, 13 (Hypothesis) |
| `properties/test_scoring_props.py` | VIS invariant, contamination, citation |

---

## Directory Structure

```
vigil/
├── scenarios/
│   ├── catalog.py              # ScenarioCatalog — loads and dispatches all packs
│   ├── runtime_spec.py         # RuntimeScenarioSpec, RuntimeConfig, EvaluationConditions
│   ├── loader.py               # ScenarioLoader (backward-compat shim → catalog)
│   ├── adapters/
│   │   ├── learning_adapter.py
│   │   ├── metacognition_adapter.py
│   │   ├── attention_adapter.py
│   │   ├── executive_adapter.py
│   │   └── social_adapter.py
│   └── packs/                  # 5 authored JSON packs (150 scenarios total)
├── environments/
│   ├── base.py                 # CognitiveEnvironment ABC, EnvironmentState, EventType
│   └── graph_scenario_env.py   # GraphScenarioEnvironment — shared runtime for all tracks
├── graphs/
│   ├── core.py                 # CognitiveGraph, fog-of-war visibility, from_spec()
│   └── generators.py           # ProceduralGenerator (transfer perturbations)
├── actions/
│   ├── schemas.py              # All action models + TrackActionSchema
│   └── parser.py               # parse_action() for replay and human sessions
├── scoring/
│   ├── vis.py                  # VISScorer — 0.3/0.7 formula + shared utilities
│   ├── track_scorers.py        # TrackScorer ABC + 5 per-track implementations
│   ├── faculty_profiler.py     # FacultyProfiler — two-stage aggregation
│   ├── metrics.py              # Shared scoring utilities
│   └── profile.py              # HumanBaseline, CognitiveProfile
├── tasks/
│   ├── vigil_benchmark.py      # vigil_episode + vigil_benchmark (Kaggle tasks)
│   └── track1_learning.py      # vigil_learning_benchmark (Track 1 wrapper)
├── baselines/
│   └── collector.py            # Human baseline collection
└── tests/
    ├── properties/             # Hypothesis property-based tests
    └── *.py                    # Unit tests per component
```

---

## Key Invariants

These hold across all tracks and are verified by property tests:

1. `VIS = 0.3 × outcome_score + 0.7 × process_score` — always, no exceptions
2. `env.score_episode()` never returns a dict with a `"vis"` key
3. `VISScorer.score_episode()` always returns a dict with a `"vis"` key
4. `spec.scoring_weights` never contains action cost keys (`inspect`, `ask_for_help`, `communication`)
5. System events (`CONTRADICTION`, `RELEVANCE_SHIFT`, etc.) never consume budget
6. `benchmark_aggregate = mean({track.mean_vis})` — not a raw mean of all VIS scores
7. `cognitive_track` string is the sole dispatch key — file names are ignored
8. `seed=0` returns the scenario exactly as authored; other seeds apply deterministic reorderings
