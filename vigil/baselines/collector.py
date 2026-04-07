"""
Human baseline collection for Vigil benchmark.

Runs human participants through the same environment episodes used for
model evaluation, then saves results as JSON for percentile computation.

Usage:
    from vigil.baselines.collector import collect_human_session, load_baseline
    from vigil.environments.graph_scenario_env import GraphScenarioEnvironment
    from vigil.scenarios.catalog import ScenarioCatalog

    catalog = ScenarioCatalog()
    spec = catalog.load("vigil_eco_01_kethara_succession")
    env = GraphScenarioEnvironment(spec)

    # Collect one participant's session (interactive terminal input)
    state = collect_human_session(env, participant_id="p001")

    # Load all collected baselines for a scenario
    baseline = load_baseline("vigil_eco_01_kethara_succession")
    percentile = baseline.compute_percentile(0.72, "vis")

Requirements: 18.1, 18.4
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from vigil.scoring.profile import HumanBaseline
from vigil.scoring.vis import VISScorer

_BASELINES_DIR = Path(__file__).parent
_SCORER = VISScorer()


def collect_human_session(
    env: Any,
    participant_id: str,
    input_fn: Optional[Callable[[str], Any]] = None,
    save: bool = True,
) -> Dict[str, Any]:
    """
    Run one human participant through an environment episode.

    Uses env.run_human_session() which applies the same 20-turn cap and
    action API as model evaluation (Req 18.1).

    Args:
        env: A CognitiveEnvironment instance (already configured with scenario/seed)
        participant_id: Unique identifier for this participant
        input_fn: Callable (obs: str) -> Any for human input.
                  Defaults to terminal input via input().
        save: Whether to append results to the baseline JSON file.

    Returns:
        Dict with participant_id, vis_scores, and raw state summary.
    """
    if input_fn is None:
        input_fn = _terminal_input_fn

    # Run the session using the same loop as model evaluation
    state = env.run_human_session(input_fn)

    # Extract answer and justification from last submit event
    final_answer = ""
    justification = ""
    from vigil.environments.base import EventType
    for event in reversed(state.action_history):
        if event.event_type == EventType.SUBMIT_ANSWER:
            final_answer = event.params.get("answer", "")
            justification = event.params.get("justification", "")
            break

    # Score the session
    episode_scores = env.score_episode(state, final_answer, justification)
    outcome_score = episode_scores.get("correctness", 0.0)

    vis_result = _SCORER.score_episode(
        state=state,
        final_answer=final_answer,
        justification=justification,
        scenario_config=env.scenario_config,
        outcome_score=outcome_score,
        judge_llm=None,  # No judge for human sessions
    )

    participant_record = {
        "participant_id": participant_id,
        "scenario_id": env.scenario_config.get("scenario_id", "unknown"),
        "vis": vis_result["vis"],
        "outcome_score": vis_result["outcome_score"],
        "process_score": vis_result["process_score"],
        "exploration_efficiency": vis_result["exploration_efficiency"],
        "learning_rate": vis_result["learning_rate"],
        "adaptivity": vis_result["adaptivity"],
        "recovery": vis_result["recovery"],
        "stopping_quality": vis_result["stopping_quality"],
        "metacognition": vis_result["metacognition"],
        "contamination_risk": vis_result["contamination_risk"],
        "actions_taken": len(state.action_history),
        "evidence_nodes": len(state.evidence_nodes),
    }

    if save:
        scenario_id = env.scenario_config.get("scenario_id", "unknown")
        _append_to_baseline(scenario_id, participant_record)

    return participant_record


def collect_baseline(
    env_factory: Callable[[], Any],
    num_participants: int = 10,
    input_fn: Optional[Callable[[str], Any]] = None,
) -> HumanBaseline:
    """
    Collect baseline data from multiple participants (Req 18.4).

    Args:
        env_factory: Callable that returns a fresh CognitiveEnvironment instance.
                     Called once per participant to ensure independent episodes.
        num_participants: Number of participants to collect (minimum 10 per Req 18.4)
        input_fn: Human input callable. Defaults to terminal input.

    Returns:
        HumanBaseline with all collected participant scores.
    """
    if num_participants < 10:
        print(f"Warning: Req 18.4 requires at least 10 participants, got {num_participants}")

    records = []
    for i in range(num_participants):
        env = env_factory()
        participant_id = f"participant_{i + 1:03d}"
        print(f"\n--- Participant {i + 1}/{num_participants} ---")
        record = collect_human_session(env, participant_id, input_fn=input_fn, save=True)
        records.append(record)
        print(f"VIS score: {record['vis']:.3f}")

    # Build and return HumanBaseline
    scenario_id = records[0]["scenario_id"] if records else "unknown"
    baseline = HumanBaseline(scenario_id=scenario_id)
    for record in records:
        baseline.add_participant({k: v for k, v in record.items() if isinstance(v, float)})

    return baseline


def load_baseline(scenario_id: str) -> Optional[HumanBaseline]:
    """
    Load a saved HumanBaseline from JSON.

    Args:
        scenario_id: The scenario_id string (e.g. "concept_formation_v1")

    Returns:
        HumanBaseline if file exists, None otherwise.
    """
    path = _BASELINES_DIR / f"{scenario_id}_baseline.json"
    if not path.exists():
        return None
    with open(path, "r") as f:
        data = json.load(f)
    return HumanBaseline.from_dict(data)


def save_baseline(baseline: HumanBaseline) -> Path:
    """
    Save a HumanBaseline to JSON.

    Args:
        baseline: HumanBaseline to save

    Returns:
        Path where the file was saved.
    """
    path = _BASELINES_DIR / f"{baseline.scenario_id}_baseline.json"
    with open(path, "w") as f:
        json.dump(baseline.to_dict(), f, indent=2)
    return path


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _append_to_baseline(scenario_id: str, record: Dict[str, Any]) -> None:
    """Append one participant record to the baseline JSON file."""
    path = _BASELINES_DIR / f"{scenario_id}_baseline.json"

    if path.exists():
        with open(path, "r") as f:
            data = json.load(f)
        baseline = HumanBaseline.from_dict(data)
    else:
        baseline = HumanBaseline(scenario_id=scenario_id)

    # Add only float fields as participant scores
    scores = {k: v for k, v in record.items() if isinstance(v, float)}
    baseline.add_participant(scores)

    with open(path, "w") as f:
        json.dump(baseline.to_dict(), f, indent=2)


def _terminal_input_fn(obs: str) -> str:
    """Default input function: print observation and read from terminal."""
    print("\n" + "=" * 60)
    print(obs)
    print("=" * 60)
    return input("Your action: ").strip()
