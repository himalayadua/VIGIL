# Track 4 Scenario Validation Checklist

This document is the working validation checklist for deciding whether a proposed Vigil scenario genuinely measures `Track 4: Metacognition` in the DeepMind AGI framework, rather than plain reasoning, planning, memory recall, post-hoc explanation, or social inference.

It is meant to be used before scenario generation, during scenario review, and before benchmark acceptance.

## Purpose

This checklist is designed to answer one core question:

`Does this scenario force the model to assess, monitor, and regulate its own cognition in a behaviorally visible way?`

If the answer is no, then it is not a strong Track 4 scenario.

## How To Use This Checklist

- Treat `Core Requirements` as mandatory unless there is a very strong reason not to.
- Treat `Strong Preferred Properties` as features that materially improve scenario quality and benchmark validity.
- Treat `Scenario-Type-Specific Checks` as required only when the scenario claims to measure that specific metacognitive sub-ability.
- Use `Rejection Criteria` as hard blockers.
- A scenario does not need to satisfy every preferred property, but it should satisfy most of the core requirements and produce clearly interpretable metacognitive behavior.

## 1. Core Requirements

### 1.1 Self-Monitoring Requirement

- Does the scenario require the model to make at least one meaningful judgment about its own cognition?
- Does the scenario require the model to assess one or more of the following:
  - confidence
  - uncertainty
  - sufficiency of evidence
  - likelihood of error
  - source of belief
  - memory status
  - need for verification
  - need for clarification or help
  - whether to stop or continue
- Would a system that solved the object-level task but had no self-monitoring perform materially worse?
- Is the metacognitive demand necessary for success rather than decorative?

### 1.2 Object-Level Versus Meta-Level Separation

- Are task success and metacognitive success scored separately?
- Can the scenario distinguish between:
  - correct answer + good metacognition
  - correct answer + poor metacognition
  - wrong answer + useful metacognitive behavior
  - wrong answer + poor metacognitive behavior
- Can the model fail metacognition even if it gets the final answer correct?
- Can the model demonstrate strong metacognitive behavior even if it ultimately answers incorrectly?

### 1.3 Blind Framing

- Does the model receive a real task rather than an explicit “reflect on yourself” exam prompt?
- Is the model not told that `Metacognition` is the faculty being evaluated?
- Does the environment naturally create uncertainty, error risk, or decision tradeoffs?
- Does the task avoid explicitly instructing the model to “now introspect” unless that is a natural part of the environment?

### 1.4 Human Solvability

- Is the scenario human-solvable under the same interface constraints?
- Could a human baseline reasonably be collected for both task performance and meta-level behavior?
- Would humans meaningfully vary in:
  - calibration
  - help-seeking
  - stopping quality
  - error detection
  - source awareness
  - self-correction
- Does the difficulty come from uncertainty management rather than arbitrary confusion?

### 1.5 Consequence Of Self-Assessment

- Does being correctly self-aware materially help performance?
- Does the environment reward good metacognition through one or more of the following:
  - reduced error
  - better stopping
  - better verification allocation
  - better source tracking
  - better help-seeking
  - safer abstention or deferment
- Does bad metacognition incur visible cost?

## 2. Environment Requirements

### 2.1 Real And Reducible Uncertainty

- Does the scenario contain genuine uncertainty, ambiguity, or incomplete evidence?
- Is the uncertainty reducible through rational action rather than arbitrary guesswork?
- Is uncertainty central to the task rather than cosmetic?
- Can the scenario distinguish uncertainty that should be reduced from uncertainty that should be tolerated?

### 2.2 Action Space Supports Metacognition

- Does the interface allow behavior such as:
  - inspect
  - verify
  - gather more evidence
  - request clarification
  - ask for help
  - abstain
  - defer
  - revise hypothesis
  - update confidence
  - report source
  - stop
- Are these actions meaningfully constrained and interpretable?
- Can the model visibly regulate behavior based on its internal assessment?

### 2.3 Cost Structure Exists

