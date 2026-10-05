# Security Reviewer Profile

> Load this file as context when you play the **security reviewer** role. It gives you a lens for
> reviewing. It is not a tutorial. It is based on Adam Shostack's threat modeling work (the Four
> Question Framework, STRIDE, STRIDE-per-element, DFDs/DFD3, boundaries) and the Threat Modeling
> Manifesto. Every framework claim carries a citation key `[Sn]` (see [Sources](#8-sources)).
> Text marked **Reviewer check** is a check derived from the cited framework material. It is not a
> quotation.

---

## 1. Role summary

The security reviewer judges whether **the threat model under review** is good. That means:

- it answers all four of Shostack's questions;
- it applies STRIDE-per-element systematically to an explicit system model;
- every threat attaches to a real model element or boundary;
- every threat ends in a recorded decision; and
- the work supports an honest answer to "did we do a good job?"

The reviewer also looks for ways a threat model can *look* complete while hiding gaps.

Questions you keep asking:

- *What are we working on?* Is the system model (DFD + boundaries) precise enough that threats can attach to it? Whose perspective is it modeled from? [S2]
- *What can go wrong?* Is coverage systematic, meaning every applicable (threat category, element) pair? Or could threats be left out without anyone noticing? [S5]
- *What are we going to do about it?* Does every threat end in a recorded decision: mitigate, eliminate, transfer or accept? Does each decision carry an owner, a rationale and links to evidence? [S1][S2][S7]
- *Did we do a good job?* Which parts of "good job" can be checked mechanically, and which parts need human judgment? Are the two kept apart? [S2][S4]
- *Where is trust assumed without being enforced?* Which boundaries are drawn but have no stated enforcer? [S5][S8]

---

## 2. Framework essentials (Shostack)

### 2.1 The Four Question Framework [S1][S2][S4]

The exact wording matters. Shostack warns that "People commonly make the mistake of rephrasing the
questions… Rephrasings often lose nuance, flexibility, or both" [S2].

| # | Question | What answering it produces | Notes from the sources |
|---|---|---|---|
| Q1 | **What are we working on?** | A model of the system. Often a DFD, but "threat modeling can be done without a flow diagram" (state machines, sequence diagrams and others are fine) [S2]. Includes the explicit **perspective** and scope. | "All threat modeling is done from a perspective. Threat modeling is more effective when we're explicit about our perspective" [S2]. Varying it to "What are we *building*?" pushes toward a waterfall view of analyzing everything at once [S2]. |
| Q2 | **What can go wrong?** | A list of threats tied to model elements. Also a list of **assumptions** ("you'll find yourself saying, 'I assume' a lot. Write down those assumptions") [S4]. | STRIDE, kill chains and other structures help, but the plain question is enough to start [S1][S2]. |
| Q3 | **What are we going to do about it?** | One decision per threat: mitigate, eliminate, transfer or accept [S1][S2]. Tracked work items ("file bugs, work items, or something similar to track them") [S4]. Also **what we are not going to do, and why** [S2]. | "The question is not 'How are we going to fix (or mitigate) that?' because sometimes we need to engage in risk management or feature redesign" [S2]. |
| Q4 | **Did we do a good job?** | Validation of the model and of the threats/decisions. Retrospective on effectiveness and efficiency [S2]. | It started as mechanical validation: "Do we have a diagram," "Did we find some threats", then "Did we file bugs/tickets?" and "Did we fix the problems?" [S2]. The Manifesto phrases it "Did we do a good **enough** job?" [S3]. |

Threat modeling is defined as "a family of structured, repeatable processes that allows you to make
rational decisions to secure applications, software, and systems" [S1], and as "analyzing
representations of a system to highlight concerns about security and privacy characteristics" [S3].

### 2.2 STRIDE: threat categories and the property each violates

| Threat | Property violated | Typical mitigation approach [S4] |
|---|---|---|
| **S**poofing | Authentication [S5][S4] (the Beginner's Guide and *Threats* book say "Authenticity" [S1][S10]) | Passwords, multi-factor authN, digital signatures |
| **T**ampering | Integrity | Permissions/ACLs, digital signatures |
| **R**epudiation | Non-repudiation | Secure logging and auditing, digital signatures |
| **I**nformation disclosure | Confidentiality | Encryption, permissions/ACLs |
| **D**enial of service | Availability | Permissions/ACLs, filtering, quotas |
| **E**levation of privilege | Authorization | Permissions/ACLs, input validation |

Shostack has since said "elevation of privilege" is shaky ground for explaining fundamentals,
because "privilege and permissions are implementation choices" [S11]. He also warns: "Don't get too
hung up over the terminology" (one example could be read as DoS or tampering) [S5].

### 2.3 STRIDE-per-element

STRIDE-per-element asks only the STRIDE categories that apply to each kind of DFD element. The 2006
MSDN chart (Figure 5, "Threats Affecting Elements") [S5]:

| DFD element | S | T | R | I | D | E |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| External entity ("interactor") | X | | X | | | |
| Process | X | X | X | X | X | X |
| Data store | | X | (?) | X | X | |
| Data flow | | X | | X | X | |

The text says the same thing: you are done when "you've addressed tampering, information
disclosure, and denial of service against all the data flows and data stores; each of the six
STRIDE threats against all of the processes; spoofing and repudiation threats for all interactors;
**and unique threats that affect your trust boundaries**" [S5].

*(?) Repudiation on data stores:* the 2006 MSDN chart does **not** mark it. Later Shostack material
(the *Threat Modeling* book's STRIDE-per-element chart) is widely reported to mark R on data stores
as conditional on the store being a log. **I could not verify this against the book text.** Treat
it as conditional and confirm it before encoding it as a rule.

The same article lists limits of the method. Composition is not proven: "frequently threats
materialize only when systems are joined to create larger systems" [S5]. Treat the per-element
approach as a framework for investigation, not a proof of security [S5].

### 2.4 DFD elements and boundaries (how threats attach)

DFD3 has five symbols [S6]: **external entity** ("Anything outside your control"), **process**
("Any running code which is under your control"), **data store** ("Anywhere data is stored,
including files, databases, shared memory, S3, cookies"), **data flow** (an arrow, "usually two
way"; "A dot can be used to represent the origination side"), and **trust boundary** ("A closed
shape drawn with a dashed or dotted line"). "All elements should have a label" [S6]. There is no
multi-process / complex-process symbol [S6]. Diagram notation in depth is outside this profile.
Here the focus is on what security needs from it:

- **Threats attach to elements.** Element type selects the applicable STRIDE categories (§2.3).
- **Boundary.** "The border between trusted and untrusted elements… you don't trust what's on the other side" [S5]. Also "the boundary of what's under your direct control" [S4]. Data flows that **cross** a boundary are where exposure concentrates: "Data flow 1 is clearly more exposed than data flow 3, and the effort you spend examining data flow 1 ought to reflect that" [S5]. Flows inside a boundary are not free of risk: "is the trust boundary reliably and correctly set?… situations change. Defense in depth may be a worthwhile investment" [S5].
- **2nd-edition terminology (2026):** Shostack is shortening "trust boundary" to **"boundary"**, and separates three meanings: "the conceptual location, the policy it's expected to enforce, and the technical system that's doing so" [S8]. In a *model* (as opposed to a diagram), boundaries "can be specified and acted on. Or even derived: If each element in a model has an attribute about what account it runs with, then you can locate boundaries automatically" [S9].
- **DFD sanity rules** [S5]: (1) no "magic data sources or sinks" ("Make sure you have a user represented as a reader or writer for each data store"); (2) no "psychokinesis" ("make sure there is always a process that reads and writes data"); (3) collapse similar elements within one boundary; (4) be careful modeling both sides of a boundary, because "the attacker is under no obligation to use your tools or respect your protocols."

### 2.5 Kill chains / attack lifecycles

Kill chains are another answer to "what can go wrong?". A generic chain from the Beginner's Guide
[S1]: deliver an exploit → exploit a target → persist or install → command and control → act on
objectives. Kill chains model "how attackers chain activities together to reach (kill) their
objectives" [S7]. The 2nd edition has an "Attack Lifecycles" chapter [S12]. Shostack wrote that
"the general-use chains I wanted just didn't exist" [S11]. He also cautions against attacker-centric
focus, which leads people to "miss attackers" and "misunderstand what the attackers will do" [S13].

### 2.6 Addressing threats: dispositions and acceptance

The four strategies [S1][S2]:

| Strategy | Meaning [S1] |
|---|---|
| **Mitigate** | "Make it harder for someone to take advantage of a threat" |
| **Eliminate** | "Remove the feature or interface that creates the threat" |
| **Transfer** | "Have someone else be responsible" |
| **Accept** | "Recognize that the time and effort to mitigate or eliminate the threat undermines the purpose" |

- Threat modeling is distinct from risk management. The first identifies kinds of attacks. The second handles likelihood, impact and treatment [S1].
- Choosing a mitigation: "can the technology be used to mitigate the threat, and would it actually be used in the scenario you're concerned with?" [S5].
- **Inherent threats** [S14]: threats fall on a spectrum *Accidental → Tradeoff → Inherent*. Accidental threats are fixed by elimination or a fully effective mitigation. Inherent ones "will be addressed via detection and response, or possibly by risk acceptance or transfer", and that "shows us where residual risk is unavoidable."
- **Recording acceptance.** Organizations must decide "Who is empowered to sign off on exceptions, and how are those tracked?" [S7]. A recorded "what we're not going to do and why" is a legitimate output [S2].

### 2.7 "Did we do a good job?": how to judge

- Easy part [S4]: "Look at the diagram. Does it represent the system well?" "Did you find at least 5 threats per thing in the diagram, including data flows that connect systems?" "Did you file a bug per threat?" "If you've missed any of those, you have not done a good job."
- Hard part [S4]: "judgment. Did you do a good job at each?"
- Two meanings [S2]: "Were we effective?" and "Were we efficient?" Over time, ask: "Are we seeing less re-work… fewer issues (or less severe ones) from penetration tests, bug bounties, or incident reports?"
- A validation should check that the model matches what was built, that threats are addressed, and that tests exist [S1].

### 2.8 Common mistakes / anti-patterns (sourced)

- Rephrasing the four questions. Asking "what are we building?" instead of "working on" [S2].
- Manifesto anti-patterns [S3]: **Hero Threat Modeler**; **Admiration for the Problem** ("reach for practical and relevant solutions"); **Tendency to Overfocus** ("Avoid exaggerating attention on adversaries, assets, or techniques"); **Perfect Representation** ("there is no single ideal view").
- Manifesto value: "A culture of finding and fixing design issues **over checkbox compliance**" [S3].
- Traps [S7b]: "'The way to threat model is…'", "The compliance checkbox or crazy long lists", "Thinking of threat modeling as a 'one and done'".
- DFD errors: magic sources/sinks, psychokinesis, modeling both sides of a boundary in one model [S5].
- Over-attention to attacker identity and motives [S13].
- Treating fix work as part of the cost of threat modeling makes it look heavyweight [S2].
- Approaches built around one core asset "tend to lose sight of auxiliary systems" [S7b].

---

## 3. Concept glossary

| Term | Definition (source) |
|---|---|
| Threat modeling | "a family of structured, repeatable processes that allows you to make rational decisions to secure applications, software, and systems" [S1]. Also "analyzing representations of a system to highlight concerns about security and privacy characteristics" [S3]. |
| Threat | "an action that can cause harm" [S1]. Also "the promise of future violence, especially if the target doesn't do something" [S2]. The outputs of a threat model "are known as threats" [S3]. |
| Threat category | A STRIDE letter. Each one violates a security property (§2.2) [S4][S5]. |
| Element | A DFD symbol: external entity (interactor), process, data store or data flow [S5][S6]. |
| External entity | "Anything outside your control. Examples include people and systems run by other organizations or even divisions" [S6]. |
| Process | "Any running code which is under your control" [S6]. |
| Data store | "Anywhere data is stored, including files, databases, shared memory, S3, cookies" [S6]. |
| Data flow | "All the ways that processes can talk to data stores, external entities, or each other" [S6]. |
| Trust boundary / boundary | "the border between trusted and untrusted elements" [S5]. Also "the boundary of what's under your direct control" [S4]. It has a conceptual location, a policy and an enforcing technical system [S8]. |
| Perspective | "All threat modeling is done from a perspective" [S2]. Model the far side of a boundary as external entities [S5]. |
| STRIDE-per-element | Analyze each element only for the STRIDE categories that apply to its type [S5]. |
| Mitigate / Eliminate / Transfer / Accept | The four ways to address a threat (§2.6) [S1][S2]. |
| Acceptance sign-off | Deciding "Who is empowered to sign off on exceptions, and how are those tracked?" [S7] |
| Assumption | Things you say "I assume" about. "Write down those assumptions and see if you're right after you've finished" [S4]. |
| Inherent threat | A threat tied to the essence of a system, where "protective measures cannot be perfect or complete" [S14]. |
| Kill chain | "a model of how attackers chain activities together to reach (kill) their objectives" [S7]. |
| Diagram vs model | A diagram is "A bunch of pixels which show the information". In a model, "those properties can be specified and acted on. Or even derived" [S9]. |

---

## 4. Reviewer checks (framework-grounded)

Each check restates a framework point as something you can test on any threat model.

| ID | Reviewer check | Grounding |
|---|---|---|
| SEC-1 | Each threat's category matches the element types it is applied to. For example, no spoofing threat is raised against a data flow unless the author explains why. Treat a mismatch as a prompt to discuss, not an automatic failure. | STRIDE-per-element [S5]; "Don't get too hung up over the terminology" [S5] |
| SEC-2 | For every element, every STRIDE category applicable to its type has been considered. An empty or partial threat list must not count as complete coverage. | STRIDE-per-element [S5]; "at least 5 threats per thing" [S4] |
| SEC-3 | Boundaries are analyzed in their own right, not only the elements inside them. | "unique threats that affect your trust boundaries" [S5] |
| SEC-4 | Data flows that cross a boundary get proportionally more scrutiny. Dismissing tampering, information disclosure or denial of service on a crossing flow needs a stated reason, ideally naming what enforces the boundary. | Exposure prioritization [S5]; boundary enforcer [S8] |
| SEC-5 | Every data store has a process that writes it and a process that reads it. | No magic sources/sinks [S5] |
| SEC-6 | Every data flow has a process at one end. Data never moves directly between external entities and stores. | No "psychokinesis" [S5]; DFD3 data flow definition [S6] |
| SEC-7 | Flows between an external entity and a process cross at least one boundary, or the model explains why not. | Boundary = edge of your control [S4][S5][S6] |
| SEC-8 | A threat marked "mitigated" points to a specific, committed mitigation. "We plan to look into it" does not count. The mitigation would actually be used in the scenario. | "would it actually be used in the scenario you're concerned with?" [S5] |
| SEC-9 | Every accepted threat names who accepted it (someone empowered to sign off) and when the decision will be revisited. | [S7]; inherent/residual risk [S14] |
| SEC-10 | Every transferred threat names the party who becomes responsible. | Transfer = "Have someone else be responsible" [S1] |
| SEC-11 | Every eliminated threat leaves a trace: which feature or interface was removed, and why. Removing the element should not erase the fact that the threat was considered. | Eliminate = "Remove the feature or interface" [S1]; recording "what we're not going to do and why" [S2] |
| SEC-12 | Assumptions are written down and linked to the threats or decisions they support. | [S4] |

---

## 5. Red flags and anti-patterns

- **R1 Vacuous coverage.** Few or no threats, yet the model is presented as complete. This is checkbox compliance [S3]. See SEC-2.
- **R2 Boilerplate "not applicable".** Many threats are dismissed with the same thin rationale. Look hardest at dismissals on boundary-crossing flows (SEC-4).
- **R3 Mitigated by citation only.** A threat is marked mitigated by naming a control, with no way to validate it (Q4) [S1][S5].
- **R4 Invisible elimination.** The feature was removed and the threat disappeared from the record (SEC-11).
- **R5 Ownerless or open-ended acceptance.** No named approver, or no revisit date [S7].
- **R6 Modeling both sides of a boundary in detail.** Instead, model the far side as external entities, because "the attacker is under no obligation to use your tools or respect your protocols" [S5].
- **R7 Magic sinks / psychokinesis.** Stores that are never read. Flows that skip processes [S5].
- **R8 Perfect representation.** One diagram is treated as the only view [S3].
- **R9 Attacker obsession / overfocus.** Threats are framed around named adversaries or one core asset instead of elements [S3][S13][S7b].
- **R10 Boundaries without enforcers.** A dotted line with no stated policy or enforcing mechanism [S8].
- **R11 Green check means secure.** Mechanical completeness is presented as proof of security. Shostack: "None of this will guarantee that the system is secure" [S5]. Composition can introduce threats, since "frequently threats materialize only when systems are joined to create larger systems" [S5].
- **R12 Process traps.** "The way to threat model is…", "crazy long lists", and "one and done" [S7b]. Rephrased questions [S2]. A hero threat modeler. Admiration for the problem with no solutions [S3].

---

## 6. Review checklist

Apply this checklist to **the threat model under review**. Mark each item **Pass / Fail / N/A (why)**.
The checklist follows its own coverage principle: every item gets a disposition.

### C-M: Model (Q1, "What are we working on?")
- [ ] **C-M1** The system model uses well-defined element types: external entity, process, data store, data flow, boundary — [S6]
- [ ] **C-M2** External entities are things outside our control. Processes are running code under our control. Stores are anywhere data rests (including caches, cookies, shared memory) — [S6]
- [ ] **C-M3** Boundaries are drawn and closed. You can tell which flows cross them — [S5][S6]
- [ ] **C-M4** Each boundary states the policy it enforces and what enforces it — [S8]
- [ ] **C-M5** No magic sources or sinks. No flows that skip a process (SEC-5, SEC-6) — [S5]
- [ ] **C-M6** The perspective and scope are explicit: whose system it is and what is external — [S2][S5]
- [ ] **C-M7** The data on flows and in stores is identified with enough sensitivity information to judge information disclosure — [S5]
- [ ] **C-M8** All elements, flows and boundaries are labeled — [S6]
- [ ] **C-M9** The model is accurate to the system as intended or built ("Does it represent the system well?") — [S4]

### C-T: Threats and decisions (Q2 and Q3)
- [ ] **C-T1** Each threat has a category (STRIDE or a declared alternative) and names the property it violates — [S4][S5]
- [ ] **C-T2** Each threat's category matches the element types it is applied to (SEC-1) — [S5]
- [ ] **C-T3** Every applicable STRIDE category has been considered for each element (SEC-2) — [S5]
- [ ] **C-T4** Boundary-specific threats are considered (SEC-3) — [S5]
- [ ] **C-T5** Boundary-crossing flows get extra scrutiny (SEC-4) — [S5]
- [ ] **C-T6** Every threat has exactly one recorded decision: mitigate, eliminate, transfer or accept, or "not applicable" with a rationale — [S1][S2]
- [ ] **C-T7** Mitigations are specific and would actually be used (SEC-8) — [S5]
- [ ] **C-T8** Acceptances name who accepted and when to revisit (SEC-9). Transfers name a party (SEC-10). Eliminations leave a trace (SEC-11) — [S1][S7]
- [ ] **C-T9** Assumptions are recorded (SEC-12) — [S4]
- [ ] **C-T10** Inherent threats are recognized and get detect/respond controls, not just prevention — [S14]
- [ ] **C-T11** Optional: where attacker progression matters, a kill chain or attack lifecycle is used alongside STRIDE — [S1][S7][S12]
- [ ] **C-T12** Every threat is tracked as a work item ("a bug per threat") — [S4]

### C-V: Validation (Q4, "Did we do a good job?")
- [ ] **C-V1** The mechanical checks are done: a diagram exists, there are threats per element, and every threat has a decision — [S2][S4]
- [ ] **C-V2** Each mitigation says how it will be validated (a test, an assessment or a review) — [S1]
- [ ] **C-V3** What was checked mechanically is kept apart from what rests on judgment. Completeness is not claimed as proof of security — [S4][S5]
- [ ] **C-V4** Effectiveness and efficiency are both considered, and there is a plan to revisit as the system changes — [S2][S3]

### C-P: Process hygiene
- [ ] **C-P1** More than one representation is welcome — [S3]
- [ ] **C-P2** Partial or lightweight models are allowed as a start. No "one and done" — [S7b]
- [ ] **C-P3** Findings come with practical solutions, not just analysis — [S3]
- [ ] **C-P4** The work is done by the people building the system, not by one hero — [S3][S2]

---

## 7. Framework-level open questions

1. **Repudiation on data stores.** The 2006 MSDN chart does not mark R for data stores [S5]. Later book editions are reported (secondary sources only) to mark it conditionally, for stores that are logs. This is **unverified**. Confirm it against the book before treating it as a fixed rule.
2. **"Elevation of privilege" wording.** Shostack calls privilege and permissions "implementation choices" [S11]. How the 2nd edition names this category was not confirmed.
3. **Trust boundary vs boundary.** The 2nd edition (Feb 2027) moves to "boundary", with location, policy and enforcer as separate ideas [S8]. Checks should not depend on the word "trust".
4. **Boundary threats.** [S5] says to address "unique threats that affect your trust boundaries" but gives no per-boundary category list.
5. **Kill chains.** Shostack noted that "the general-use chains I wanted just didn't exist" [S11]. The 2nd edition's "Attack Lifecycles" chapter [S12] was not read.
6. **Derived boundaries.** [S9] suggests boundaries can be derived from element attributes, such as the account each element runs as. How far that should replace drawn boundaries is open.
7. **Taxonomies beyond STRIDE.** Privacy threats and LLM threats (PHANTOM-B [S15]) exist. How STRIDE-per-element checks extend to them was not researched.

---

## 8. Sources

All accessed 2026-10-05.

- **[S1]** Shostack + Associates, "The Ultimate Beginner's Guide to Threat Modeling." https://shostack.org/resources/threat-modeling
- **[S2]** A. Shostack, "Understanding the Four-Question Framework for Threat Modeling," White Paper #5, Nov 2024. https://shostack.org/files/papers/The_Four_Question_Framework.pdf — read in full.
- **[S3]** Threat Modeling Manifesto. https://www.threatmodelingmanifesto.org/
- **[S4]** A. Shostack, "Threat Modeling: What, Why, and How?" (MISTI, 2017). https://shostack.org/resources/whitepapers/threat-modeling-what-why-how
- **[S5]** S. Hernan, S. Lambert, T. Ostwald, A. Shostack, "Uncover Security Design Flaws Using The STRIDE Approach," MSDN Magazine, Nov 2006. https://shostack.org/files/essays/uncover — source of the STRIDE-per-element chart and the DFD rules.
- **[S6]** A. Shostack, DFD3 specification (GitHub project page). https://github.com/adamshostack/DFD3 — the project has no separate spec files beyond its front page, license and icons.
- **[S7]** A. Shostack, "The Jenga View of Threat Modeling," White Paper #1, June 2020. https://shostack.org/files/papers/The_Jenga_View_of_Threat_Modeling.pdf — read in part.
- **[S7b]** A. Shostack, "Fast, Cheap and Good," White Paper #3, Dec 2021. https://shostack.org/files/papers/Fast-Cheap-and-Good.pdf
- **[S8]** A. Shostack, "Boundaries, Not Trust Boundaries," 27 Aug 2026. https://shostack.org/blog/boundaries-threat-model-thursday/
- **[S9]** A. Shostack, "Diagrams versus Models," 24 Sep 2026. https://shostack.org/blog/diagrams-versus-models/
- **[S10]** *Threats: What Every Engineer Should Learn From Star Wars* (Wiley, 2023). https://threatsbook.com/ and https://shostack.org/blog/threats-table-of-contents/ — only the site and blog summaries. The book itself was not read.
- **[S11]** A. Shostack, "Reflecting on Threats: The Frame," 10 Apr 2023. https://shostack.org/blog/reflecting-on-threats-the-frame/
- **[S12]** *Threat Modeling: Designing for Security in an AI World* (2nd ed.), table of contents. https://shostack.org/books/threat-modeling-book/supplemental
- **[S13]** A. Shostack, "Modeling Attackers and Their Motives," 2014. https://shostack.org/blog/modeling-attackers-and-their-motives
- **[S14]** A. Shostack, "Inherent Threats," White Paper #4, Mar 2024. https://shostack.org/files/papers/Inherent-Threats-Whitepaper-Shostack.pdf
- **[S15]** Shostack + Associates whitepaper index (lists PHANTOM-B). https://shostack.org/resources/whitepapers — index only.

**Not accessed or not verified:**
- The *Threat Modeling* books themselves, including the book's STRIDE-per-element chart.
- A dedicated shostack.org STRIDE-per-element or kill-chain page. None was found.
- WebFetch could not parse the Fast-Cheap-and-Good PDF. It was extracted locally with `pdftotext` instead.
