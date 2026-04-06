# Track 3 Scenario Validation Checklist

## Executive Functions

## 0. Purpose

Use this checklist to answer one core question:

**Does this scenario genuinely measure executive control over thought and action in a goal-directed task, rather than recall, generic reasoning, attention alone, or long-context memory?**

If the answer is no, it is not a strong Executive Functions scenario. DeepMind’s evaluation framework also requires tasks to be **targeted**, **held-out**, **varied in difficulty**, **varied in structure**, and comparable to **human baselines under the same conditions and tool access**. 

---

## 1. Core requirements

### 1.1 Goal-directed control

* Does the scenario require the agent to pursue an explicit or discoverable goal over multiple steps?
* Does success depend on keeping that goal active while acting?
* Would the task still be meaningful if the final answer text were hidden and only the **trajectory of actions** were visible?
* Does the scenario measure **control of behavior** in service of a goal, not just correctness of a final response?

### 1.2 Sequential dependence

* Does the order of actions matter?
* Do earlier decisions shape later options, costs, or feasibility?
* Does the task require the agent to organize actions over time instead of answering in one shot?
* Is there a real difference between a coherent control policy and opportunistic local moves?

### 1.3 Control pressure

* Does the scenario create at least one real need for:

  * maintaining a goal,
  * planning ahead,
  * inhibiting a tempting action,
  * switching strategy,
  * resolving conflict,
  * or holding and manipulating intermediate state?
* If none of these are genuinely required, the task is probably not Executive Functions.

### 1.4 Not just “hard reasoning”

* Is the difficulty coming from **control demands**, not only from abstract reasoning complexity?
* Could a model with strong static reasoning but weak control still fail here?
* Does the scenario expose the difference between:

  * knowing what should be done,
  * and actually controlling behavior well enough to do it?

### 1.5 Human-solvability

* Is the scenario human-solvable under the same interface and tool rules?
* Would humans show meaningful differences in planning quality, inhibition, switching, or working-memory integrity on this task?
* Is the task hard because it stresses control, not because it is confusing, obscure, or unfair?

---

## 2. What this track is **not**

A strong Executive Functions scenario should **not** primarily be:

* a static reasoning puzzle with no sequential control demands
* a memory test that just checks recall of prior facts
* an attention test dominated by salience filtering alone
* a learning test dominated by discovering a hidden rule over repeated evidence
* a social test dominated by theory-of-mind inference
* a long-context retrieval task where success mostly comes from finding a buried detail

DeepMind’s own definition matters here: executive functions are about **regulating and orchestrating** thoughts and actions for goal-directed behavior, while working memory in this context is specifically **manipulating information internally in service of a goal**, not mere storage. 

---

## 3. Environment requirements

Unlike Track 1, **partial observability is helpful but not mandatory** for every Executive Functions scenario. Some strong executive-function tasks can be fully visible, as long as they stress planning, inhibition, switching, conflict handling, or working-memory manipulation.

### 3.1 Stateful task environment

* Is the environment stateful rather than one-shot?
* Can the agent’s actions alter progress, available options, or future costs?
* Does the task unfold over time rather than collapse into a single inference?

### 3.2 Multi-step structure

* Are there multiple required steps or subgoals?
* Does the task reward action sequencing rather than isolated correct choices?
* Is there a meaningful planning horizon?

### 3.3 Budget or constraint pressure

* Is there some limit that makes control meaningful:

  * step budget,
  * time budget,
  * resource budget,
  * interruption cost,
  * switching cost,
  * move penalty,
  * or conflict among constraints?
* Without some pressure, brute-force or diffuse behavior may work too easily.

### 3.4 Tempting but wrong options

* Are there high-salience, habitual, default, or locally attractive actions that should be suppressed?
* Can the scenario expose impulsive or perseverative behavior?
* Is there at least one moment where the best move is **not** the most obvious move?

### 3.5 Replanning opportunities

