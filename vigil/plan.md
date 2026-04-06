Vigil: Stateful Cognitive Graph Benchmark Framework

 Context

 This plan implements a benchmark framework for the Google DeepMind × Kaggle "Measuring AGI"
 Hackathon ($200K prize pool, deadline April 16, 2026). The benchmark targets Track 1: Learning
  from DeepMind's cognitive taxonomy.

 Core Innovation: Instead of static QA benchmarks, Vigil creates stateful cognitive graph
 environments where AI models must explore, learn, and demonstrate cognitive abilities through
 their actions. The model enters a hidden world graph and must choose entry points, navigate
 nodes/edges, make decisions, and submit conclusions.

 Problem Statement: Current AI benchmarks measure recall, not genuine intelligence. DeepMind's
 framework identifies Learning as having the largest benchmark coverage gap. The key insight
 from the research:
 - Learning = "ability to acquire new knowledge through experience, study, or instruction"
 - Current LLMs only learn during training or in-context (not persistently)
 - Valid benchmarks must control for prior knowledge and measure acquisition efficiency

 Requirements

 Must-Have Requirements

 1. Kaggle SDK Compliance
   - Tasks decorated with @kbench.task
   - First parameter must be llm
   - Return type annotations required (float, bool, dict, tuple)
   - Single task per notebook for leaderboard submission
 2. Modular Scenario Architecture
   - Scenarios stored as separate JSON files
   - Hot-swappable scenario definitions
   - Extensible to add new scenarios without code changes
   - Support for multiple tracks (Learning, Metacognition, Attention, Executive Functions,
 Social Cognition)
 3. Cognitive Profile Scoring
   - Multi-metric scoring (not just accuracy)
   - Scores: correctness, path efficiency, evidence quality, calibration, recovery
   - Human baseline comparison capability
   - Results serialized to run.json
 4. Procedural Graph Generation
   - Generate varied graph instances from JSON templates
   - Control difficulty levels
   - Ensure held-out test sets (prevent contamination)

 Technical Constraints (from Kaggle SDK)

 - No external servers (all code in notebook)
 - No persistent state between runs
 - State serialized to run.json
 - In-memory graph representation (NetworkX or pure Python)

 Architecture

 Directory Structure

 vigil/
 ├── __init__.py
 ├── environments/           # Cognitive environment implementations
 │   ├── __init__.py
 │   ├── base.py            # CognitiveEnvironment ABC
 │   ├── concept_formation.py
 │   ├── associative.py
 │   ├── reinforcement.py
 │   ├── observational.py
 │   └── procedural.py
 ├── graphs/                # Graph data structures & generators
 │   ├── __init__.py
 │   ├── core.py            # Graph, Node, Edge classes
 │   └── generators.py      # Procedural generation
 ├── scenarios/             # Scenario definitions (JSON-based)
 │   ├── __init__.py
 │   ├── loader.py          # JSON scenario loader
 │   └── schemas/           # JSON schema definitions
 │       ├── concept_formation.json
 │       ├── associative.json
 │       └── reinforcement.json
 ├── actions/               # Action handling
 │   ├── __init__.py
 │   ├── parser.py          # Parse model actions from text
 │   └── schemas.py         # GraphAction dataclass
 ├── scoring/               # Scoring engine
 │   ├── __init__.py
 │   ├── metrics.py         # Scoring functions
 │   └── profile.py         # CognitiveProfile dataclass
 ├── tasks/                 # Kaggle task definitions
 │   ├── __init__.py
 │   └── track1_learning.py # @kbench.task decorators
 └── utils/
     ├── __init__.py
     └── serialization.py   # JSON serialization helpers

 Key Components

 1. Base Environment (environments/base.py)

 Abstract base class defining the interface:
 - reset() → EnvironmentState
 - get_available_actions(state) → str (action menu)
 - execute_action(state, action) → (success, observation)
 - score_exploration(state, final_answer) → Dict[str, float]
 - verify_rule(answer) → bool

 2. Graph State (graphs/core.py)

 Dataclasses for graph representation:
 - GraphNode: id, features, category (hidden), metadata
 - GraphEdge: source, target, relation_type, weight
 - CognitiveGraph: nodes, edges, hidden_rules

 3. Scenario Loader (scenarios/loader.py)

 Loads JSON scenario definitions:
 - Graph topology templates
 - Node/edge generation rules
 - Hidden rule encoders
 - Difficulty parameters

 4. Action Parser (actions/parser.py)

 Parses model's natural language into structured actions:
 - expand:node_id → GraphAction
 - inspect:node_id → GraphAction
 - submit:answer → GraphAction
 - Uses regex fallback + structured output

 5. Scoring Engine (scoring/)

 Multi-metric cognitive profile:
 - correctness: Binary pass/fail on rule identification
 - efficiency: optimal_path / actual_path
 - evidence_quality: visited_evidence_nodes / required_evidence
 - calibration: 1 - |confidence - correctness|
 - recovery: Adaptation after contradiction

 JSON Scenario Schema (Example)

 {
   "scenario_id": "concept_formation_v1",
   "cognitive_track": "learning",
   "sub_ability": "concept_formation",
   "graph_config": {
     "num_nodes": 15,
     "num_categories": 3,
     "features_per_node": 5,
     "core_features_per_category": 3
   },
   "hidden_rule": {
     "type": "category_by_core_features",
     "description": "Nodes in same category share 3+ core features"
   },
   "scoring_weights": {
     "correctness": 0.5,
     "efficiency": 0.2,
     "evidence_quality": 0.2,
     "calibration": 0.1
   },
   "difficulty_levels": [1, 2, 3]
 }

 Implementation Phases

 Phase 1: Core Infrastructure (Week 1)

 - Create vigil/ directory structure
 - Implement CognitiveEnvironment ABC
 - Implement CognitiveGraph and state classes
 - Implement scenario JSON loader
 - Create empty JSON scenario files

 Phase 2: First Environment (Week 2)

 - Implement ConceptFormationEnv
 - Implement action parser
 - Implement scoring metrics
 - Create @kbench.task definition
 - Test in Kaggle notebook

 Phase 3: Dataset Evaluation (Week 3)

 - Implement procedural graph generation
 - Create scenario configs for multiple difficulty levels
 - Implement .evaluate() pattern for dataset runs
 - Add human baseline collection (separate Streamlit app)

 Phase 4: Additional Scenarios (Week 4)

 - Implement AssociativeLearningEnv
 - Implement ReinforcementLearningEnv
 - Generate full benchmark dataset
 - Submit to Kaggle leaderboard
 ┌────────────────────────────────┬──────────────────────────┐
 │              File              │         Purpose          │
 ├────────────────────────────────┼──────────────────────────┤
 │ vigil/__init__.py              │ Package initialization   │
 ├────────────────────────────────┼──────────────────────────┤
 │ vigil/environments/base.py     │ CognitiveEnvironment ABC │
 ├────────────────────────────────┼──────────────────────────┤
 │ vigil/graphs/core.py           │ Graph data structures    │
 ├────────────────────────────────┼──────────────────────────┤
 │ vigil/scenarios/loader.py      │ JSON scenario loader     │
 ├────────────────────────────────┼──────────────────────────┤
 │ vigil/actions/parser.py        │ Action parsing logic     │
 ├────────────────────────────────┼──────────────────────────┤
 │ vigil/scoring/metrics.py       │ Scoring functions        │
 ├────────────────────────────────┼──────────────────────────┤
 │ vigil/tasks/track1_learning.py │ Kaggle task definitions  │
 └────────────────────────────────┴──────────────────────────┘

 Scenario JSON Files

 ┌────────────────────────────────────────────────┬────────────────────────┐
 │                      File                      │   Cognitive Ability    │
 ├────────────────────────────────────────────────┼────────────────────────┤
 │ vigil/scenarios/schemas/concept_formation.json │ Concept Formation      │
 ├────────────────────────────────────────────────┼────────────────────────┤
 │ vigil/scenarios/schemas/associative.json       │ Associative Learning   │
 ├────────────────────────────────────────────────┼────────────────────────┤
 │ vigil/scenarios/schemas/reinforcement.json     │ Reinforcement Learning │
 ├────────────────────────────────────────────────┼────────────────────────┤
 │ vigil/scenarios/schemas/observational.json     │ Observational Learning │
 ├────────────────────────────────────────────────┼────────────────────────┤
 │ vigil/scenarios/schemas/procedural.json        │ Procedural Learning    │
 ├────────────────────────────────────────────────┼────────────────────────┤
 │ vigil/scenarios/schemas/language.json          │ Language Learning      │
 └────────────────────────────────────────────────┴────────────────────────┘

 Reusable Patterns from References

 From Kaggle Benchmarks CI

 1. Task Pattern: @kbench.task decorator with llm as first param
 2. Structured Output: Use schema=GraphAction for parsing
 3. Dataset Evaluation: Use .evaluate() with pandas DataFrame
 4. Multi-metric Return: Return dict or tuple[float, float]

 From Tic-Tac-Toe Example

 1. Game Loop Pattern: State → Prompt → Execute → Score
 2. Abstract Base Class: Define interface all environments implement
 3. Action Schema: Dataclass for structured actions

 From LangWatch

 1. Trace Collection: Capture action sequences in state
 2. Multi-metric Evaluation: Separate scoring functions per metric

 From TrustGraph

 1. Flow Architecture: Isolated processing instances
 2. Graph Representation: Node/edge dicts with metadata
 3. Configuration Separation: JSON-based config files

 Verification Steps

 End-to-End Test

 1. Create vigil/ directory structure
 2. Implement base classes and first environment
 3. Create sample JSON scenario
 4. Define @kbench.task in notebook
 5. Run task with kbench.llm
 6. Verify task.json and run.json generated
 7. Check leaderboard submission

 Testing Checklist

 - Environment instantiates from JSON config
 - Model can explore graph via actions
 - Actions are parsed correctly
 - Scoring returns valid metrics
 - Results serialize to run.json
 - Task runs in Kaggle notebook
 - Leaderboard displays results

 Success Criteria

 1. Framework supports hot-swapping scenario JSON files without code changes
 2. New cognitive tracks can be added by creating new environment classes
 3. Scenarios are fully defined in JSON (graph structure, rules, scoring)
 4. Benchmark runs on Kaggle and produces valid leaderboard entry
 5. Multi-metric cognitive profiles generated for each model run