- Is there a cost for premature commitment?
- Is there a cost for excessive checking?
- Is there a cost for unnecessary help-seeking?
- Is there a cost for failing to seek help when appropriate?
- Can the scenario distinguish between:
  - rational caution
  - generic hedging
  - reckless confidence
  - verification paralysis

### 2.4 Provenance And Source Traceability

- Can the environment track whether information came from:
  - direct observation
  - prior exploration
  - memory of earlier nodes
  - inference
  - instruction
  - demonstration
  - help from another source
- Can the model be tested on whether it knows where a belief came from?
- Can fabricated or confused source claims be detected?

### 2.5 Event Logging Supports Scoring

- Does the trace log:
  - confidence states
  - revisions
  - contradiction encounters
  - verification actions
  - help requests
  - stopping decisions
  - source claims
  - evidence inspected before commitment
- Is there enough event detail to reconstruct whether metacognitive control was rational?

## 3. Metacognition-Theory Alignment

### 3.1 DeepMind Metacognition Definition Alignment

- Does the scenario align with the idea that metacognition is knowledge of one’s own cognitive processes plus the ability to monitor and control them?
- Does the task measure meta-level cognition rather than object-level competence alone?
- Does the benchmark make self-monitoring and self-regulation behaviorally visible?

### 3.2 Three-Layer Structure Alignment

Every scenario should either isolate one layer cleanly or intentionally combine several in a controlled and explainable way.

- `Metacognitive Knowledge`
  - Does the scenario test self-knowledge about limitations, learning processes, memory status, or behavioral tendencies?
- `Metacognitive Monitoring`
  - Does the scenario test confidence calibration, judgments of learning, error monitoring, or source judgments in real time?
- `Metacognitive Control`
  - Does the scenario test how the model changes strategy, verifies, corrects, defers, or asks for help based on monitoring?

### 3.3 Evidence Of Real Metacognition

- Would a good score be evidence of genuine self-monitoring rather than polished reflection language?
- Is the metacognitive signal visible in behavior rather than only in explanation text?
- Can the scenario distinguish between:
  - real uncertainty awareness
  - generic caution
  - post-hoc rationalization
  - stylistic self-doubt without behavioral change

## 4. Metacognitive Sub-Ability Coverage

Every scenario should either isolate one sub-ability cleanly or intentionally combine several in a controlled and explainable way.

### 4.1 Knowledge Of Limitations

- Does the scenario require the model to recognize what it cannot yet justify?
- Can the benchmark detect overclaiming?
- Can honest uncertainty be rewarded without rewarding blanket hedging?
- Is there at least one moment where saying “I do not know yet” is more correct than pretending certainty?

### 4.2 Knowledge Of Learning Processes

- Does the scenario require the model to know what kind of information or experience would most improve performance?
- Can it identify what it should inspect next to reduce uncertainty?
- Can it distinguish between high-value and low-value verification actions?
- Does the model need to choose how to learn more effectively within the episode?

### 4.3 Metamemory

- Does the scenario test whether the model knows whether something is actually known, seen, or remembered?
- Can it distinguish:
  - remembered
  - inferred
  - guessed
  - unseen
  - forgotten
- Can the task detect false memory claims or mistaken familiarity?
- Is the task harder than merely storing one exposed fact in working memory?

### 4.4 Knowledge Of Behavioral Tendencies

- Does the scenario let the model reveal awareness of its own tendencies such as:
  - rushing
  - overchecking
  - repeating failed strategies
  - weak source grounding
  - premature stopping
- Can such self-knowledge improve future choices?

### 4.5 Confidence Calibration

- Is confidence captured in a way that can be checked against correctness?
- Can the scenario penalize:
  - overconfidence on wrong answers
  - underconfidence on correct answers
- Is confidence measured at meaningful moments such as:
  - before verification
  - after verification
  - before final submission
- Can the task resist performative “medium confidence everywhere” behavior?

### 4.6 Judgments Of Learning

- Is there a study, exploration, or exposure phase followed by a prediction about later performance?
- Can the scenario compare predicted mastery to actual later performance?
- Can it detect illusions of mastery or false confidence in having learned enough?