* Can plans fail or become suboptimal?
* Is there at least one point where the agent may need to re-evaluate and adjust?
* Can the environment reveal whether the system notices failure and changes course?

### 3.6 Conflict structure

* Does the scenario create competing goals, competing responses, or competing constraints?
* Is there a genuine need to arbitrate between them?
* Can the task show which priority the agent chose and why?

### 3.7 Tool access controls

* If external tools are allowed, are they controlled and matched to the human baseline?
* Would unrestricted scratchpads, planners, internet search, or note-taking trivialize the executive demand being measured?
* If the task claims to test working memory or planning, are external aids bounded enough that the cognitive target remains interpretable?

DeepMind explicitly warns that tool access can muddy what is being measured and says human baselines should get the **same tools** the AI system is allowed to use. 

---

## 4. Executive-function theory alignment

### 4.1 Track definition alignment

* Does the scenario match DeepMind’s definition of executive functions as higher-order abilities enabling goal-directed behavior?
* Does it measure orchestration of thought/action rather than domain knowledge?

### 4.2 Unity-and-diversity alignment

* Is the scenario either:

  * cleanly targeting one executive sub-ability,
  * or combining several in a deliberate, explainable way?
* If it combines multiple sub-abilities, is it clear which one is primary and which are secondary?

### 4.3 Process over outcome

* Would a strong score be evidence of **good control policy**, not only final correctness?
* Can the task distinguish:

  * lucky success,
  * brute-force success,
  * brittle rule-following,
  * and genuinely well-regulated behavior?

Diamond’s synthesis and the unity/diversity literature are useful guardrails here: executive functions are related, but not interchangeable, so benchmark design should avoid vague “general difficulty” and instead create interpretable control demands. 

---

## 5. Sub-ability-specific checks

## 5.1 Goal setting and maintenance

DeepMind defines this as the ability to **set and maintain goals to organize and direct action**. 

* Is there a clear target state, objective, or active goal representation?
* Must the agent keep that goal active across multiple steps?
* Are there opportunities for **goal neglect** or drift?
* Can the scenario reveal whether the agent:

  * forgets the goal,
  * confuses subgoals with the main goal,
  * or abandons the goal after distraction?
* Does success depend on maintaining goal coherence, not just rediscovering the goal each step?

## 5.2 Planning

DeepMind defines planning as formulating future action sequences to reach goals, and notes that planning is central to multi-step and long-term problems. 

* Does the scenario require thinking ahead, not just greedy local choice?
* Are there action sequences where short-term convenience harms long-term success?
* Is there a meaningful difference between:

  * no plan,
  * shallow plan,
  * and robust multi-step plan?
* Can the task expose:

  * failure to anticipate consequences,
  * poor subgoal order,
  * weak pruning of bad branches,
  * or inability to replan?

## 5.3 Inhibitory control

DeepMind defines inhibitory control as suppressing habitual or learned responses in favor of controlled, goal-appropriate ones. Diamond’s review treats inhibition as a core EF, with common paradigms including Stroop-, go/no-go-, and stop-signal-like demands. 

* Is there a dominant but wrong response tendency?
* Does the scenario require suppressing an intuitive, habitual, or salient move?
* Are inhibition failures behaviorally visible?
* Can the benchmark detect:

  * impulsive action,
  * premature submission,
  * repeated attraction to low-value options,
  * or failure to suppress outdated rules?

## 5.4 Cognitive flexibility

DeepMind defines this as switching between tasks, concepts, or ways of thinking. Diamond’s review notes that flexibility is often studied with task-switching and set-shifting paradigms such as Wisconsin Card Sorting–style rule shifts. 

* Does the scenario require switching strategy, rule set, representation, or subtask?
* Is there a real need to stop using a formerly good policy?
* Does success depend on noticing when a current strategy has become wrong or inefficient?
* Can the scenario reveal:

  * perseveration,
  * brittle commitment,
  * slow switching,
  * or over-switching without justification?

