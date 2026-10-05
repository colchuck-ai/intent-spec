# Product reviewer profile

Load this as context before reviewing a product model or specification as the **product reviewer**. It gives the reviewer a lens built on Jobs-to-be-Done (JTBD). It is not a tutorial.

The lens uses four primary terms: **job, job executor, outcome, requirement**. Terms from the main JTBD schools (Ulwick/ODI, Kalbach, Christensen/Moesta, Klement) are mapped onto these four. "The model under review" means whatever specification, schema, rule set or example documents you were asked to review.

**Schools disagree, so say which one you are applying.** JTBD has two interpretations that their own proponents call incompatible:

- *job-as-process* (Ulwick/ODI), which is outcome-driven.
- *job-as-progress* (Christensen, Moesta, Klement). Klement calls the first one "Jobs-As-Activities". [S16 pp. 187–188; S1]

This profile's statement grammars come from ODI. The progress school does not accept ODI-style job statements as jobs (§2.1). When a finding depends on the school, say which one you are applying.

---

## 1. Role summary

The product reviewer checks that the model under review can express product intent precisely, keeps solutions out of the places where they don't belong, and makes the reasoning traceable. The reviewer follows this chain:

```
job executor --performs--> job --has--> job step --yields--> outcome <--serves-- requirement <--satisfied by-- solution component
                                                               ^
                                         risk --endangers------+   measure/KPI --tracks--+
```

Questions the reviewer keeps asking:

1. **Who?** Is every job tied to the person who actually does it (the job executor)? Is that person kept separate from the buyer and from the people who support the product over its lifecycle?
2. **What?** Is each job stated without reference to a solution, so it stays stable while products change?
3. **How will they judge success?** Is each outcome a measurable, controllable, solution-free metric with a fixed grammar, attached to a job (ideally to a job step)?
4. **What will we build, and why?** Does every requirement trace to at least one outcome, or to some other stated justification? Is each requirement in turn satisfied by something in the solution?
5. **What did we decide not to serve?** Is coverage explicit? Unserved outcomes and unmapped job steps should carry a recorded disposition, not simply be missing.
6. **Is this a need, or evidence about a need?** Importance and satisfaction survey results are research evidence. A declared priority is a decision. Keep them distinct.
7. **What stops adoption?** Are constraints and the forces that block switching (anxiety, habit) captured anywhere? Or is the model purely functional?
8. **Can it be checked?** Can each JTBD statement rule be enforced by a schema or a runnable check, or is it only a prose guideline?

---

## 2. Concept glossary

Bracketed codes refer to §8 (Sources). Text in quotation marks is quoted from the source.

### 2.1 Primary terms

#### Job
- **ODI definition:** "the fundamental goal customers are trying to accomplish or problem they are trying to solve in a given situation" [S2 p. 9; S3 p. 64]. "When it comes to innovation, the job, not the product, must be the unit of analysis" [S2 p. 8]. Products are "merely point-in-time solutions that enable customers to execute jobs" [S2 p. 9; S3 p. 65].
- **Christensen school, early definition:** "A 'job' is the fundamental problem a customer needs to resolve in a given situation" [S11]. Christensen frames the job as the *causal* mechanism of purchase, where demographics are only correlated with it: "the causal mechanism behind a purchase is, 'Oh, I've got a job to be done'" [S12].
- **Christensen Institute definition:** a job is "the progress they're trying to make as they strive toward a goal or aspiration within particular circumstances". "All Jobs incorporate functional, social, and emotional forces". "We hire for different Jobs based on our changing circumstances" [S10].
- **Klement definition:** "A Job to be Done is the process a consumer goes through whenever she aims to transform her existing life-situation into a preferred one, but cannot because there are constraints that stop her" [S16 p. 32]. "People have Jobs; things don't" [S16 p. 43].
- **Core functional job (ODI):** "a single, solution-free statement" of the task [S4]. ODI examples include "cut a piece of wood in a straight line" [S4] and "listen to music while commuting to work" [S5].
- **School conflict:** Klement calls this "the biggest mistake": treating a job as "an activity or task". His examples of mistakes are "listen to music, cut a straight line, or make a quarter-inch hole" [S16 p. 35]. These are the very forms ODI uses. A reviewer applying the progress school will reject ODI job statements as activities.
- **ODI grammar:** `verb + object of the verb + contextual clarifier` [S3 p. 64; S5]. "a job statement must at a minimum contain a verb to introduce the statement and an object of the verb". A clarifier and examples are optional [S3 p. 67]. Example: "Determine the current value of an antique when at an auction" [S3 p. 64].
- **Kalbach grammar (secondary summary):** `verb + object + clarifier`. Write from the performer's perspective. Mention no technology. The job has an end state. Leave out adjectives such as "quick" or "easy", because they describe needs [S15].
- **Properties (ODI):**
  - "All jobs are processes."
  - "All jobs have a universal structure."
  - "Jobs are separate from solutions." [S7 p. 3]
  - The job "is the stable, long-term focal point around which value creation should be centered" [S3 p. 65].

