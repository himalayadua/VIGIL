# Track 3 Scenario Validation Checklist

## Executive Functions

This document is the working validation checklist for deciding whether a proposed Vigil scenario genuinely measures `Track 3: Executive Functions` in the DeepMind AGI framework, rather than generic reasoning, static QA, long-context retrieval, or pure memory.

It is meant to be used before scenario generation, during scenario review, and before benchmark acceptance.

## Purpose

This checklist is designed to answer one core question:

`Does this scenario force the model to regulate and orchestrate thought and action in pursuit of a goal under meaningful constraints?`

If the answer is no, then it is not a strong Track 3 scenario.

## How To Use This Checklist

- Treat `Core Requirements` as mandatory unless there is a very strong reason not to.
- Treat `Strong Preferred Properties` as features that materially improve scenario quality and benchmark validity.
- Treat `Scenario-Type-Specific Checks` as required only when the scenario claims to measure that specific executive sub-ability or scenario family.
- Use `Rejection Criteria` as hard blockers.
- A scenario does not need to satisfy every preferred property, but it should satisfy most of the core requirements and produce clearly interpretable executive-control behavior.

## 1. Core Requirements

### 1.1 Goal-Directed Control

- Does the scenario require the agent to pursue an explicit or discoverable goal over multiple steps?
- Does success depend on keeping that goal active while acting?
- Would the scenario still be meaningful if the final answer text were hidden and only the behavior trace were available?
- Does the task measure control of behavior in service of a goal, not just correctness of a final response?
- Would a system that "knows what to do" but cannot regulate its behavior still fail here?

### 1.2 Sequential Dependence

- Does the order of actions materially affect success, cost, or feasibility?
- Do earlier choices shape later options or consequences?
- Is there a real difference between coherent multi-step control and opportunistic local moves?
- Would one-shot reasoning be insufficient without actual sequential execution?

### 1.3 Control Pressure

- Does the scenario create at least one genuine need for one or more of the following:
  - goal maintenance
  - planning
  - inhibitory control
  - cognitive flexibility
  - conflict resolution
  - working memory
- Is that pressure behaviorally visible rather than merely implied in the story?
- If all of these could be ignored and the task would still be easy, is the scenario actually testing executive function?

### 1.4 Executive Function Rather Than Generic Difficulty

- Is the difficulty coming from control demands rather than only from reasoning complexity?
- Could a model with strong static reasoning but weak control still fail?
- Does the scenario expose the difference between:
  - knowing
  - deciding
  - sequencing
  - suppressing
  - switching
  - and carrying out a goal-aligned policy?

### 1.5 Human Solvability

- Is the scenario human-solvable with the same interface and tool constraints?
- Does the difficulty come from control structure rather than arbitrary obscurity?
- Could a human baseline reasonably be collected for this scenario?
- Would human behavior traces be meaningfully comparable to model traces?

## 2. Environment Requirements

### 2.1 Graph As Executive Environment

- Is the graph a stateful environment for action, not just a graph-shaped description?
- Does traversal materially affect progress, feasibility, or cost?
- Do node choices, ordering, and subgoal paths matter?
- Does the graph support meaningful action primitives such as:
  - exploration
  - inspection
  - commitment
  - backtracking
  - replanning
  - submission
  - stopping

### 2.2 Constraint Structure

- Does the scenario impose meaningful constraints such as:
  - step budget
  - time budget
  - resource budget
  - expansion budget
  - switching cost
  - interruption cost
  - dependency order
  - mutually exclusive actions
- Do these constraints make executive control necessary rather than decorative?
- Could brute force still solve the task too easily despite the intended constraints?

### 2.3 Stateful Consequences

- Do actions have consequences for what becomes possible, costly, blocked, or risky?
- Can poor sequencing create later problems?
- Can good early planning reduce later cost?
- Is there a meaningful difference between reversible and irreversible mistakes?

### 2.4 Partial Observability

- Is partial observability present when it helps the executive demand?
- If the whole graph is visible, does the task still create planning, inhibition, or switching pressure?
- If the whole graph is hidden, is the task still fair and interpretable?
- Is the observability regime chosen to strengthen executive-function measurement rather than mimic Track 1 by default?

### 2.5 Tempting But Wrong Options

- Are there salient, habitual, default, or locally attractive actions that should be suppressed?
- Is at least one poor but tempting path behaviorally reachable?
- Can the scenario expose impulsive, greedy, or perseverative action tendencies?