## 5.5 Conflict resolution

DeepMind defines this as managing conflicting information, contradictory goals, or competing responses to choose an appropriate action. 

* Does the task present genuinely competing cues, goals, or action recommendations?
* Must the agent choose under conflict rather than merely follow one clear signal?
* Is there a principled way to judge whether the conflict was resolved well?
* Can the task reveal whether the system:

  * collapses under contradiction,
  * chooses arbitrarily,
  * or resolves tradeoffs coherently?

## 5.6 Working memory

DeepMind defines working memory here as manipulating information internally in service of a goal, and Baddeley’s framework treats the central executive as coordinating that active use of limited information. 

* Must the agent hold and transform intermediate state while acting?
* Is the task harder than simply rereading visible information?
* Does it require:

  * maintaining a small number of active constraints,
  * updating them,
  * combining them,
  * or mentally simulating future states?
* Is the load high enough to matter but not so high that the task becomes an unfair memory stress test?

---

## 6. Behavioral evidence the scenario should surface

A good Executive Functions benchmark should let you score the **episode**, not just the final answer.

### 6.1 Goal persistence

* Did the agent stay aligned with the main objective?
* Did it drift into irrelevant side behavior?
* Did it mistake a local subgoal for the overall goal?

### 6.2 Plan quality

* Did the agent act with anticipatory structure?
* Did it sequence subgoals well?
* Did it avoid obviously dominated branches?
* Did it prune rather than wander?

### 6.3 Replanning quality

* When conditions changed or a plan failed, did the agent update well?
* Did it recover quickly?
* Did it keep forcing the original plan after contradiction?

### 6.4 Inhibition quality

* How often did it choose salient but wrong actions?
* Did it submit too early?
* Did it repeatedly take low-value default actions?

### 6.5 Flexibility / switch cost

* How efficiently did it switch when strategy changes were needed?
* Was switching too slow?
* Was it erratic and over-reactive?
* Did it generalize the new rule or keep mixing old and new policies?

### 6.6 Conflict handling

* When cues or goals conflicted, did the agent arbitrate coherently?
* Was the choice explainable in relation to priorities and constraints?
* Did it ignore one side of the conflict without justification?

### 6.7 Working-memory integrity

* Did the agent preserve and correctly update intermediate state?
* Did it lose track of constraints, dependencies, or already-established commitments?
* Did errors cluster when active state had to be manipulated, not just remembered?

### 6.8 Stopping quality

* Did the agent stop at the right time?
* Did it continue searching after an adequate plan was available?
* Did it stop before enough control work had been done?

### 6.9 Explanation-grounded control

* Can the model justify its plan, switch, inhibition choice, or conflict resolution using the actual states it encountered?
* Can unsupported post-hoc stories be penalized?

---

## 7. Difficulty design

DeepMind’s protocol also says tasks should be varied in difficulty and structure, so your executive-function family should scale difficulty in ways that stress control rather than mere verbosity or obscurity. 

### 7.1 Good difficulty dimensions

* longer but still manageable planning horizon
* more subgoal dependencies
* stronger lure/default options
* tighter resource budgets
* more costly switching
* more frequent or less obvious rule changes
* higher but bounded working-memory manipulation load
* more nuanced conflict tradeoffs
* interruptions or context changes that test goal maintenance
* need for hierarchical planning rather than flat action lists

### 7.2 Bad difficulty dimensions

* adding lots of irrelevant text
* adding arbitrary naming confusion
* hiding essential facts unfairly
* making humans fail for interface reasons
* turning the task into trivia or domain-jargon decoding
* increasing difficulty only by making the context longer

---

## 8. Shortcut resistance

### 8.1 Surface shortcut checks

* Can the agent succeed by spotting a superficial pattern rather than exerting control?
* Is the “best plan” obvious from the prompt wording alone?
* Is there an answer template that bypasses the need to maintain, inhibit, switch, or resolve conflict?