#### Job executor
- **Definition:** "The primary user of the product, the person who employs it to accomplish the core functional job" [S4]. Also: "the person actually getting the Job done in the moment. Not the buyer, not the economic decision-maker, not the persona on the marketing deck. The person whose hands are on the product". And: "A Job Executor is a specific role in a specific moment: not 'contractors' but the tradesperson on a scaffolding … at the Confirm step of the Job" [S5].
- **Market definition (ODI):** "we define a market as a group of people and the 'job' they are trying to get done" [S6]. A market is therefore the pair (executor, job). Market size can be calculated "based on the number of potential job executors, the frequency with which they execute the job, and their willingness to pay to get the job done better" [S4].
- **The three customer types (ODI):** "the Job executor, the Purchase decision maker, and the product life cycle support team" [S4].
  - The purchase decision maker is "the individual or group responsible for making the financial purchase decision".
  - The lifecycle support team covers "those who install, transport, repair, maintain, upgrade, or dispose of the product. They perform what we call 'consumption chain jobs'" [S4].
- **Kalbach's term is *job performer*:** "It's also possible to create personas for roles other than the job performer. Chief among these is a buyer persona. You might also find that personas are needed for approvers, technicians, or people who are beneficiaries of job outcomes" [S14]. Kalbach does not see JTBD as replacing personas: "not all job performers are the same, and personas can be used to illustrate different types of performers" [S14].
- **Christensen school:** segment by job and circumstance, not by customer attributes. "The fact that you're 18 to 35 years old with a college degree does not cause you to buy a product" [S12]. "It is the situation rather than the customer that must be the fundamental unit of marketing analysis" [S11].

#### Outcome (desired outcome)
- **Definition:** "Desired outcomes are the metrics customers use to measure the successful execution of a job" [S2 p. 12, Fig. 3]. ODI defines a customer need as "a statement that tells the organization how customers measure value as they try to get a job done … We call customer needs, formulated in the manner described above, 'desired outcomes'" [S6]. "In ODI, needs are synonymous with desired outcomes" [S14].
- **ODI grammar:** `direction of improvement + unit of measure + object of control + contextual clarifier (+ example of object of control)` [S2 p. 11 Fig. 2; S3 p. 64].
  - "An outcome statement must at a minimum contain a direction of improvement, a unit of measure … and an object of control. Optionally … a contextual clarifier … and examples" [S3 p. 67].
  - Example: "Minimize the time it takes to identify the correct drill bit size for the material being drilled" [S5].
  - **Direction:** in 2008 the rule was "begin with either the word 'minimize' or 'increase'", with minimize used "about 90% of the time" [S3 pp. 67–68]. **Later refinement:** Kalbach (2020) notes that "within the ODI method, desired outcome statements now show only a downward or minimizing direction" [S14, note 1]. Strategyn's current pages give only "Minimize…" examples [S5, S6]. However, an older Strategyn paper still lists "minimize or increase" [S8 p. 10]. Kalbach himself allows "minimize, decrease, or lower" and "maximize, increase, and raise", while noting that "minimize has been found to be more precise language since people can imagine what zero looks like" [S14].
  - **Metric:** "In more than 95% of our desired outcome statements, our metrics are limited to time, likelihood, frequency, amount, risk or number" [S3 p. 68]. Kalbach's typical examples are "Time, effort, skill, and likelihood" [S14].
