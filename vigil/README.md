# Vigil: Stateful Cognitive Graph Benchmark Framework

**Track 1: Learning** - Google DeepMind × Kaggle "Measuring AGI" Hackathon

## Overview

Vigil is a benchmark framework that creates **stateful cognitive graph environments** where AI models must explore, learn, and demonstrate cognitive abilities through their actions - not just answer questions.

### Core Innovation

Instead of static QA benchmarks, Vigil places models in interactive graph environments where they must:
- Choose entry points
- Navigate through nodes and edges
- Make decisions based on discovered information
- Submit conclusions with evidence

### Cognitive Abilities Tested (Track 1: Learning)

| Sub-ability | Description | Scenario |
|-------------|-------------|----------|
| **Concept Formation** | Abstracting key features to form categories | Nodes share hidden core features |
| **Associative Learning** | Learning relationships between events | Paired associations |
| **Reinforcement Learning** | Learning from rewards/punishments | Navigate to rewards, avoid penalties |
| **Observational Learning** | Learning by watching demonstrations | *(coming soon)* |
| **Procedural Learning** | Improving through practice | Skill acquisition over rounds |
| **Language Learning** | Learning new syntax/vocabulary | Novel grammar rules |

## Quick Start

### On Kaggle (Recommended)

1. **Create a new Kaggle notebook** at https://www.kaggle.com/benchmarks/tasks/new

2. **Add the vigil package** by uploading the `vigil/` folder or using:
```python
!pip install vigil  # or copy vigil/ folder
```

3. **Run the provided notebook**: `vigil_kaggle_notebook.ipynb`

4. **Submit to leaderboard** - The notebook ends with `%choose concept_formation_learning`

### Local Testing

```bash
# Run local tests
cd vigil
python run_kaggle_test.py

# Or run the full test suite
python test_vigil.py
```

## Kaggle Integration

### Task Definition Pattern

Vigil uses the Kaggle Benchmarks SDK pattern:

```python
import kaggle_benchmarks as kbench
from vigil.environments.concept_formation import ConceptFormationEnv

@kbench.task(name="concept_formation_learning")
def concept_formation_task(llm, difficulty: int = 2, seed: int = 42) -> float:
    """
    Track 1 Learning: Concept Formation Test

    Returns:
        Final score (0.0 - 1.0)
    """
    # Load environment
    env = ConceptFormationEnv(difficulty=difficulty, seed=seed)
    state = env.reset()

    # Exploration loop
    for turn in range(15):
        if state.budget_remaining <= 0:
            break

        # Get action from LLM
        response = llm.prompt(f"Your action: {env.get_available_actions(state)}")
        action = parse_action(response)

        if action.action_type == ActionType.SUBMIT:
            final_answer = llm.prompt("What is the rule?")
            scores = env.score_exploration(state, final_answer)
            return scores["final_score"]

    return 0.0  # Timeout
```

### Leaderboard Submission

The final cell of the notebook uses the `%choose` magic:

```python
%choose concept_formation_learning
```

This designates which task is submitted to the Kaggle leaderboard.

## Architecture

### Directory Structure

````
vigil/
├── environments/         # Cognitive environment implementations
│   ├── base.py          # CognitiveEnvironment ABC
│   ├── concept_formation.py
│   ├── associative.py
│   └── reinforcement.py
├── graphs/              # Graph data structures
│   └── core.py          # CognitiveGraph, GraphNode, GraphEdge
├── scenarios/           # Scenario definitions (JSON-based)
│   ├── loader.py        # JSON scenario loader
│   └── schemas/         # JSON scenario files (6 scenarios)
├── actions/             # Action handling
│   ├── parser.py        # Parse model actions
│   └── schemas.py       # GraphAction dataclass
├── scoring/             # Scoring engine
│   ├── metrics.py       # Multi-metric scoring functions
│   └── profile.py       # CognitiveProfile dataclass
├── tasks/               # Kaggle task definitions
│   └── track1_learning.py
├── notebooks/           # Jupyter notebooks
│   ├── vigil_kaggle_notebook.ipynb  # Main Kaggle notebook
│   └── vigil_track1_learning.ipynb  # Original reference
└── run_kaggle_test.py   # Local test runner
````