### 8.2 Structural shortcut checks

* Can a greedy local heuristic solve nearly all instances?
* Can memorizing a graph/task template replace real planning?
* Is the same control demand preserved under:

  * renamed entities,
  * reordered options,
  * changed layouts,
  * or reskinned domains?

### 8.3 Tool shortcut checks

* Could unlimited notes, calculators, solvers, or external planners wash out the executive demand?
* If yes, either restrict them or redefine the task to measure executive control with those tools explicitly included for both humans and models. 

---

## 9. Scenario-family notes

These are strong families for Executive Functions scenarios.

### 9.1 Planning-heavy tasks

Best when you want:

* explicit subgoals
* action ordering
* branch pruning
* lookahead
* plan revision after failure

### 9.2 Inhibition-heavy tasks

Best when you want:

* strong lures/default moves
* prepotent response suppression
* “don’t do the obvious thing” structure
* premature action penalties

### 9.3 Rule-switch / task-switch tasks

Best when you want:

* cognitive flexibility
* switching cost
* perseveration measurement
* old-rule suppression after change

### 9.4 Conflict-arbitration tasks

Best when you want:

* competing goals
* conflicting cues
* contradictory constraints
* explainable prioritization

### 9.5 Working-memory control tasks

Best when you want:

* active state tracking
* online updating
* mental simulation
* intermediate calculations or dependency management

### 9.6 Mixed-control tasks

Best when you want a more ecologically valid executive profile:

* maintain goal
* plan
* inhibit
* switch
* resolve conflict
* manipulate state

These mixed tasks are often more realistic, but harder to interpret unless scoring cleanly separates the main source of failure.

---

## 10. Rejection criteria

Reject a scenario if one or more of the following is true:

* It is basically static QA.
* Final correctness matters far more than control quality.
* There is no meaningful goal-maintenance burden.
* There is no real need to plan ahead.
* There is no tempting but wrong action to inhibit.
* There is no switching or replanning pressure.
* There is no real conflict to resolve.
* “Working memory” is just recalling a visible fact.
* The task is dominated by attention, reasoning, memory, or learning instead of executive control.
* A greedy local policy solves it reliably.
* Unlimited tools trivialize the intended demand.
* Human and AI conditions would not be comparable.
* Difficulty comes mainly from clutter, token length, or obscurity.
* Two agents with very different control quality would look identical under the scoring.

---

## 11. Minimum acceptance checklist

A scenario should usually move forward only if the answer is **yes** to most of these:

* Does it test executive control rather than static knowledge?
* Is there a genuine multi-step goal?
* Does the order of actions matter?
* Is at least one executive sub-ability clearly targeted?
* Are control failures behaviorally visible?
* Can process be scored, not just outcome?
* Is human comparison feasible?
* Are tool conditions controlled?
* Does the task resist greedy shortcutting?
* Does difficulty scale through control demands?
* Can the same mechanic survive perturbation or reskinning?
* Would weak planning/inhibition/flexibility/conflict handling actually cause failure?

---

## 12. Strong preferred properties

These are not mandatory in every case, but they make Track 3 scenarios much stronger:

* clear subgoal hierarchy
* budget pressure
* meaningful lures
* visible switch cost
* interpretable perseveration
* explicit conflict tradeoffs
* bounded but real working-memory load
* replanning after surprise
* trace-grounded justification
* perturbation-ready variants
* distinct failure signatures for different EF weaknesses

---

## 13. Compressed scenario gate

For quick screening:

* goal-directed
* multi-step
* control-heavy
* process-scoreable
* at least one clear executive sub-ability
* no easy greedy shortcut
* human-solvable
* tool-controlled
* difficulty from control, not clutter
* interpretable failure modes

If a candidate fails several of these, it should not move forward as a Track 3 scenario.