- **Required qualities:** "solution-free, … measurable". Each outcome should be able to "survive a survey" so it can "be converted into an Opportunity Score" [S5]. It must be "measurable, controllable" [S3]. Outcomes are "stable over time, since they represent measures of performance that are inherent to the execution of a specific job" [S8 p. 10].
- **Volume and placement:** a typical job has 8–12 steps, 6–12 needs per step, and roughly 50–150 needs in total [S2 p. 10; S6]. An older figure is 50–100 [S8]. Outcomes are captured per job-map step, covering speed, stability and output. "A company knows that it has uncovered all the customer's need statements when all attempts to capture outcomes related to speed, predictability and output have been exhausted for each process step" [S3 p. 68].
- **Constraint (related ODI input):** ODI treats as "a third customer input … the constraints that stand in the way of customers using a product or service to execute a job". These either prevent the job altogether or "prevent the use of a product under certain circumstances" [S8 pp. 7–8]. Klement builds constraints into the definition of a job itself [S16 p. 32].

#### Requirement
**Note on the term:** usage differs across schools and from common product practice.
- **In ODI,** a "requirement" or "customer requirement statement" *is the customer need*, either a job statement or a desired outcome statement. Rule 2 says "The requirement statement must not include or make mention of a technology, solution or product or service feature". Solutions are "the means by which unmet needs are satisfied" [S3 p. 65].
- **ODI's taxonomy of customer inputs:** ODI lists solutions, specifications, needs and benefits as common inputs, and argues that only desired outcomes should be captured from customers. "Recognizing that only desired outcomes need to be captured from customers – not needs, benefits, solutions or specifications – is the first step" [S8 p. 7]. In this taxonomy, what product practice calls a requirement is a *solution* or *specification*.
- **In common product and engineering practice,** a requirement is a *solution-side commitment*: what the product must do or be.
- **Reviewer reading:**
  - An *outcome* is the need. It belongs to the problem space and is solution-free, as ODI defines it.
  - A *requirement* is a commitment the product makes so that outcomes are better satisfied. It belongs to the solution space and must be verifiable.
  - ODI's no-solution rule applies to jobs and outcomes, not to solution-side requirements.
  - A requirement should say which outcomes it serves, and in which direction it is meant to move each outcome's metric.
  - The model under review must say which meaning of "requirement" it uses.
- **How requirements are derived (ODI):** quantify unmet outcomes, then run "sequenced and focused idea generation" against them, then evaluate concepts "against all the customer-defined metrics" [S2 pp. 13–16]. ODI asserts that it "begins by identifying all the customer's needs before any solution is considered. It then quantifies which of those needs are underserved, and only then moves to ideation" [S4]. Requirements come after prioritized outcomes, never before.

### 2.2 Supporting concepts

