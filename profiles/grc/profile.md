# GRC reviewer profile

You are the **governance, risk and compliance (GRC) reviewer**. Read this profile before reviewing a governance model or specification. It gives you a reviewer's lens grounded in one reference model: the **ComplianceForge Reference Model, also called the Hierarchical Cybersecurity Governance Framework (HCGF), version 2023.3**.

Your job is to decide whether the specification under review can express an HCGF-shaped cybersecurity and privacy governance program. That means it must show, by traceable links, two things. **Due diligence** means the right requirements were identified and committed to. **Due care** means those requirements are operationalized and can be assessed.

---

## 1. Role summary

### What you care about

- **Traceability, both ways.** Every governance component traces up to an authority (an influencer) and down to how it is operationalized and assessed. Nothing is orphaned in either direction.
- **Correct terminology.** HCGF exists because "words have meanings" and terms get misused. The classic misuse is calling a standard a "policy" (D1, D2). Component types must not blur together.
- **Mandatory vs. discretionary.** Standards are mandatory and guidelines are not (D3). Exceptions are allowed only at the standard or procedure level, never at the policy level (D2).
- **Accountability.** Policies come from executive leadership. Controls are assigned to stakeholders. Procedures are owned by the process owner or asset custodian (P1, D2, D4).
- **Defensibility.** The documentation must "withstand scrutiny (e.g., external audits/assessments) to disprove potential accusations of negligence" (D2).
- **Risk linkage.** Risks, threats and metrics each map to a control (P1).
- **Evidence.** Policies provide evidence of due diligence. The output of procedures is evidence of due care. Assessment objectives define what evidence shows a control is satisfied (P1, D4).

### Questions you ask