### Key Components

#### 1. CognitiveEnvironment (Base Class)
All environments implement this interface:
- `reset()` - Initialize episode
- `get_available_actions()` - Get action menu
- `execute_action()` - Run action
- `score_exploration()` - Multi-metric scoring

#### 2. Scenario Loader
Loads configurations from JSON files:
```python
from vigil.scenarios.loader import ScenarioLoader
loader = ScenarioLoader()
config = loader.load("concept_formation")
```

#### 3. Scoring Engine
Multi-metric cognitive profiles:
- **Correctness**: Task success (50%)
- **Efficiency**: Path optimization (20%)
- **Evidence Quality**: Evidence collection (20%)
- **Calibration**: Confidence-accuracy match (10%)
- **Recovery**: Adaptation after errors (variable)

## Scenario Format

Scenarios are defined in JSON files in `vigil/scenarios/schemas/`:

```json
{
  "scenario_id": "concept_formation_v1",
  "cognitive_track": "learning",
  "sub_ability": "concept_formation",
  "graph_config": {
    "num_nodes": 15,
    "num_categories": 3
  },
  "hidden_rule": {
    "type": "category_by_core_features",
    "description": "Nodes in same category share 3+ core features"
  },
  "scoring_weights": {
    "correctness": 0.50,
    "efficiency": 0.20,
    "evidence_quality": 0.20,
    "calibration": 0.10
  }
}
```

## Adding New Scenarios

1. Create JSON file in `vigil/scenarios/schemas/`
2. Implement environment class inheriting from `CognitiveEnvironment`
3. Add task definition in `vigil/tasks/`

## Running the Benchmark

### Full Dataset Evaluation

```python
import pandas as pd
import kaggle_benchmarks as kbench

@kbench.task(name="single_graph_instance")
def single_instance(llm, difficulty: int, seed: int) -> bool:
    score = concept_formation_task.run(llm, difficulty=difficulty, seed=seed)
    return score > 0.5

@kbench.task(name="concept_formation_full_benchmark")
def full_benchmark(llm, df: pd.DataFrame) -> tuple[float, float]:
    with kbench.client.enable_cache():
        runs = single_instance.evaluate(
            llm=[llm],
            evaluation_data=df,
            n_jobs=4,
            timeout=300
        )

    eval_df = runs.as_dataframe()
    return float(eval_df.result.mean()), float(eval_df.result.std())
```

## Human Baseline Collection

Human baselines are collected separately using a Streamlit app:

```bash
# Run human baseline collection (separate from Kaggle)
streamlit run vigil/notebooks/human_baseline_app.py
```

Human data is used to compute percentiles in the cognitive profile.

## Evaluation Metrics

| Metric | Description | Default Weight |
|--------|-------------|----------------|
| Correctness | Binary pass/fail on rule identification | 50% |
| Efficiency | Optimal path / actual path | 20% |
| Evidence Quality | Evidence nodes collected | 20% |
| Calibration | Confidence matches correctness | 10% |
| Recovery | Adaptation after errors | variable |

## Testing

```bash
# Run full test suite
cd vigil
python test_vigil.py

# Run local Kaggle simulation
python run_kaggle_test.py
```

## References

- [DeepMind AGI Cognitive Framework Paper](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/30952288/2da445e3-d7cf-4788-90dd-94a4df00eafe/measuring-progress-toward-agi-a-cognitive-framework.pdf)
- [Kaggle Benchmarks SDK](https://github.com/Kaggle/kaggle-benchmarks)
- [Kaggle Benchmarks Quick Start](https://www.kaggle.com/docs/benchmarks#intro)
- [Chollet's Measure of Intelligence](https://arxiv.org/abs/1911.01547)
- [ARC-AGI Benchmark](https://arcprize.org/)

## License

Apache 2.0