| Concept | Definition | Source |
|---|---|---|
| **Job map / job step** | "a visual depiction of a functional job, deconstructed into its discrete process steps". It shows what the customer is *trying to get done* (needs view), not what they are doing (solution view) | [S2 p. 10; S7] |
| **Universal job map** | 1 **Define**: determine goals and plan resources. 2 **Locate**: gather items and information needed to do the job. 3 **Prepare**: set up the environment. 4 **Confirm**: verify that they're ready. 5 **Execute**: carry out the job. 6 **Monitor**: assess whether the job is being successfully executed. 7 **Modify**: make alterations to improve execution. 8 **Conclude**: finish the job or prepare to repeat it. "nearly all jobs also require a problem resolution step" | [S7 pp. 1, 3; S2 p. 10 Fig. 1] |
| **Valid job step test** | "valid step: ascertain patient vital signs / invalid step: check the monitor"; "valid step: place an order / invalid step: call the supplier to place an order" | [S7 p. 4] |
| **Kalbach's map structure** | The map "breaks the main job into stages that are then broken down further into steps", where steps are "smaller objectives", not tasks. *Search-result summary only* | [S15] |
| **Related jobs** | "other supporting or related jobs customers may be interested in performing". "It is often the case that 10 to 20 other jobs may be of interest" | [S8 pp. 7–8; S5] |
| **Emotional jobs** | Personal (how the executor wants to feel) and social (how they want to be perceived) | [S2 p. 12 Fig. 3; S15] |
| **Consumption chain jobs** | Purchase, receive, install, set up, learn to use, interface with, transport, store, maintain, upgrade, replace, dispose. "each consumption chain job has its own distinct job map and set of need statements" | [S2 p. 12] |
| **Hierarchy of customer needs** | Core functional job → job map → outcomes; other functional jobs (related); emotional jobs (personal, social); consumption chain jobs | [S2 p. 12 Fig. 3] |
| **Job levels** | Aspiration → big job → little job → micro-job. Asking "Why?" moves up a level; asking "How?" moves down. *Secondary summary of Kalbach* | [S15] |
| **Circumstance** | Christensen: the situation is "a simpler, more stable point of focus" than the customer [S11]. Christensen Institute: "Circumstances are subject to change" [S10]. Kalbach segments performers by circumstance [S14]. ODI puts it in the contextual clarifier [S3] | |
| **Opportunity algorithm** | 2002 form: "Importance + (Importance - Satisfaction) = Opportunity", with "importance and satisfaction level 1 to 10" [S9]. Current form: `Opportunity = Importance + max(Importance – Satisfaction, 0)` [S2 p. 13]. Range 0–20 [S14]. Strategyn: "Both are measured on a ten-point scale" [S5]. Worked example: "9.5 + (9.5 - 3.2) = 15.8", which was "the highest opportunity value of all" [S9] | |
| **Opportunity thresholds** | Above 15 extreme, above 12 high, above 10 solid, 10 or below served or overserved. **Still unverified**: secondary sources only | [S18] |
| **Top-two-box scoring** | Importance is "the percentage of respondents who rated the outcome in the top two points", scaled to 0–10. **Secondary only** | [S18] |
| **Survey sample (Kalbach)** | "more than 150 … a good rule of thumb is to have at least twice the respondents as the desired outcome statements" | [S14] |
| **Underserved vs overserved** | Underserved outcomes point to core-market growth. Underserved *jobs* point to new or adjacent markets [S2 p. 13]. Overserved customers who are not willing to pay more are candidates for disruptive or low-cost strategies [S4] | |
| **Six growth strategies** | Features for the core job; features for related jobs; a new platform for the core job; a new platform for core plus related jobs; a new platform for a **new job executor**; and a new platform for a new executor with core plus related jobs | [S2 p. 15] |
| **Forces of progress** | *Promote change:* push of the situation ("whatever you're doing isn't working") and pull of the new solution. *Block change:* anxiety of the new solution and habit of the present ("the emotional energy attached to what they already do") | [S13; S1] |
| **Switch timeline** | The interview reconstructs the path "From your first thought to actually choosing it and using it" | [S13] |
| **Job story** | `[ When _____ ] [ I want to _____ ] [ So I can _____ ]`: situation, motivation, outcome. Created at Intercom; "Alan Klement later named it". This is a requirement-level framing, not an ODI outcome statement | [S17] |

### 2.3 Synonym map (primary term ← other schools)

| Primary term | Ulwick / ODI | Kalbach (Playbook) | Christensen / Moesta | Klement |
|---|---|---|---|---|
| **job executor** | job executor (purchase decision maker and lifecycle support team are *other* customer types) | job performer (plus buyer, approver, technician, beneficiary roles) | customer in a situation | consumer / "she" |
| **job** | core functional job; also related, emotional and consumption-chain jobs | main job (big job); related, emotional, social and consumption jobs | job = progress, or "fundamental problem … in a given situation" | Job to be Done = transformation process from the current to a preferred life-situation |
| *job step* | job map step (8 universal steps + problem resolution) | stages → steps | n/a | n/a (steps are "activities") |
| *circumstance* | contextual clarifier | circumstances | circumstance / situation | life-situation; "When" in job stories |
| *constraint* | constraint (third customer input) | n/a | anxiety, habit (forces that block change) | constraints (part of the job definition) |
| **outcome** | desired outcome = customer need = "requirement statement" | need / desired outcome statement | the progress made (no metric grammar) | "So I can" (loosely) |
| **requirement** (solution-side) | solution / specification (not a customer input) | solution | the product that is "hired" | the product / solution |

---

## 3. Expected model, in JTBD terms

These are the things the reviewer looks for. Each item should have a stable identifier, so traces survive rewording.

### 3.1 Entities and relationships