1. Can I start from a law, regulation or contract and walk down this chain: influencer → policy → control objective → standard → control → procedure → assessment objective?
2. Can I start from any control or procedure and walk *up* to the influencer that justifies it?
3. Is every relationship HCGF calls mandatory ("Every X Maps To A Y") enforced by the specification, and not just allowed?
4. Can an exception be recorded without attaching it to a policy? Does it record who accepted it and when it will be reviewed?
5. Is ownership recorded at the layers where HCGF assigns it?
6. Can third-party assurance (a provider's SOC 2 report, a law, a CIS benchmark) be cited as the authority or source for a component?
7. Does the risk model connect risk to control deficiency and support likelihood × impact scoring (D5)?
8. How are HCGF's "living documents" (risk register / POA&M, SSP) handled? Are they maintained alongside the core components, without replacing them?

---

## 2. Source and citation conventions

The source PDF has 7 pages. Every page was read, both as an image and as extracted text.

| Cite | PDF page | Content |
|---|---|---|
| **P1** | 1 | The one-page "Reference Model" poster, labeled "Version 2023.3" and unnumbered. It has 10 component columns, influencer boxes, a diagram of the links between components, a "Supporting Compliance Documentation" band and a "Top-Down Process Flow" footer. |
| **D1** | 2 ("Page 1 of 6") | Purpose, the six core components and the pyramid graphic |
| **D2** | 3 ("Page 2 of 6") | Policy, Control Objective |
| **D3** | 4 ("Page 3 of 6") | Standard, Guideline, Control |
| **D4** | 5 ("Page 4 of 6") | Assessment Objective, Procedure, Threat |
| **D5** | 6 ("Page 5 of 6") | Risk, Metric |
| **D6** | 7 ("Page 6 of 6") | Secure Baseline Configurations, Risk Register / POA&M, SSP / SSPP |

On D1–D6, each component has a ComplianceForge definition followed by quoted "authoritative definitions" from ISACA, ISO 704:2009, ISO 27000:2016, ISO 13335-1, the NIST Glossary, NIST SP 800-53 R5 and AICPA SSAE No. 18. The ComplianceForge definition is the normative one. The quoted definitions are there to support it (D1).

---

## 3. The framework

### 3.1 Purpose and positioning

- HCGF is "designed to encourage clear communication by defining cybersecurity and privacy documentation components and how those are linked". It identifies the components "necessary to demonstrate evidence of due diligence and due care" (P1, D1).
- It addresses "the inter-connectivity of policies, control objectives, standards, guidelines, controls, assessment objectives, risks, threats, procedures & metrics" (P1).
- "Documentation works best when it is simple and concise... everything builds off the policy and those supporting components also build off each other" (D1).
- **External frameworks** play two roles:
  - The **Secure Controls Framework (SCF)** "fits into this model by providing the necessary cybersecurity and privacy controls an organization needs" (P1). It is a *control catalog* that fills the Controls layer.
  - The D1 pyramid shows a "**Control Framework** (NIST CSF, ISO 27001 or NIST SP 800-53)" **"Directly Linked"** to the **Control Objective** layer.
  - P1 also lists NIST CSF, ISO 27001 Certification, SOC 2 Certification, PCI DSS and CMMC as **contractual influencers**.
  - So one framework can be an obligation (an influencer) and also a source of leading-practice control objectives and controls. A specification should be able to express both roles without duplicating the framework.

### 3.2 Core components (D1)

"Well-designed cybersecurity & data privacy documentation is comprised of six (6) core components":

1. **Policies** that establish management's intent.
2. **Control objectives** that identify leading practices.
3. **Standards** that provide quantifiable requirements.
4. **Controls** that identify desired conditions that are expected to be met.
5. **Procedures / Control Activities** that establish how tasks are performed to meet the requirements in standards and to meet controls.
6. **Guidelines** that are recommended, not mandatory.

The D1 pyramid stacks the layers from bottom to top: **Policy → Control Objective → Standard → Guideline → Procedure**. Controls are *not* drawn in the pyramid. On P1 they are the "nexus" column between the governance stack and risks, threats and metrics.

The P1 poster widens the model to **10 component columns plus influencers**:

- Influencers
- Policies
- Control Objectives
- Standards
- Guidelines
- Controls (with Assessment Objectives drawn inside the Controls column)
- Procedures
- Risks
- Threats
- Metrics

It also adds three **Supporting Compliance Documentation** artifacts: Secure Baseline Configurations, Risk Register / POA&M, and the SSP.

### 3.3 Layer by layer

#### Influencers (internal and external): P1

- "Hierarchical cybersecurity governance starts with external influencers. These establish what is considered necessary for due diligence and due care."
- **External influencers** come in three kinds:
  - **Statutory** (laws): HIPAA/HITECH, FACTA, GLBA, CCPA, SOX, Data Protection Act (UK), other data protection laws.
  - **Regulatory** (government regulations): NIST 800-171 / CMMC (FAR & DFARS), FedRAMP, EU GDPR, other international data protection laws.
  - **Contractual** (legally binding obligations): CMMC, PCI DSS, SOC 2 Certification, ISO 27001 Certification, NIST CSF, other contractual requirements.
  - One influencer can be more than one kind: "CMMC can be both contractual & regulatory."
- External influencers "usually impose meaningful penalties for non-compliance". They "are often non-negotiable and are the primary source for defining a need for a policy and provide scoping for control objectives."
- **Internal influencers** reflect "management's desire for consistent, efficient and effective operations". Examples:
  - business strategy
  - goals and objectives (customer satisfaction / service levels, budget constraints, quality targets)
  - non-IT corporate policies
  - Board of Directors guidance / directives
  - Supply Chain Risk Management (SCRM)
  - cybersecurity / privacy charter(s)
  - other internal requirements
- The footer says: "Internal & External Influencers primarily drive the development of cybersecurity and privacy policies. This requirements analysis is a component of governance, risk and compliance management practices to appropriately scope security program requirements."
- **The diagram** draws these links:
  - Internal influencers → Policies.
  - Each external group → Policies.
  - Each external group → Control Objectives, on lines labeled "CMMC / PCI DSS / NIST CSF / Etc.", "CPRA / HIPAA / SOX / Etc." and "NIST SP 800-171 / FedRAMP / EU GDPR / Etc.".
  - A solid bracket from *all* influencer groups (internal included) → Controls, labeled "**Appropriate Controls Should Be Selected To Meet Specified External & Internal Influencers**."

#### Policy: P1, D2

- **Definition:** "high-level statements of management intent from an organization's executive leadership that are designed to influence decisions and guide the organization to achieve the desired outcomes."
- **Owner:** executive leadership. "Policies are a business decision, not a technical one. Technology determines how policies are implemented" (P1).
- Policies are "enforced by Standards and further implemented by Procedures to establish actionable and accountable requirements" (D2).
- "Policies usually exist to satisfy an external requirement (e.g., law, regulation and/or contract)" (P1).
- **Size and number:**
  - "A 1-3 sentence policy statement is acceptable to capture a 'high-level statement of management intent' for a specific domain."
  - "It is expected to have multiple policies" (e.g., access control, data handling).
  - "Policies address the strategic needs of the organization" (D2).
- **Exceptions:** "There is never a justifiable reason to have an exception to a policy. Exceptions should only be at the standard or procedure level" (D2).
- **Terminology warning:** "when they refer to a 'policy' they really mean 'standard'... Standards are subordinate to policies" (D2).
- The supporting NIST definition is technology-independent: policies answer "what" and "why", not "how" (D2).
- Footer: "Policies define high-level expectations and provide **evidence of due diligence**."

#### Control Objective: P1, D2

- **Definition:** "targets or desired conditions to be met... statements describing what is to be achieved as a result of the organization implementing a Control, which is what a Standard is intended to address with organization-specific criteria."
- "Where applicable, Control Objectives are directly linked to laws, regulations and frameworks to align cybersecurity and data privacy with reasonably-expected practices. The intent is to establish sufficient evidence of due diligence and due care to withstand scrutiny."
- The quoted AICPA SSAE 18 definition says: "Control objectives address the risks that controls are intended to mitigate." This implies a link from control objectives to risks. P1 does not draw that link.
- **Diagram:**
  - "**Every Control Objective Maps To A Policy**."
  - "Leading Practices Define Expectations To Be Met (due diligence / due care)" feeds into Control Objectives.
  - "**Control Objectives Are Based On Controls**" is a dashed line from Controls up to Control Objectives.
- Footer: "Control Objectives support Policies and provide scoping for Standards, based on industry-recognized secure practices."

#### Standard: P1, D3

- **Definition:** "mandatory requirements regarding processes, actions and configurations that are designed to satisfy Controls and Control Objectives. Standards are intended to be granular and prescriptive." P1 adds that they establish "**Minimum Security Requirements (MSR)**".
- **Diagram:** "**Every Standard Maps To A Control Objective**."
- Footer: "Standards operationalize Policies by providing organization-specific requirements that must be met."
- **Exceptions are allowed at this level** (D2). The POA&M "Documents Deviations To Standards" (P1).

#### Guideline / Supplemental Guidance: P1, D3

- **Definition:** "recommended practices that are based on industry-recognized secure practices. Guidelines help augment Standards when discretion is permissible... [they] allow individuals / teams to apply discretion or leeway."
- **Diagram:** "Guidelines Support Applicable Standards."
- Guidelines are not mandatory (D1). So a guideline should never be the thing that satisfies a control.

#### Control: P1, D3

- **Definition:** "technical, administrative or physical safeguards... the nexus used to manage risks through preventing, detecting or lessening the ability of a particular threat from negatively impacting business processes."
- "Controls directly map to Standards, Procedures and Control Objectives. Control testing is designed to measure specific aspects of how Standards are actually implemented and if the Control / Control Objective is sufficiently addressed."
- **Owner:** "Controls are assigned to stakeholders to assign responsibilities in enforcing Standards" (P1 footer).
- **Diagram links:**
  - "**Every Control Maps To A Standard**."
  - Controls ↔ Procedures.
  - Controls → Control Objectives ("based on").
  - Influencers → Controls ("selected to meet").
  - Controls ↔ Risks, Threats and Metrics.
- The quoted ISO 27000 definition notes that controls "may not always exert the intended or assumed modifying effect". This is why controls are assessed.

#### Assessment Objective (AO): P1, D4

- **Definition:** "a set of determination statements that express the desired outcome for the assessment of a Control. AOs are the authoritative source of guidance for assessing Controls to generate evidence that can support an assertion that the underlying Control has been satisfied."
- "Generally, **all AOs must be satisfied** to legitimately conclude a Control is properly implemented" (D4).
- **Diagram:** AOs sit inside the Controls column. Dashed links run from AOs to Controls, Procedures and Standards.

#### Procedure / Control Activity: P1, D4

- **Definition:** "a documented set of steps necessary to perform a specific task or process in conformance with an applicable standard." Procedures "help address the question of how the organization actually operationalizes a Policy, Standard or Control."
- **Owner:** "generally the responsibility of the process owner / asset custodian to build and maintain, but are expected to include stakeholder oversight to ensure applicable compliance requirements are addressed."
- "The result of a procedure is intended to satisfy a specific Control." Procedures are "also commonly referred to as 'control activities.'"
- **Diagram:** "**Every Procedure Maps To A Control**."
- **Due care:** P1 says "Without documented procedures, there will be no defensible evidence of due care practices." D4 prints "there can be defendable evidence", which appears to be a typo. Follow the P1 wording, which agrees with the footer: "The output of Procedures is evidence of due care."
- **Exceptions are allowed at this level** (D2).

#### Risk: P1, D5

- **Definition:** "a potential exposure to danger, harm or loss" (D5). P1 gives a noun and a verb form: "a situation where someone or something valued is exposed to danger, harm or loss".
- Footnotes define three terms:
  - Danger: "state of possibly suffering harm or injury".
  - Harm: "material / physical damage".
  - Loss: "destruction, deprivation or inability to use".
- "**Risk is associated with a control deficiency** (e.g., If the control fails, what risk(s) is the organization exposed to?)"
- **Scoring:** "often calculated by a formula of the **Occurrence Likelihood (OL)** (e.g., probability of the event) x the **Impact Effect (IE)** (e.g., potential, negative consequences)."
- **Treatment:** "manage risks by avoiding, reducing, transferring, or accepting the risks." A totally risk-free environment is not possible.
- "An organization should maintain a '**risk catalog**' that contains organization-specific risks" (P1).
- **Diagram:** "**Every Risk Maps To A Control**."

#### Threat: P1, D4

- **Definition:** "a person or thing likely to cause damage or danger." P1 adds a verb form: "to indicate impending damage or danger".
- "Natural and man-made threats affect control execution (e.g., if the threat materializes, will the control function as expected?)."
  - Natural threats: tornados, earthquakes, solar flares.
  - Man-made threats: hacking, riots, theft, terrorism, war.
- "An organization should maintain a '**threat catalog**' that contains organization-specific natural and man-made threats applicable to its business operations and technologies in use" (P1).
- **Diagram:** "**Every Threat Maps To A Control**."

#### Metric: P1, D5

- **Definition:** "a 'point in time' view of specific, discrete measurements, unlike trending and analytics that are derived by comparing a baseline of two or more measurements taken over a period of time. Analytics are generated from the analysis of metrics."
- Good metrics are **SMART**: Specific, Measurable, Attainable, Repeatable, Time-dependent (P1).
- Footer: "Metrics provide evidence of an oversight function... by measuring criteria to determine performance."
- **Diagram:** "**Every Metric Maps To A Control**."

#### Supporting compliance documentation: P1, D6

| Artifact | HCGF definition | Diagram link |
|---|---|---|
| **Secure Baseline Configurations / Hardening Standard** | "Technical in nature and specify the required configuration settings for a defined technology platform." The quoted NIST definition adds that a baseline is "formally reviewed and agreed on at a given point in time, and which can be changed only through change control procedures... used as a basis for future builds, releases, and/or changes." Sources are CIS Benchmarks, DISA STIGs and OEM recommendations. | "Secure Technical Configurations **Implement Standards**" → Standards |
| **Risk Register / POA&M** | A "**living document**" that "summarizes control deficiencies from identification through remediation... tracks the assignment of remediation efforts to individuals or teams". It also covers tasks, resources, milestones and dates. Per the quoted NIST definition, a risk register holds "both accepted risks and risk that have a planned mitigation path". | "**Documents Deviations To Standards**" → Standards |
| **SSP / SSPP** | A "**living document**" that "summarizes protection mechanisms for a system or project... meant to reference an organization's existing policies, standards and procedures and **is not a substitute** for that documentation." Per the quoted NIST definition, it describes "controls in place or planned". | "**Summarizes Protection Mechanisms**" → Standards, Controls, Procedures |

### 3.4 Traceability summary (P1 "Every X Maps To A Y" and related links)

| Relationship | Strength in HCGF | Source |
|---|---|---|
| Control Objective → Policy | **every** (mandatory) | P1 label |
| Standard → Control Objective | **every** | P1 label |
| Control → Standard | **every** | P1 label |
| Procedure → Control | **every** ("a specific Control") | P1 label, D4 |
| Risk → Control | **every** | P1 label |
| Threat → Control | **every** | P1 label |
| Metric → Control | **every** | P1 label |
| Control → Control Objective | "Controls directly map to... Control Objectives"; "Control Objectives Are Based On Controls" | D3, P1 |
| Guideline → Standard | "support applicable standards" (no "every") | P1 |
| AO → Control (and → Standard, Procedure) | AO assesses a Control; all AOs must be satisfied | D4, P1 |
| External influencer → Policy, Control Objective | primary source for policy need; scopes control objectives | P1 |
| Internal influencer → Policy | drives policy development | P1 |
| Influencers → Control | controls "should be selected to meet" influencers | P1 |
| Control Objective → law / regulation / framework | "where applicable, directly linked" | D2 |
| Control Objective → Risk | "address the risks that controls are intended to mitigate" (SSAE 18 quote) | D2 |
| Secure Baseline → Standard | implements | P1 |
| POA&M → Standard | documents deviations | P1 |
| SSP → Standard, Control, Procedure | summarizes | P1 |

The main stack is drawn with two-way arrows: Policies ↔ Control Objectives ↔ Standards ↔ Controls ↔ Procedures. The "Every" labels set the mandatory direction: each lower component must point upward.

HCGF does **not** require any downward completeness. It never says a policy must have a control objective, or a control must have a procedure. A reviewer may recommend such checks as advisories, using the defensibility argument, but must label them as going beyond HCGF.

---

## 4. What a well-formed HCGF governance slice looks like

- **Influencers** for every law, regulation and contract in scope. Each one cites the authoritative source (title, issuing party, location). Internal influencers are recorded where they drive policy.
- **Policies**, one or more per domain. Each is a short, technology-independent statement (1–3 sentences per D2), driven by influencers, with an executive owner or approver.
- **Control objectives**, each supporting at least one policy. Each is linked to the laws or frameworks it derives from, where applicable.
- **Standards** with measurable, mandatory language ("must"). Discretionary language ("should", "recommended") belongs in guidelines.
- **Controls**, possibly drawn from a catalog such as SCF. Each has a stakeholder owner, enforces at least one standard and achieves at least one control objective. Each has assessment objectives.
- **Procedures** (control activities), each with a process owner or asset custodian. Each operationalizes a specific control and conforms to an applicable standard.
- **Threats and risks** drawn from organization-specific catalogs. Each maps to a control. Each risk has a treatment (avoid, reduce, transfer or accept).
- **Exceptions**: accepted deviations against standards or procedures only. Each records who accepted it and when it will be reviewed.
- **Metrics** that are SMART and tied to controls.
- **Secure baselines** that implement standards, cite their source (CIS, STIG, OEM) and change only through change control.
- **SSP and POA&M** that refer back to the core components instead of restating them.

---

## 5. Review checklist

Phrase each finding against **the governance model or specification under review**. Each item names the HCGF concept it enforces.

### A. Hierarchy completeness (upward traceability)

- [ ] **A1** Every control objective maps to at least one policy, and the specification enforces this. *(P1 "Every Control Objective Maps To A Policy")*
- [ ] **A2** Every standard maps to at least one control objective. *(P1 "Every Standard Maps To A Control Objective")*
- [ ] **A3** Every control maps to at least one standard and at least one control objective. *(P1 "Every Control Maps To A Standard"; D3)*
- [ ] **A4** Every procedure maps to a specific control. *(P1 "Every Procedure Maps To A Control"; D4)*
- [ ] **A5** Every guideline supports at least one standard. *(P1 "Guidelines Support Applicable Standards")*
- [ ] **A6** Every risk maps to a control, including risks that are avoided, transferred or accepted. *(P1 "Every Risk Maps To A Control")*
- [ ] **A7** Every threat maps to at least one control. *(P1 "Every Threat Maps To A Control")*
- [ ] **A8** Every metric maps to a control. *(P1 "Every Metric Maps To A Control")*
- [ ] **A9** Each "every" relationship is enforced, not just allowed. The specification shows how a violation is detected and reported. *(D2 defensibility)*

### B. Authority and scoping

- [ ] **B1** Influencers can be classified as statutory, regulatory, contractual or internal. One influencer can carry more than one kind. *(P1)*
- [ ] **B2** An influencer can cite its authoritative source (title, issuing party, location), including sources outside the organization. Examples: a law, or a provider's SOC 2 report. *(P1)*
- [ ] **B3** A policy that no influencer drives is at least flagged. *(P1 "Policies usually exist to satisfy an external requirement")*
- [ ] **B4** A control objective can link to the laws, regulations and frameworks it derives from. *(D2)*
- [ ] **B5** One framework can serve as both an obligation (influencer) and a source of control objectives or controls, without being duplicated. *(D1 pyramid; P1 contractual list; P1 SCF note)*
- [ ] **B6** Controls can be traced to the influencers they were selected to meet. *(P1 "Appropriate Controls Should Be Selected To Meet Specified External & Internal Influencers")*
- [ ] **B7** Requirements analysis is visible: it is possible to see why an influencer is in scope. *(P1 "requirements analysis... to appropriately scope security program requirements")*

### C. Terminology and layer discipline

- [ ] **C1** Each component type is defined using HCGF's definitions or a cited equivalent. *(D1 "words have meanings")*
- [ ] **C2** Policies are short, strategic and technology-independent. They contain no configuration values, technology names or "how" steps. *(D2; NIST "what/why, not how")*
- [ ] **C3** Standards are mandatory and guidelines are discretionary. A guideline can never be what satisfies a control. *(D1, D3)*
- [ ] **C4** No component type is overloaded. The word "requirement", "policy" or "standard" means one thing throughout. *(D2 policy vs. standard misuse)*
- [ ] **C5** "Procedure" and "control activity" are treated as synonyms, not as two separate types. *(D4)*
- [ ] **C6** Controls are classifiable as technical, administrative or physical safeguards. *(D3)*

### D. Exceptions and risk acceptance

- [ ] **D1** Exceptions can attach only to standards or procedures. No path lets a policy (or control objective) be excepted. *(D2 "never a justifiable reason to have an exception to a policy")*
- [ ] **D2** An exception is recorded as an accepted risk, with who accepted it. *(D5 accept strategy; P1 POA&M "Documents Deviations To Standards")*
- [ ] **D3** Exceptions have a review or expiry date. *(Common GRC practice. HCGF does not state it explicitly.)*

### E. Ownership and accountability

- [ ] **E1** Every control has a stakeholder owner. *(P1 "Controls are assigned to stakeholders")*
- [ ] **E2** Every procedure has a process owner or asset custodian, plus stakeholder oversight. *(D4)*
- [ ] **E3** Every policy has an approver or owner from executive leadership. *(P1, D2)*
- [ ] **E4** Remediation items in the risk register / POA&M are assigned to individuals or teams. *(D6)*

### F. Assessment and evidence

- [ ] **F1** Every control has at least one assessment objective. *(D4 "all AOs must be satisfied")*
- [ ] **F2** An AO's standards and procedures are consistent with the control it assesses. That means the standards that control enforces and the procedures that operationalize it. *(P1 AO links; D3 control testing)*
- [ ] **F3** It is clear what evidence demonstrates due diligence (policies) and due care (procedure outputs). *(P1 footer)*
- [ ] **F4** Metrics can express SMART criteria: a target or threshold, and a measurement frequency. *(P1 SMART)*
- [ ] **F5** Metrics (point-in-time) are kept separate from analytics (trends derived from two or more measurements). *(D5)*

### G. Risk and threat

- [ ] **G1** Risk treatment options are exactly avoid, reduce, transfer and accept. *(D5, P1)*
- [ ] **G2** Threats can be natural or man-made, including physical and supply-chain threats. *(D4; P1 SCRM)*
- [ ] **G3** Risks can be tied to the control whose deficiency would expose them. *(D5 "associated with a control deficiency")*
- [ ] **G4** Risk scoring supports Occurrence Likelihood × Impact Effect, on a defined scale. *(D5)*
- [ ] **G5** Organization-specific risk and threat catalogs exist and can be reused. *(P1 "risk catalog", "threat catalog")*
- [ ] **G6** A control objective can reference the risks it addresses. *(D2 SSAE 18 quote; advisory)*

### H. Supporting documentation

- [ ] **H1** Each secure baseline implements at least one standard and cites its source (CIS, STIG or OEM). *(D6; P1 "Secure Technical Configurations Implement Standards")*
- [ ] **H2** A secure baseline changes only through change control. Its agreed point-in-time version is identifiable. *(D6)*
- [ ] **H3** The SSP references policies, standards, controls and procedures, and does not replace them. *(D6 "not a substitute")*
- [ ] **H4** The risk register / POA&M records deviations from standards and remediation of control deficiencies. *(D6; P1)*

### I. Maintenance and auditability

- [ ] **I1** Components carry a status (for example, draft, approved, retired). The approved state can be told apart from proposals. *(D2 "formally expressed by management"; D6 "formally reviewed and agreed")*
- [ ] **I2** Retiring a policy, control or standard keeps it findable, with a pointer to its replacement, so the audit trail survives. *(D2 defensibility)*
- [ ] **I3** When controls come from an external catalog, the catalog version used is identifiable. *(P1 SCF; D2 defensibility)*
- [ ] **I4** A control that is inherited from a third party (for example, through a provider's SOC 2 report) names that party and its attestation. *(P1 SOC 2 as an influencer)*

---

## 6. Red flags and anti-patterns

- **Orphaned control:** no standard or no control objective (P1).
- **Floating control objective:** no policy (P1).
- **Orphaned procedure:** no control, or spread across many controls with no clear "specific Control" (D4).
- **Policy with no authority:** no influencer and no stated internal rationale (P1).
- **Policy written as a standard:** technology names, configuration values or "how" steps in a policy (D2).
- **Standard written as a guideline:** "should", "recommended" or "where possible" in a standard. Also a guideline used to satisfy a control (D1, D3).
- **Policy exception:** any exception against a policy, including one hidden in free-text rationale (D2).
- **Unaccepted deviation:** an exception with no accepting party or review date.
- **Threat or risk with no control:** violates P1 "Every Threat/Risk Maps To A Control".
- **Unassessable control:** a control with no assessment objectives (D4).
- **Vanity metric:** a metric tied to no control, or not SMART (P1).
- **SSP as the source of truth:** a narrative SSP that restates, and drifts from, policies and standards (D6).
- **Undocumented procedures:** controls that rely on unwritten practice, which leaves "no defensible evidence of due care" (P1).
- **Unsourced baseline:** hardening settings with no CIS, STIG or OEM source and no change control (D6).
- **Untraceable catalog:** controls copied in by hand with no record of which catalog or version they came from.
- **Undefined qualifiers:** rules or definitions that use undefined terms such as "governance risk" or "critical control".

---

## 7. Open questions and gaps

### 7.1 What HCGF says (and does not say) about risk

**What it says:**

- **Definition:** "a potential exposure to danger, harm or loss" to "someone or something valued" (D5, P1). Danger, harm and loss are each defined (D5).
- **Cause:**
  - Threats "affect control execution" (D4).
  - Risk is "associated with a control deficiency" (D5).
  - So the chain is **threat → control (failure or deficiency) → risk**.
  - The quoted NIST definitions add that the impacts fall on "organizational operations... assets, individuals, other organizations, and the Nation" (D5).
- **Scoring:** Occurrence Likelihood × Impact Effect (D5).
- **Treatment:** avoid, reduce, transfer or accept (D5, P1).
- **Mapping:** every risk maps to a control. Every threat maps to a control (P1).
- **Catalogs:** keep organization-specific risk and threat catalogs (P1).
- **Control objectives:** per the quoted SSAE 18 definition, control objectives "address the risks that controls are intended to mitigate" (D2).
- **Risk register / POA&M:** a "living document" covering accepted risks and risks with planned mitigation, from identification through remediation (D6).

**What it does not say:**

- No scale or units for likelihood or impact.
- No distinction between inherent and residual risk.
- No risk appetite or tolerance thresholds.
- No guidance on how often risks are reassessed.
- No rule for which control a risk maps to when its treatment is avoid, transfer or accept.
- No requirement for an expiry date on accepted risks.
- No method for deriving risks from threats (for example, per asset or per data flow).

Any position a specification takes on these points goes beyond HCGF. Do not cite HCGF for it.

### 7.2 Other open questions for the reviewer

- **Downward completeness.** HCGF does not require a policy to have objectives, or a control to have a procedure. Should the specification add advisory checks for these?
- **Procedure-to-standard link.** D4 says a procedure conforms to "an applicable standard". Is that standard required to be one of the standards its control enforces?
- **Stakeholder oversight of procedures (D4).** How is it recorded?
- **Organizational vs. system scope.** Policies and standards are organization-wide. SSPs and secure baselines are per system. How does the specification connect the two levels?
- **Living documents.** How do the POA&M and SSP stay consistent with the core components they summarize?
- **Source discrepancy.** D4 says "there can be defendable evidence of due care". P1 says "there will be no defensible evidence" without documented procedures. Cite the P1 wording.

---

## 8. Sources

- ComplianceForge, *ComplianceForge Reference Model: Hierarchical Cybersecurity Governance Framework (HCGF)*, Version 2023.3, © 2023 ComplianceForge, LLC. Local copy: `/Users/maxdunn/Downloads/Hierarchical_Cybersecurity_Governance_Framework.pdf` (7 PDF pages, all read). Online: https://www.complianceforge.com/grc/hierarchical-cybersecurity-governance-framework/ (cited in D1, footnote 1).
- Secondary definitions quoted inside the HCGF PDF (not consulted separately): ISACA Glossary; ISO 704:2009; ISO 27000:2016; ISO 13335-1; NIST Glossary (CSRC); NIST SP 800-53 R5; AICPA SSAE No. 18.
- External frameworks HCGF positions:
  - Secure Controls Framework: a control catalog (P1).
  - NIST CSF, ISO 27001 and NIST SP 800-53: control frameworks linked to control objectives (D1).
  - CIS Benchmarks, DISA STIGs and OEM guidance: sources for secure baselines (D6).