---


  Summary: Vigil Framework Implementation Complete

  I've built the complete Vigil: Stateful Cognitive Graph Benchmark Framework
   for the Google DeepMind × Kaggle "Measuring AGI" Hackathon.

  Directory Structure Created

  vigil/
  ├── __init__.py                 # Package initialization
  ├── README.md                   # Documentation
  ├── test_vigil.py              # Test suite (all tests pass)
  ├── environments/
  │   ├── base.py                # CognitiveEnvironment ABC
  │   ├── concept_formation.py   # Concept Formation scenario
  │   ├── associative.py         # Associative Learning scenario
  │   └── reinforcement.py       # Reinforcement Learning scenario
  ├── graphs/
  │   └── core.py                # CognitiveGraph, GraphNode, GraphEdge
  ├── scenarios/
  │   ├── loader.py              # JSON scenario loader
  │   └── schemas/
  │       ├── concept_formation.json
  │       ├── associative.json
  │       ├── reinforcement.json
  │       ├── observational.json
  │       ├── procedural.json
  │       └── language.json
  ├── actions/
  │   ├── parser.py              # Action parsing from natural language
  │   └── schemas.py             # GraphAction dataclass
  ├── scoring/
  │   ├── metrics.py             # Multi-metric scoring functions
  │   └── profile.py             # CognitiveProfile dataclass
  ├── tasks/
  │   └── track1_learning.py     # Kaggle task definitions
  ├── utils/
  │   └── serialization.py       # JSON utilities
  └── notebooks/
      └── vigil_track1_learning.ipynb  # Kaggle notebook template

  Key Features Implemented

  1. 6 Scenario JSON Files - Empty templates for all Learning sub-abilities
  (concept formation, associative, reinforcement, observational, procedural,
  language)
  2. 3 Environment Implementations - Working environments for concept
  formation, associative learning, and reinforcement learning
  3. Multi-Metric Scoring - Correctness, efficiency, evidence quality,
  calibration, recovery
  4. Action Parser - Parses natural language into structured actions (expand,
   inspect, backtrack, submit)
  5. Kaggle-Compliant Tasks - Ready for @kbench.task decorator integration

  Test Results

  All 6 tests pass:
  - Imports
  - Scenario loader
  - Graph generation
  - Action parser
  - Concept formation environment
  - Scoring engine