| Expectation | Cardinality and notes | JTBD basis |
|---|---|---|
| **Job executor** as a role, separate from concrete actors and personas | performs one or more jobs | [S4, S5, S14] |
| **Other customer roles** (purchase decision maker, lifecycle support) kept separate or explicitly excluded | Consumption-chain jobs belong to lifecycle support. Financial concerns belong to the buyer | [S4] |
| **Job** with statement fields `verb`, `object`, optional `clarifier`, optional `examples` (or one validated statement). The model declares which school it follows | exactly one executor per job, so a market is (executor, job) | [S3, S6, S16] |
| **Job kind**: `core-functional \| related \| emotional-personal \| emotional-social \| consumption-chain` | Consumption-chain jobs may carry a sub-kind | [S2 Fig. 3] |
| **Jobs independent of products** | Several solutions may serve the same job. The model must not force a duplicate job per product | [S7 p. 3] |
| **Job step** with `stage` (`define \| locate \| prepare \| confirm \| execute \| monitor \| modify \| conclude`, optionally `resolve-problem`) and an order | each step belongs to exactly one job | [S7] |
| **Outcome** with fields `direction`, `metric` (`time \| likelihood \| frequency \| amount \| risk \| number`, extensible), `objectOfControl`, optional `clarifier`, optional `examples`. `direction` is `minimize` (preferred, and possibly the only value in current ODI) or `increase` | exactly one job per outcome; optionally one step *of that job* | [S3, S14] |
| **Constraint** (optional) | belongs to a job; may name the circumstance in which it applies | [S8, S16] |
| **Requirement → outcome trace** | each requirement serves one or more outcomes, or states another explicit justification; optionally states its intended effect on the metric | [S2 p. 16] |
| **Outcome disposition** | each committed outcome is either served by at least one requirement, or carries `out-of-scope \| overserved \| deferred` plus a rationale | explicit coverage |
| **Job-map coverage** | each universal stage of a core job is mapped to at least one step, or marked not-applicable with a rationale | [S3 p. 68] |
| **Evidence separate from intent** | importance/satisfaction data and opportunity scores are linked as research evidence. A declared priority is labelled as a decision | [S2, S9] |
| **Outcome measurement** | if a separate KPI or measure exists, its relation to the outcome's own metric is defined | [S3] |

### 3.2 Checks the model should be able to run

Each check has an ID, a target, a condition, a pointer to the failing item, and a hint. Grammar heuristics are `should`. Structural checks are `must`.

| Check | Condition (informal) | JTBD basis |
|---|---|---|
| `requirement-traces` | each requirement serves at least one outcome, or names another explicit justification | [S2, S4] |
| `requirement-satisfied` | each committed requirement is satisfied by at least one solution component | need → solution |
| `executor-performs-job` | each executor performs at least one job | market = (executor, job) [S6] |
| `job-has-outcome` | each committed core-functional job has at least one outcome | [S2] |
| `outcome-served-or-dispositioned` | each committed outcome is served, or carries a disposition plus rationale | explicit coverage |
| `outcome-step-same-job` | an outcome's step belongs to the outcome's job | outcomes relate to the job of interest [S3 rule 10] |
| `outcome-grammar` | direction is in the allowed set; metric and object of control are present | [S3 p. 67] |
| `job-grammar` | verb and object are present | [S3 p. 67] |
| `statement-single-concept` (should) | no " and " / " or " joining two needs | "it instantly becomes two requirement statements" [S3 p. 66] |
| `job-solution-free` (should) | job and outcome text contains no term from the model's own solution vocabulary | Rule 2 [S3 p. 65] |
| `job-map-coverage` | each universal stage of a core job is mapped or marked not-applicable | [S3 p. 68, S7] |
| `lifecycle-consistency` | a committed requirement does not serve only retired or draft outcomes; a committed outcome does not belong to a retired job | stability of jobs [S3] |

---

## 4. Review checklist

Each item names the JTBD concept it protects. Mark each item **pass**, **fail** or **absent**. Report anything absent as a finding.

### A. Vocabulary
- [ ] A1 **(all terms)** Job, job executor, outcome and requirement are defined consistently with the model. The meaning of "requirement" is stated (§2.1).
- [ ] A2 **(job)** The model declares which JTBD school it follows: job-as-process (ODI) or job-as-progress [S16 pp. 187–188].
- [ ] A3 **(job)** Jobs are documented as independent of solutions and stable over time [S3, S7].
- [ ] A4 **(executor)** The executor is kept separate from the buyer and from lifecycle support [S4, S5], and from concrete actors and personas [S14].
- [ ] A5 **(outcome)** The outcome grammar is documented with at least one compliant example. The policy on allowed directions is explicit.