### 2.6 Replanning Opportunities

- Can plans fail or become suboptimal as new information arrives?
- Is there at least one moment where the agent may need to revise an action sequence?
- Is successful replanning visible in the trace?
- Can the benchmark distinguish between stubborn continuation and intelligent course correction?

### 2.7 Conflict Structure

- Does the scenario contain competing goals, constraints, cues, or action recommendations?
- Must the model choose among them rather than follow a single obvious policy?
- Is there a principled way to evaluate whether conflict was resolved well?

## 3. Executive-Function Alignment

### 3.1 DeepMind Executive Function Definition Alignment

- Does the scenario match the idea of higher-order control enabling goal-directed behavior?
- Does it measure regulation and orchestration of thought and action rather than domain knowledge?
- Does it test control under constraints rather than generic success?

### 3.2 Unity And Diversity Of Executive Functions

- Does the scenario isolate one executive sub-ability cleanly, or intentionally combine several in a controlled way?
- If multiple sub-abilities are involved, is the primary target explicit?
- Can likely failure modes still be interpreted instead of collapsing into "the task was hard"?

### 3.3 Evidence Of Real Executive Control

- Would a good score be evidence of genuine executive control rather than lucky task completion?
- Is the control signal visible in the trajectory of actions?
- Can the scenario reveal the difference between:
  - lucky success
  - brute-force success
  - shallow heuristic success
  - and genuinely controlled, goal-directed behavior?

## 4. Executive Sub-Ability Coverage

Every scenario should either isolate one sub-ability cleanly or intentionally combine several in a controlled and explainable way.

### 4.1 Goal Setting And Maintenance

- Is there a clear overall objective or target state?
- Must the agent maintain the goal over several steps?
- Are there opportunities for distraction, drift, or goal neglect?
- Can the scenario reveal whether the model:
  - forgets the main goal
  - confuses subgoals with the main goal
  - loses the objective after interruption
  - or pursues locally attractive but globally irrelevant branches?

### 4.2 Planning

- Does the scenario require thinking ahead rather than greedy local choice?
- Are there action sequences where short-term convenience harms long-term success?
- Can the benchmark distinguish:
  - no plan
  - shallow plan
  - brittle plan
  - robust multi-step plan
- Can it expose failures such as:
  - poor subgoal order
  - lack of lookahead
  - weak branch pruning
  - inability to anticipate constraints

### 4.3 Inhibitory Control

- Is there a dominant, salient, habitual, or default action that should be suppressed?
- Must the model inhibit an intuitive but wrong move?
- Are inhibition failures visible in the trace?
- Can the benchmark detect:
  - impulsive action
  - premature submission
  - repeated attraction to low-value options
  - failure to stop a no-longer-valid policy?

### 4.4 Cognitive Flexibility

- Does the scenario require switching strategy, rule set, representation, or subtask?
- Is there a meaningful need to abandon a formerly good policy?
- Can the benchmark reveal:
  - perseveration
  - brittle commitment
  - delayed switching
  - over-switching without cause
  - confusion after policy shifts?

### 4.5 Conflict Resolution

- Does the scenario present competing goals, contradictory cues, or incompatible constraints?
- Must the agent arbitrate rather than simply solve a single clean objective?
- Can the benchmark reveal whether the model:
  - collapses under contradiction
  - chooses arbitrarily
  - ignores one side of the conflict
  - or resolves tradeoffs coherently?

### 4.6 Working Memory

- Must the model actively hold and manipulate intermediate state while pursuing the goal?
- Is the task harder than simply rereading one visible fact?
- Does success require one or more of the following:
  - tracking constraints
  - updating commitments
  - combining intermediate results
  - mentally simulating future states
  - carrying unresolved dependencies forward
- Is the working-memory burden high enough to matter but not so high that the scenario becomes an unfair memory stress test?

## 5. Control Failure And Recovery

### 5.1 Goal Drift Pressure

- Is there at least one meaningful opportunity for goal drift?
- Does the scenario pressure the model to stay aligned with the main objective despite distraction?
- Is goal-maintenance quality observable and scoreable?

### 5.2 Replanning Quality

- Can the trace show whether the model:
  - noticed a failed plan
  - abandoned an outdated plan
  - reformulated a better sequence
  - or kept forcing a bad policy?
- Is successful replanning behaviorally visible?