### 4.7 Error Monitoring

- Is there at least one plausible error or contradiction point?
- Can the model notice the mismatch between expectation and observed evidence?
- Can the benchmark distinguish between:
  - detected quickly
  - detected late
  - never detected
  - detected but ignored
- Is error detection behaviorally visible in the trace?

### 4.8 Source Judgments

- Does the model need to know where a belief came from?
- Can the benchmark distinguish between:
  - direct observation
  - memory
  - inference
  - instruction
  - help from others
  - guesswork
- Are source confusions possible and diagnostically meaningful?

### 4.9 Error Correction

- Once an error is detected, does the model actually revise answer or strategy?
- Is successful correction observable and scoreable?
- Can the scenario distinguish between:
  - noticing an error and correcting it
  - noticing an error but failing to act
  - cosmetic self-criticism with no real adjustment
  - lucky second answers without real error awareness

### 4.10 Learning Strategy Selection

- Does the model choose among alternative strategies for reducing uncertainty or improving future performance?
- Can it redirect effort toward weak or uncertain parts rather than already-mastered parts?
- Does it stop redundant checking and focus on the most diagnostic next step?

## 5. Disconfirmation, Revision, And Control

### 5.1 Disconfirmation Pressure

- Is there at least one meaningful point where an initial belief becomes questionable?
- Does the scenario pressure the model to revise an internal judgment about correctness, confidence, source, or strategy?
- Is the disconfirming evidence behaviorally reachable through good metacognitive behavior?

### 5.2 Revision Quality

- Can the trace show whether the model:
  - committed early
  - noticed mismatch
  - revised confidence appropriately
  - revised source attribution appropriately
  - changed strategy appropriately
- Is revision quality observable and scoreable?

### 5.3 Dead Ends And Recovery

- Are there diagnostically meaningful overchecking traps, false-certainty traps, or irrelevant verification loops?
- Would a good solver recognize and recover from them?
- Can the benchmark measure whether the model:
  - doubled down blindly
  - recovered efficiently
  - sought the right kind of help
  - continued checking after enough evidence was available

## 6. Hidden Mechanism Design

### 6.1 Hidden Meta-State Quality

- Is there an important hidden uncertainty state, source ambiguity, or error risk that the model must manage?
- Is the task structured so that the model must move from object-level task pursuit to meta-level self-regulation?
- Could the hidden meta-demand take forms such as:
  - uncertain evidence sufficiency
  - memory/source ambiguity
  - conflict between confidence and evidence quality
  - verification tradeoff
  - stopping tradeoff
  - clarification-or-commit dilemma

### 6.2 Surface Versus Meta-Depth

- Are the important metacognitive demands absent from the most obvious surface reading of the task?
- Is the scenario weaker because all uncertainty is already explicitly announced?
- Does the task reward moving from surface completion to deeper self-monitoring?

## 7. Path And Behavior Scoring Readiness

### 7.1 Meta-Behavior Quality

- Can the scenario distinguish coherent self-regulation from generic caution or noise?
- Can it detect whether the model checked the right thing at the right time?
- Can it identify whether uncertainty management was rational rather than habitual?

### 7.2 Verification Efficiency

- Is there a notion of near-optimal verification or evidence gathering?
- Can the scenario distinguish efficient checking from brute-force or redundant verification?
- Are wasted verification actions visible in the trace?

### 7.3 Justification Quality

- Can the model’s justification be checked against what it actually saw and did?
- Does the explanation require grounded reference to real evidence, confidence changes, or revision triggers?
- Can fabricated or unsupported meta-justifications be penalized?

### 7.4 Behavioral Signatures

- Does the scenario produce interpretable signatures such as:
  - overconfidence
  - underconfidence
  - calibration improvement after evidence
  - premature stopping
  - endless checking
  - failure to ask for help
  - unnecessary help-seeking
  - source confusion
  - contradiction blindness
  - cosmetic self-correction
  - real self-correction
- Would two models with the same final answer be distinguishable by trace quality?