### B. Structure
- [ ] B1 **(job ↔ product)** Several products or solutions can serve the same job without duplicating it.
- [ ] B2 **(job kinds)** Related, emotional and consumption-chain jobs are expressible, or leaving them out is a recorded choice.
- [ ] B3 **(job map)** Job steps exist, and their stages match the universal job map.
- [ ] B4 **(outcome grammar)** Outcomes are structured or pattern-validated, with the minimum parts enforced.
- [ ] B5 **(job grammar)** A job is verb + object, with an optional clarifier.
- [ ] B6 **(outcome ↔ job)** An outcome belongs to exactly one job.
- [ ] B7 **(requirement ↔ outcome)** The trace exists and is enforced.
- [ ] B8 **(constraints)** Constraints or adoption blockers are expressible, or leaving them out is a recorded choice [S8, S13].
- [ ] B9 **(measurement)** There is no duplicate source of truth for how an outcome is measured.

### C. Checks
- [ ] C1 Each check in §3.2 is either implemented or explicitly declined.
- [ ] C2 Heuristic checks are advisory, and their hints quote the JTBD rule they rest on.
- [ ] C3 Coverage checks exist for outcomes and for job-map stages.
- [ ] C4 Lifecycle checks span the whole chain: job → outcome → requirement → solution.

### D. Examples
- [ ] D1 A valid example shows the full chain: executor → core job → steps → outcomes → requirements → solution components.
- [ ] D2 The jobs and outcomes in the examples pass the JTBD grammar. Authors copy whatever the examples do.
- [ ] D3 Each check has an invalid example that names the check it breaks. At minimum: a requirement with no trace; an outcome with no direction or metric; an outcome joined with "and"; a job that mentions a technology; a committed outcome with no requirement and no disposition; an executor with no job.
- [ ] D4 An example links research evidence (survey, interviews) by reference rather than inline.

### E. Evidence vs decision
- [ ] E1 Importance, satisfaction and opportunity data are not mixed into need statements. Declared priorities are labelled as decisions.
- [ ] E2 If opportunity scores appear, they are treated as derived from evidence. The rating scale and the formula variant (with or without `max`) are stated.

---

## 5. Red flags and anti-patterns

| Red flag | Why it is wrong | Source |
|---|---|---|
| A job or outcome names a technology, feature, product or component ("Use the mobile app to…") | Solutions contaminate needs and are not stable over time. "When solutions are included in a need statement … we see lower ratings" | [S3 pp. 64–65] |
| A job step is an action, not a goal ("check the monitor") | It is a process map, not a job map | [S7 p. 4] |
| A step depends on one executor's method ("call the supplier to place an order") | A step must apply to every executor | [S7 p. 4] |
| An outcome uses vague quality words ("reliable", "easy", "fast", "correctly") with no metric | Ambiguous and not actionable | [S3 pp. 63, 65] |
| One statement joins two needs with "and" or "or" | "it instantly becomes two requirement statements" | [S3 p. 66] |
| Mixed directions or inconsistent nouns across outcomes | They confound prioritization | [S3 p. 66 Rules 5–6; S3 p. 67] |
| The executor is a buyer, an org-chart role or a marketing persona | "Not the buyer, not the economic decision-maker, not the persona on the marketing deck" | [S5] |
| Segmentation by demographics instead of job and circumstance | Demographics correlate with purchase but do not cause it | [S12, S11] |
| Requirements with nothing behind them ("ideas-first") | "the 'ideas-first' approach is inherently flawed and cannot work" | [S2 p. 3] |
| Customer-supplied solutions or specifications accepted as needs | "only desired outcomes need to be captured from customers – not needs, benefits, solutions or specifications" | [S8 p. 7] |
| Outcomes of a related or consumption job filed under the core job | "Outcome statements must relate to the primary job of interest … and not to ancillary jobs" | [S3 p. 66 rule 10] |
| A job with no end state ("live a healthy life") | A main job needs a clear endpoint | [S15] |
| A job map confused with a journey map or service blueprint | A job map is solution-independent | [S7, S15] |
| Survey percentages stored as attributes of a need | Mixes evidence with the need | [S2, S9] |
| Job stories used as the outcome layer | They lack ODI's measurable direction and metric | [S17, S3] |
| Under the progress lens: jobs written as activities ("listen to music") | The progress school calls these tasks, not jobs | [S16 p. 35] |

---

## 6. Open questions about the framework