---


  Summary: Vigil Framework - Kaggle SDK Integration Complete

  Files Created/Updated

  ┌─────────────────────────────────────────────┬─────────────────────────┐
  │                    File                     │         Purpose         │
  ├─────────────────────────────────────────────┼─────────────────────────┤
  │                                             │ Updated - Now contains  │
  │ vigil/tasks/track1_learning.py              │ actual @kbench.task     │
  │                                             │ decorated functions     │
  ├─────────────────────────────────────────────┼─────────────────────────┤
  │ vigil/notebooks/vigil_kaggle_notebook.ipynb │ New - Main Kaggle       │
  │                                             │ notebook for submission │
  ├─────────────────────────────────────────────┼─────────────────────────┤
  │ vigil/notebooks/requirements.txt            │ New - Dependencies file │
  ├─────────────────────────────────────────────┼─────────────────────────┤
  │ vigil/run_kaggle_test.py                    │ New - Local test runner │
  ├─────────────────────────────────────────────┼─────────────────────────┤
  │ vigil/README.md                             │ Updated - Complete      │
  │                                             │ documentation           │
  └─────────────────────────────────────────────┴─────────────────────────┘

  Key Integration Points

  1. Task Decorator Pattern: All tasks now use @kbench.task decorator
  2. Return Type Annotations: All tasks return -> float for proper scoring
  3. LLM First Parameter: All tasks accept llm as first parameter
  4. %choose Magic: Notebook ends with %choose concept_formation_learning

  Test Results

  - ✅ 6/6 framework tests pass
  - ✅ Local Kaggle simulation passes
  - ✅ All imports work correctly
  - ✅ Scenario loading works (6 scenarios available)
  - ✅ Action parsing functional
  - ✅ Scoring engine produces multi-metric profiles

  Directory Structure (Final)

  vigil/
  ├── environments/       # 3 environment implementations
  ├── graphs/            # Graph data structures
  ├── scenarios/         # 6 JSON scenario files
  ├── actions/           # Action parsing
  ├── scoring/           # Multi-metric scoring
  ├── tasks/             # Kaggle @kbench.task definitions
  ├── notebooks/         # Kaggle notebooks
  ├── test_vigil.py      # Test suite
  └── run_kaggle_test.py # Local runner

  Next Steps for Kaggle Submission

  1. Upload vigil_kaggle_notebook.ipynb to Kaggle
  2. Run all cells to verify environment
  3. Click "Save Version" to submit to leaderboard
  4. The %choose magic handles task registration