### 7.5 Stopping Behavior

- Is it possible to tell whether the model stopped too early, too late, or appropriately?
- Does the scenario contain enough signal to assess rational stopping?
- Can the benchmark reward stopping after sufficient confidence and evidence rather than endless uncertainty theater?

## 8. Evidence Grounding

### 8.1 Evidence Coverage

- Are there critical evidence nodes, contradiction points, or verification opportunities that should appear in successful trajectories?
- Can the scenario verify whether these were actually visited?
- Is the minimum evidence set identifiable for responsible commitment?

### 8.2 Anti-Storytelling Controls

- Can the model be penalized for claiming verification it never performed?
- Can the model be penalized for citing sources it never visited?
- Can the justification be grounded in the traversal log rather than post-hoc storytelling?
- Is there a clean mapping from visited evidence to final meta-level explanation?

## 9. Calibration, Help-Seeking, And Stopping

### 9.1 Calibration Support

- Can the scenario support repeated confidence judgments so calibration can be measured meaningfully?
- Can selective accuracy under abstention or deferment be measured?
- Can the benchmark distinguish real calibration from generic uncertainty language?

### 9.2 Help-Seeking Support

- Is there an option to ask for help, clarification, or escalation?
- Is help-seeking sometimes rational and sometimes wasteful?
- Can the scenario score:
  - appropriate help-seeking
  - avoidable help-seeking
  - failure to seek help when needed
- Does help change what the model can reasonably know?

### 9.3 Stopping And Deferral Support

- Is there a rational stopping point?
- Is there a meaningful option to defer or abstain?
- Can the task distinguish:
  - premature stopping
  - rational stopping
  - endless checking
  - panic abstention

## 10. Transfer And Generalization

### 10.1 Transfer Support

- Can the same latent metacognitive challenge be tested under:
  - a new graph layout
  - renamed entities
  - different domain skin
  - changed evidence order
  - new surface content with same uncertainty structure
- Would success survive these changes if the model actually had the targeted metacognitive skill?

### 10.2 Generalization Testing

- Can the scenario family distinguish real meta-skill from one-task gaming?
- Does surface variation break shallow prompt patterning?
- Is transfer distance intentional rather than arbitrary?

## 11. Multi-Domain Design Controls

### 11.1 Controlled Multi-Domain Use

- If the scenario is multi-domain, do the domains share a common metacognitive mechanism?
- Does domain diversity improve transfer validity rather than create unrelated variety?
- Is the scenario family coherent rather than a grab-bag of puzzles?

### 11.2 Stable Mechanic, Variable Surface

- Is the hidden metacognitive structure stable across domain variants?
- Do surface changes preserve the same underlying monitoring or control challenge?
- Would shortcutting on one domain fail on another domain skin?

## 12. Difficulty Design

### 12.1 Good Difficulty Dimensions

- Does difficulty vary along useful dimensions such as:
  - evidence ambiguity
  - contradiction subtlety
  - source confusion risk
  - confidence trap strength
  - number of plausible wrong paths
  - verification cost
  - stopping ambiguity
  - help-seeking tradeoff complexity
  - revision depth

### 12.2 Bad Difficulty Dimensions

- Is difficulty being increased mainly by:
  - adding more text
  - adding arbitrary clutter
  - increasing jargon
  - making humans fail for non-metacognitive reasons
  - hiding key evidence unfairly
  - making the task simply harder at the object level
- If yes, redesign the difficulty curve.

## 13. Shortcut Resistance

### 13.1 Surface Shortcut Checks

- Is the correct confidence or source state not trivially leaked by the prompt surface?
- Is the answer not effectively inferable without any self-monitoring?
- Is there no trivial policy such as “always verify” or “always abstain” that dominates?
- Is the scenario resistant to generic hedging strategies?

### 13.2 Structural Shortcut Checks

- Are the underlying uncertainty structure and scoring robust to reordering, renaming, or superficial changes?
- Are near-miss variants possible?
- Can multiple equivalent renderings preserve the same metacognitive challenge?
- Is the model prevented from memorizing a repeated scenario-template-to-confidence policy?