1. **Q1. Which school?** Job-as-process (ODI) and job-as-progress (Christensen, Moesta, Klement) disagree about what a job *is* [S16 pp. 187–188]. Can one model host both, for example with an ODI functional job plus a progress-style "struggling moment"? Or must it pick one?
2. **Q2. The meaning of "requirement".** ODI uses it for the need itself [S3]. Product practice uses it for a solution commitment. Which term avoids confusion?
3. **Q3. Allowed outcome directions.** The 2008 rules allow minimize or increase [S3]. Current ODI reportedly allows only minimize [S14 note 1]. Kalbach allows maximize too [S14]. Which should be enforced, and should "increase" statements be rewritten?
4. **Q4. Emotional and social jobs vs measurability.** The ODI outcome grammar suits functional jobs. The sources consulted give no equivalent strict grammar for emotional jobs.
5. **Q5. Structured fields vs a free statement.** Breaking the statement into fields makes it machine-checkable, but it may fight the optional parts (examples, clarifier).
6. **Q6. Circumstance and constraint as first-class.** The progress school and Kalbach treat circumstance as central [S10, S11, S14]. ODI and Klement both name constraints [S8, S16]. Should a model represent these separately?
7. **Q7. Opportunity thresholds and scale.** The cut-offs (above 10, 12 and 15) and top-two-box scoring are still secondary-only. Ulwick's 2002 article used raw 1–10 means without `max` [S9]. The thresholds depend on which scale is used.
8. **Q8. Step-level executors.** In B2B settings, different roles may perform different steps of one job. ODI defines a market as (executor, job). How should that be handled?
9. **Q9. Stability vs reframing.** ODI says jobs and outcomes stay stable for decades [S3, S8]. When a job is reframed at a different level of abstraction, how should retired outcomes point to their replacements?

---

## 7. Quick reference card

```
JOB        := <verb> <object> [<contextual clarifier>] [e.g., <ex1>, <ex2>]        (ODI)
              solution-free · executor's perspective · end state · one concept
              progress school: job = transformation of a life-situation, blocked by constraints
OUTCOME    := <minimize (preferred) | increase> <metric: time|likelihood|frequency|amount|risk|number>
              <object of control> [<contextual clarifier>] [e.g., <ex1>, <ex2>]
              solution-free · measurable · controllable · one concept · relates to the job of interest
JOB MAP    := define → locate → prepare → confirm → execute → monitor → modify → conclude (+ resolve problems)
ROLES      := job executor ≠ purchase decision maker ≠ lifecycle support team
FORCES     := push + pull  vs  anxiety + habit
OPPORTUNITY = importance + max(importance − satisfaction, 0)   on 0–10 scales → 0–20   [derived from evidence]
TRACE      := executor ─performs→ job ─has→ step ─yields→ outcome ←serves─ requirement ←satisfied by─ solution
```

---

## 8. Sources

**Primary** means the text was written by the originator or their firm and I read it directly. **Secondary** means a third-party summary. Page numbers are the printed page numbers.