### 5.3 Perseveration And Recovery

- Are there diagnostically meaningful dead ends, stale strategies, or invalidated policies?
- Would a careful solver recognize and leave them?
- Can the benchmark measure whether the model:
  - got stuck
  - kept repeating a failing strategy
  - recovered quickly
  - or over-corrected into aimless switching?

## 6. Constraint And Conflict Design

### 6.1 Constraint Quality

- Are the scenario constraints cognitively meaningful rather than arbitrary?
- Do they create real tradeoffs instead of merely shrinking the search space?
- Could the constraint layer include forms such as:
  - deadlines
  - capacity limits
  - precedence constraints
  - incompatible commitments
  - context switches
  - interruption costs
  - resource exhaustion
  - temporary lockouts

### 6.2 Surface Versus Structural Control Demand

- Are the important control demands absent from the most obvious surface description?
- Is the task weaker because the best plan is too easy to read off immediately?
- Does the graph reward discovering the right control policy rather than parroting the most visible instruction?

## 7. Path And Behavior Scoring Readiness

### 7.1 Path Quality

- Can the scenario distinguish coherent control from wandering?
- Can it detect whether the model sequenced subgoals intelligently?
- Can it identify whether the model prioritized the right branches at the right time?

### 7.2 Decision Efficiency

- Is there a notion of near-optimal or at least efficient control?
- Can the scenario distinguish efficient execution from brute-force exploration?
- Does the graph structure make wasted actions, unnecessary switches, or poor ordering visible?

### 7.3 Justification Quality

- Can the model's explanation be checked against the states and constraints it actually encountered?
- Does the justification require reference to goal structure, tradeoffs, or plan revision?
- Can unsupported post-hoc rationalizations be penalized?

### 7.4 Behavioral Signatures

- Does the scenario produce interpretable signatures such as:
  - goal neglect
  - shallow planning
  - impulsive execution
  - premature stopping
  - perseveration
  - delayed switching
  - over-switching
  - weak conflict arbitration
  - working-memory collapse
  - efficient recovery after failure
- Would two models with the same final answer be distinguishable by trace quality?

### 7.5 Stopping Behavior

- Is it possible to tell whether the model stopped too early, too late, or appropriately?
- Does the scenario contain enough signal to assess rational stopping?
- Can the benchmark reward stopping after sufficient control work rather than endless exploration?

## 8. Evidence Grounding

### 8.1 Evidence Coverage

- Are there critical states, branches, constraints, or conflict points that should appear in successful trajectories?
- Can the scenario verify whether these were actually encountered and handled?
- Is the minimum control-relevant evidence set identifiable?

### 8.2 Anti-Storytelling Controls

- Can the model be penalized for citing states, constraints, or conflicts it never encountered?
- Can the explanation be grounded in the traversal log rather than post-hoc storytelling?
- Is there a clean mapping from visited evidence to final plan explanation or decision rationale?

## 9. Transfer And Generalization

### 9.1 Transfer Support

- Can the same executive demand be tested under:
  - a new graph layout
  - renamed entities
  - different surface instructions
  - changed local topology
  - new distractor patterns
  - reordered options
- Would success survive these changes if the model actually had the targeted executive-control skill?

### 9.2 Generalization Testing

- Can the scenario family distinguish control-skill generalization from template memorization?
- Does surface variation break shallow pattern matching?
- Is transfer distance intentional rather than arbitrary?

## 10. Multi-Domain Design Controls

### 10.1 Controlled Multi-Domain Use

- If the scenario is multi-domain, do the domains share a common executive-control mechanic?
- Does domain diversity improve robustness rather than create unrelated variety?
- Is the scenario family coherent rather than a grab-bag of puzzles?

### 10.2 Stable Executive Demand, Variable Surface

- Is the control structure stable across domain variants?
- Do surface changes preserve the same underlying planning, inhibition, switching, or conflict challenge?
- Would shortcutting on one domain fail on another domain skin?

## 11. Difficulty Design

### 11.1 Good Difficulty Dimensions

- Does difficulty vary along useful dimensions such as:
  - planning horizon
  - subgoal dependency depth
  - lure strength
  - switching cost
  - interruption frequency
  - conflict subtlety
  - working-memory manipulation load
  - resource scarcity
  - replanning frequency
  - hierarchical control demand

### 11.2 Bad Difficulty Dimensions