## 14. Minimum Acceptance Checklist

A scenario should usually be accepted only if the answer is `yes` to most of the following:

- Does it force self-monitoring rather than just task solving?
- Are object-level and meta-level performance separable?
- Is uncertainty real and reducible?
- Does the environment support verify / revise / ask-help / stop style behavior?
- Is there a cost structure for premature commitment versus excessive checking?
- Can confidence be scored against correctness?
- Is there at least one meaningful revision opportunity?
- Is there a rational stopping point?
- Can source judgments be tested?
- Can fabricated source claims be penalized?
- Can the scenario distinguish overconfidence, underconfidence, and good calibration?
- Is it human-solvable?
- Does it avoid collapsing into another track?
- Does it produce diagnostic metacognitive signatures?

## 15. Strong Preferred Properties

These are not mandatory for every scenario, but they make scenarios materially stronger:

- explicit help-seeking option
- explicit abstain or defer option
- prospective confidence before answer
- post-verification confidence update
- source-tagged beliefs
- contradiction point
- overconfidence trap
- underconfidence or overchecking penalty
- verification actions with nonzero cost
- multiple opportunities for strategy shift
- trace-grounded justifications
- repeated instances enabling calibration estimation
- transfer-ready variants
- multi-domain reskinning with stable meta-demand
- rational stopping opportunities

## 16. Scenario-Type-Specific Notes

These should be used when a scenario intentionally targets a particular family of metacognitive tasks.

### 16.1 Calibration-Centered Tasks

- Is confidence measured prospectively rather than only after outcome is known?
- Can calibration be estimated across repeated instances?
- Is there enough repetition to separate one-off luck from reliable calibration?

### 16.2 Error Monitoring And Correction Tasks

- Is there a plausible initial error or misleading path?
- Can contradiction or failure be observed before final submission?
- Does the benchmark distinguish noticing from correcting?

### 16.3 Source Monitoring Tasks

- Are beliefs traceable to observation, inference, memory, or instruction?
- Can source confusion be induced without making the task unfair?
- Does source tracking matter for safe or correct task completion?

### 16.4 Help-Seeking Or Escalation Tasks

- Is help available but costly or limited?
- Are there cases where help should be sought and cases where it should not?
- Is the model judged on appropriateness rather than frequency of help-seeking?

### 16.5 Stopping And Verification Tasks

- Can the model decide when it has enough evidence?
- Is overchecking penalized?
- Is premature stopping penalized?
- Is there a measurable optimum or near-optimum stopping region?

### 16.6 Judgments-Of-Learning Tasks

- Is there an exploration or study phase followed by future performance prediction?
- Can predicted mastery be compared to later actual performance?
- Can the benchmark detect overestimation or underestimation of learning progress?

## 17. Rejection Criteria

Reject a scenario if one or more of the following is true:

- It can be solved perfectly without any self-monitoring.
- Confidence reporting is present but has no consequence.
- Help-seeking is impossible, always optimal, or always suboptimal.
- Source attribution cannot be checked.
- There is no meaningful revision opportunity.
- There is no uncertainty tradeoff.
- The task mainly measures reasoning, planning, or memory rather than metacognitive regulation.
- The task rewards generic hedging.
- Honest uncertainty is punished indiscriminately.
- Overconfidence cannot be distinguished from correct confidence.
- Self-correction cannot be distinguished from lucky second answers.
- Human comparison would be meaningless or impossible.
- The trace does not let you verify what the model knew when it made a meta-judgment.

## 18. Compressed Scenario Gate

If we need a fast scenario screen, use this shorter gate:

- self-monitoring required
- meta-judgment affects behavior
- object and meta scores separable
- real uncertainty
- reducible uncertainty
- calibration measurable
- revision opportunity
- help / abstain / verify tradeoff
- source awareness testable
- rational stopping testable
- human solvability
- shortcut resistance
- interpretable metacognitive behavior
- not secretly another track

If a candidate scenario fails multiple items in this short gate, it should not move forward.