| ID | Source | Status |
|---|---|---|
| S1 | Agile Brand Guide, "Jobs-to-be-Done (JTBD)", https://agilebrandguide.com/wiki/models/jobs-to-be-done-jtbd/#how-to-utilize-jtbd | **Verified verbatim** from a web.archive.org snapshot, because the live page is behind a Cloudflare block. It confirms the 7-step "How to Apply" process, the three dimensions, the four forces, the use cases, and the "two schools" framing. It is an encyclopedic secondary source; this profile relies on it only for the overview |
| S2 | Ulwick, A. W., *What is Outcome-Driven Innovation® (ODI)?*, Strategyn whitepaper, https://innovationroundtable.com/summit/wp-content/uploads/2014/05/Strategyn_what_is_Outcome_Driven_Innovation.pdf | Primary; full text read |
| S3 | Ulwick, A. W. & Bettencourt, L. A., "Giving Customers a Fair Hearing", *MIT Sloan Management Review* 49(3), Spring 2008, pp. 62–68, https://www.ki-insights.com/wp-content/uploads/2024/05/Ulwick.pdf | Primary (MIT SMR reprint 49314); full text read |
| S4 | Strategyn, "Jobs to Be Done (JTBD): The Original Framework", https://strategyn.com/jobs-to-be-done/ | Primary; page text extracted directly |
| S5 | Strategyn, "Jobs to Be Done template", https://strategyn.com/jobs-to-be-done-template/ | Primary; page text extracted directly |
| S6 | Strategyn (Ulwick), "Customer Needs Definition", https://strategyn.com/customer-needs-defined/ | Primary; **new**; page text extracted directly |
| S7 | Bettencourt, L. A. & Ulwick, A. W., "The Customer-Centered Innovation Map", *HBR* May 2008, Strategyn reprint, https://strategyn.com/wp-content/uploads/2019/10/The_Customer_Centered_Innovation_Map___HBR.pdf | Primary; full text read |
| S8 | Strategyn, *The Strategic Role of Customer Requirements in Innovation* (whitepaper), https://strategyn.com/wp-content/uploads/2019/10/The-Strategic-Role-of-Customer-Requirements-in-Innovation-Strategyn.pdf | Primary; **new**; full text read |
| S9 | Ulwick, A. W., "Turn Customer Input into Innovation", *HBR* Jan 2002, republished at https://www.cbsnews.com/news/turn-customer-input-into-innovation/ (© 2002 Harvard Business School Publishing) | Primary; **new**; publisher-licensed republication |
| S10 | Christensen Institute, "Jobs to Be Done", https://www.christenseninstitute.org/theory/jobs-to-be-done/ | Primary (Christensen's institute); fetched, but the tool returned a summary, so quotes may not be exact |
| S11 | Christensen, C. M., Anthony, S. D., Berstell, G. & Nitterhouse, D., "Finding the Right Job for Your Product", *MIT SMR* 2007, https://sloanreview.mit.edu/article/finding-the-right-job-for-your-product/ | Primary; **new**; open access; fetched, but the tool returned a summary |
| S12 | Nobel, C., "Clay Christensen's Milkshake Marketing", HBS Working Knowledge, 14 Feb 2011, https://hbswk.hbs.edu/item/clay-christensens-milkshake-marketing | Primary (Christensen quoted directly); **new**; page text extracted directly |
| S13 | Moesta, B., "Unpacking the Progress Making Forces Diagram", Jobs to be Done Radio, https://jobstobedone.org/radio/unpacking-the-progress-making-forces-diagram/ | Primary; **new**; fetched, but the tool returned a summary. The episode date was not shown |
| S14 | Kalbach, J., *The Jobs To Be Done Playbook* (2020), Chapter 4 excerpt on UXmatters, https://www.uxmatters.com/mt/archives/2020/05/book-excerpt-the-jobs-to-be-done-playbook.php | Primary (an authorized excerpt); full text extracted directly. This replaces the earlier summary-based citation |
| S15 | Clark, A., summary of Kalbach's *Playbook*, https://andrewclark.co.uk/product-book-summaries/the-jobs-to-be-done-playbook | **Secondary.** Still the only source for Kalbach's five elements, job levels, job-statement pitfalls, and job map vs journey map |
| S16 | Klement, A., *When Coffee and Kale Compete*, 2nd ed. (2018), free PDF linked from the author's site (https://www.whencoffeeandkalecompete.com/, read via web.archive.org because the live site returned 403): https://www.dropbox.com/s/je0ax86qitprdi9/WCAKC.pdf | Primary; **new**; full text read |
| S17 | Adams, P., "How we accidentally invented Job Stories", Intercom blog, 28 Jun 2016, https://www.intercom.com/blog/accidentally-invented-job-stories/ | Primary; **new**; page text extracted directly. Verifies the job-story format |
| S18 | Secondary summaries of the opportunity thresholds and top-two-box scoring: https://roadmap.one/blog/posts/blog8-8-opportunity-scoring/, https://businessbookclub.substack.com/p/jobs-to-be-done-by-anthony-w-ulwick, Wikipedia "Outcome-Driven Innovation" | **Secondary; still unverified** |

**Still inaccessible or not used:**
- **Ulwick, *Jobs to be Done: Theory to Practice* (2016)** (https://jobs-to-be-done-book.com/). The free PDF sits behind a personal-details form, which I did not submit. Third-party PDF hosts were not used.
- **Christensen et al., "Know Your Customers' Jobs to Be Done", *HBR* 2016:** paywalled.
- **Christensen et al., "Marketing Malpractice", *HBR* 2005:** not retrieved (paywalled). It is known only through S1.
- ***Competing Against Luck*:** no publisher excerpt was retrieved.
- **Klement's original job-story article** (jtbd.info): returned 403, and the archive snapshot did not resolve. S17 is used instead.
- **jobs-to-be-done.com (Ulwick's Medium posts):** returned 403, and the archive was rate-limited.
- **Kalbach's "The Core JTBD Process" (Medium):** returned 403.
- **jtbdtoolkit.com:** only a course page was available, with no definitions.
- **The Re-Wired Group's forces-of-progress page:** returned 404.