- Is difficulty being increased mainly by:
  - adding more text
  - adding arbitrary clutter
  - increasing naming confusion
  - hiding key evidence unfairly
  - making humans fail for non-cognitive reasons
- If yes, redesign the difficulty curve.

## 12. Shortcut Resistance

### 12.1 Surface Shortcut Checks

- Is the best policy not obvious from the prompt wording alone?
- Is the answer not leaked in the entry node or first hop?
- Is there no trivial local heuristic that solves most instances?
- Is the scenario not reducible to template matching on visible labels?

### 12.2 Structural Shortcut Checks

- Is the topology-to-answer relationship perturbable?
- Are graph ordering, naming, and layout safely changeable?
- Are near-miss variants possible?
- Can multiple equivalent renderings preserve the same executive challenge?
- Is the model prevented from memorizing repeated graph-template-to-policy mappings?

## 13. Minimum Acceptance Checklist

A scenario should usually be accepted only if the answer is `yes` to most of the following:

- Does it test executive control rather than static knowledge?
- Does it contain a genuine multi-step goal?
- Does the order of actions matter?
- Is there at least one clear executive sub-ability being measured?
- Are control failures behaviorally visible?
- Can final correctness be separated from behavioral quality?
- Is the graph stateful and interactive?
- Are meaningful constraints present?
- Is there a real need for planning, inhibition, switching, conflict handling, or working-memory manipulation?
- Is it human-solvable?
- Can it support transfer or perturbation variants?
- Does it resist shortcutting?
- Does it produce diagnostic behavioral signatures?

## 14. Strong Preferred Properties

These are not mandatory for every scenario, but they make scenarios materially stronger:

- explicit subgoal hierarchy
- meaningful budget pressure
- strong but suppressible lures
- interpretable switch points
- visible perseveration opportunities
- clear conflict tradeoffs
- bounded but real working-memory manipulation
- replanning after surprise
- evidence-grounded justification
- transfer-ready variants
- distinct failure signatures for different executive weaknesses

## 15. Scenario-Type-Specific Notes

These should be used when a scenario intentionally targets a particular family of executive tasks.

### 15.1 Planning-Heavy Worlds

- Does the model need to build and execute a multi-step action sequence?
- Are dependencies and action order central?
- Would greedy local choice fail?

### 15.2 Inhibition-Heavy Worlds

- Are there salient but low-value actions that should be suppressed?
- Would impulsive action visibly damage performance?
- Is premature commitment penalized?

### 15.3 Rule-Shift Or Task-Switch Worlds

- Does the model need to abandon a previously successful policy?
- Are switch points behaviorally visible?
- Can perseveration be measured cleanly?

### 15.4 Conflict-Arbitration Worlds

- Are there genuine competing goals or incompatible constraints?
- Must the model justify which tradeoff it selected?
- Is there a coherent rubric for evaluating the resolution?

### 15.5 Working-Memory Control Worlds

- Does the model need to track and update intermediate state actively?
- Are external aids bounded enough that working-memory demand remains meaningful?
- Is the burden about manipulation, not just storage?

### 15.6 Mixed Executive-Control Worlds

- Does the scenario intentionally combine goal maintenance, planning, inhibition, switching, conflict resolution, and working memory?
- If so, is the intended primary source of difficulty still interpretable?
- Can the scoring separate different control failures rather than collapse into one generic score?

## 16. Rejection Criteria

Reject a scenario if one or more of the following is true:

- It is basically a static QA task.
- Final correctness matters far more than control quality.
- There is no genuine multi-step goal.
- There is no real need to plan ahead.
- There is no tempting but wrong action to inhibit.
- There is no switching, replanning, or conflict pressure.
- Working memory is reduced to recalling one visible fact.
- The task is dominated by attention, memory, learning, or generic reasoning rather than executive control.
- A greedy local policy solves it reliably.
- Unlimited tools trivialize the intended executive demand.
- Humans would fail for arbitrary reasons rather than because control demands are hard.
- Different models with very different control quality would look identical under the scoring.

## 17. Compressed Scenario Gate

If we need a fast scenario screen, use this shorter gate:

- goal-directed
- multi-step
- control-heavy
- stateful environment
- meaningful constraints
- at least one clear executive sub-ability
- visible control failures
- process-scoreable
- human solvability
- transfer potential
- shortcut resistance
- interpretable executive behavior

If a candidate scenario fails multiple items in this short gate, it should not move forward.
