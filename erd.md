```mermaid
erDiagram

  %% Rules and derivations
  %% Each rule and derivation has an ID (SECTION-n). An ID is never renumbered or reused; a removed rule retires its ID.
  %% Retired: RISK-3, C4-9, C4-18, DFD-2, DFD-16 (now link cardinality).
  %% A rule marked (should) has severity warning; every other rule has severity error.
  %% A rule or derivation that uses a derivation cites its ID in brackets.
  %% A guidance line is review advice that cannot be checked mechanically; it is not a rule and has no ID.

  %% Document
  %% The document is the unit of distribution; its fields are the header, not an item.

  DOCUMENT {
    string id "package name, e.g. openemr; required"
    string version "semver; required"
    string intentSpec "contract version; required"
    string stage "proposed | ratified | deprecated; the stage of every item that states none; required"
  }
  DOCUMENT ||--o{ IMPORT: has

  IMPORT {
    string alias "local prefix in alias:id; unique in the document; required"
    string source "where the imported document is fetched from; required"
    string version "semver range; required"
  }
  %% the lockfile sits beside the document and, per import alias, records source, resolved version, digest, the imported document's stage and a snapshot of items keyed by type and id, each with its stage resolved [DOC-2]
  %% the snapshot holds the referenced items plus their closure over outgoing links and over contained items (items whose in points at a snapshotted item, e.g. a profile's selections), stopping at external references
  %% ids inside a snapshot are read relative to its alias; rules that follow links into an import read the snapshot, never the fetched document
  %% rule DOC-1: removing or renaming an item id is a breaking change (major version)

  %% Serialization
  %% A document is one YAML or JSON object. Its top-level keys are the DOCUMENT fields, imports (a map from alias to {source, version}) and one key per entity type.
  %% An entity type's key is its name in camelCase with the last word pluralised by adding s (JOB_EXECUTOR jobExecutors, DATA_FLOW_DIAGRAM dataFlowDiagrams), except:
  %% PERSON people, POLICY policies, PROCESS processes, EXTERNAL_ENTITY externalEntities, TRUST_BOUNDARY trustBoundaries.
  %% Each entity type's value is a map from item id to the item's fields; nothing nests, so an item's JSON pointer is /<key>/<id>.
  %% An item id, the document id and an import alias match ^[a-z0-9]+(-[a-z0-9]+)*$, so a pointer needs no ~0 or ~1 escaping.
  %% A reference is an id or alias:id; the colon tells them apart because no id contains one.
  %% A link is a field on its source item named after its verb, containment included (in). A to-one link (|| or o| at the target) holds one reference; a to-many link (|{ or o{) holds a list.
  %% An attribute whose type ends in [] is a list of values of that type; its description says "one or more" (minItems 1) or "zero or more". Any other attribute holds one value of its type.
  %% ruleWaivers is an object whose keys are rule IDs as written here (e.g. GRC-25) and whose values are rationale strings.

  %% References
  %% Every link below is a reference. Its target is a local item id or an imported alias:id.
  %% Only a link drawn to EXTERNAL_REFERENCE may instead target the id of an external reference
  %% for things outside intent-spec: job cites, outcome cites, adoption inherits, influencer cites, influencer binds, secure baseline derives.

  EXTERNAL_REFERENCE {
    string title "free text; required"
    string url "optional"
    string party "who it comes from, e.g. AWS; optional"
    string version "edition or date; optional"
  }
  %% Every item has a document-unique id. Items never nest: containment is the link in, drawn from the contained item to its container like any other link.
  %% Rule prose says X contains Y (or hosts Y) to mean Y in X.
  %% Every item except an external reference, which is not intent, has a stage: proposed | ratified | deprecated. An item states its stage only where it differs from the document's stage.
  %% derived DOC-2: an item's stage is its own stage, or else the document's stage; every rule that names a stage means this one
  %% A deprecated item names its replacement (replacedBy) or, when nothing replaces it, gives a deprecationRationale.
  %% Every item may also have a name and a description (free text, optional); they are not repeated in each entity. Rule C4-1 asks for both on C4 elements.
  %% Every item may also have ruleWaivers (optional): a map from the ID of a (should) rule to a rationale for why that warning does not apply to the item. A checker reports a waived warning as waived, with its rationale, instead of dropping it. (A treatment's waives link is unrelated: it waives standards and procedures.)
  %% rule DOC-3: every key of an item's ruleWaivers is the ID of a (should) rule; waiving an error-severity rule or an unknown ID is itself an error
  %% An attribute is optional unless marked required. An optional attribute without a stated default is absent when omitted; a list attribute marked "one or more" is required and non-empty.
  %% A date is an ISO 8601 calendar date string (YYYY-MM-DD). Loaders parse YAML with the YAML 1.2 JSON or core schema, so an unquoted date stays a string, never a timestamp.
  %% rule REF-1: a link not drawn to EXTERNAL_REFERENCE resolves to a local or imported item; an external reference there is a type error
  %% rule REF-2: where allowed, an external reference satisfies a link's cardinality; rules that inspect the target skip it
  %% rule REF-3: a ratified item does not link to a proposed item [DOC-2]
  %% rule REF-4 (should): a ratified item does not link to a deprecated item, except a review of a deprecated target [DOC-2]
  %% rule REF-5: coverage rules apply only to items declared in this document; an imported or external system is treated as external

  %% Links
  %% Lines with the same source and verb are one link, stored as one field on the source item. Its target may be any entity type drawn for it.
  %% Every line of a link carries the same cardinality, counted over all its targets together:
  %% RELATIONSHIP }o--|| PERSON: leaves and RELATIONSHIP }o--|| SYSTEM: leaves mean a relationship leaves exactly one person or system.
  %% Where cardinality would differ per target type, the link uses a different verb per type.
  %% rule REF-6: a link's target is an item of an entity type drawn for that link; generated from the ERD for every link, so other rules do not repeat it

  %% Product
  %% Constraints and forces of progress are deliberately out of scope.

  PRODUCT
  PRODUCT }o--o{ JOB: targets
  %% rule PRODUCT-1: every ratified product targets at least one job
  %% rule PRODUCT-2: a job targeted by a ratified product has at least one ratified outcome

  JOB_EXECUTOR {
    string description "the person or group who does the job, described by role (the JTBD job executor); required"
  }
  %% rule PRODUCT-3 (should): every job executor is motivated by at least one job

  JOB {
    string statement "required; from the executor's perspective; may include the circumstance, e.g. when planning next week's shifts"
    enum kind "core | related | consumption | purchase; optional, default core"
  }
  %% a core job is what the product is hired for; a related job is done alongside it; a consumption job is about living with the product (setting up, upgrading, running it); a purchase job is choosing and paying for it, and its executor is the buyer
  %% guidance: the statement of a core or related job, and of its outcomes, is solution-free; a consumption or purchase job and its outcomes may name the product
  %% a purchase job's outcomes are usually served by commercial commitments (pricing, terms, procurement paperwork): requirements with a verification that no system, container, component or deployment node satisfies [C4-8]
  JOB }o--|| JOB_EXECUTOR: motivates
  JOB }o--o{ EXTERNAL_REFERENCE: cites

  OUTCOME {
    string statement "required; measurable"
    enum disposition "out-of-scope | overserved | deferred; optional"
    string rationale "required with a disposition"
  }
  OUTCOME }o--|| JOB: in
  OUTCOME }o--o{ PRODUCT: scopes
  OUTCOME }o--o{ EXTERNAL_REFERENCE: cites
  %% disposition: out-of-scope means the products it applies to will not serve the outcome; deferred means they will, but not yet; overserved means they already satisfy it beyond what executors value, so no further requirements will be added for it
  %% derived PRODUCT-7: a disposition applies to the products the outcome scopes, or to every product that targets its job when it scopes none
  %% rule PRODUCT-4: an outcome scopes products only when it has a disposition, and only products that target its job
  %% rule PRODUCT-5: for every ratified product that targets its job, every ratified outcome is served by at least one ratified requirement that applies to that product [PRODUCT-8] or has a disposition that applies to it [PRODUCT-7], never both unless that disposition is overserved

  REQUIREMENT {
    string statement "required"
    string verification "how satisfaction is checked; required"
  }
  %% a requirement is a solution-side commitment the team builds; mandatory organisational requirements are STANDARDs
  REQUIREMENT }o--o{ OUTCOME: serves
  REQUIREMENT }o--o{ TREATMENT: executes
  REQUIREMENT }o--o{ ADOPTION: implements
  REQUIREMENT }o--o{ PRODUCT: scopes
  %% derived PRODUCT-8: a requirement applies to the products it scopes; when it scopes none, it applies to every product that targets the job of an outcome it serves, every product governed by an adoption it implements, and every product a treatment it executes applies to [RISK-17]
  %% rule PRODUCT-6: every requirement serves an outcome, executes a treatment, implements an adoption or is cited by a threat review

  %% Measurement (shared by product and governance)

  METRIC {
    string target "threshold; required"
    string frequency "required"
  }
  METRIC }o--o{ CONTROL: measures
  METRIC }o--o{ OUTCOME: measures
  %% rule METRIC-1: every metric measures at least one control or outcome
  %% guidance: a metric that measures an outcome tracks that outcome's own measure from the executor's side (time to see a trend, automations lost offline); a product-side threshold such as script size or load time belongs in a requirement's statement or verification

  %% Risk

  THREAT {
    enum category "spoofing | tampering | repudiation | information-disclosure | denial-of-service | elevation-of-privilege | other; required"
    enum[] appliesTo "external-entity | process | data-store | data-flow; zero or more; empty means not reviewed per DFD element"
    string rationale "required when appliesTo is outside the STRIDE-per-element set"
  }
  THREAT }o--o{ CONTROL: threatens
  %% threatens is HCGF's sense: the threat can stop the control working as expected (not "the control mitigates the threat")
  %% STRIDE-per-element set: external-entity S,R; process S,T,R,I,D,E; data-store T,R,I,D; data-flow T,I,D. Category other allows any appliesTo.
  %% rule RISK-1 (should): appliesTo is within the STRIDE-per-element set for the category, or the threat gives a rationale
  %% rule RISK-2 (should): every threat threatens at least one control, or some review of it cites a control or requirement

  THREAT_REVIEW {
    enum disposition "risk | covered | not-applicable; required"
    string rationale "required when not-applicable"
  }
  %% disposition: covered means the cited safeguards leave no exposure at the targets that needs an owner or a review date; risk means some exposure remains to own, even when a reduce treatment addresses it; not-applicable means the threat leaves no such exposure there even without safeguards, and the rationale says why
  THREAT_REVIEW }o--|| THREAT: reviews
  THREAT_REVIEW }o--o{ EXTERNAL_ENTITY: inspects
  THREAT_REVIEW }o--o{ PROCESS: inspects
  THREAT_REVIEW }o--o{ DATA_STORE: inspects
  THREAT_REVIEW }o--o{ DATA_FLOW: inspects
  THREAT_REVIEW }o--o| RISK: raises
  THREAT_REVIEW }o--o{ CONTROL: cites
  THREAT_REVIEW }o--o{ REQUIREMENT: cites
  %% rule RISK-16: a review inspects at least one target, and all its targets are of one kind
  %% rule RISK-4: every (threat, target) pair where the threat applies to the target's kind is inspected by exactly one review; one review records one disposition for every target it inspects
  %% rule RISK-5: a deprecated target keeps its reviews
  %% rule RISK-6: raises exactly one risk when disposition is risk; otherwise none
  %% rule RISK-7: cites at least one control or requirement when disposition is covered; otherwise none
  %% rule RISK-18 (should): a review whose disposition is not-applicable inspects no data flow that crosses a trust boundary [DFD-11]
  %% derived RISK-8: a DFD's products are those realized by the system it depicts, or by the system containing the container it depicts
  %% derived RISK-9: a review's products are the products [RISK-8] of every DFD that includes, or shows [DFD-20], an element it inspects
  %% rule RISK-10: when disposition is covered, for every product of the review [RISK-9], at least one cited control is adopted in mode system, procedure or inherited by that product, or at least one cited requirement applies to that product [PRODUCT-8] and is satisfied by a system that realizes that product, or by a container or component in one
  %% derived RISK-11: a threat poses every risk raised by a review of it

  RISK
  RISK }o--o{ OUTCOME: endangers
  %% rule RISK-12: every risk has at least one treatment

  TREATMENT {
    enum strategy "avoid | reduce | transfer | accept; required"
    string owner "accountable person; for accept, who accepted; required"
    date reviewBy "required when reduce or accept"
    string rationale "required unless reduce; names the removed feature, the receiving party, or why the risk is accepted"
  }
  TREATMENT }o--|{ RISK: treats
  TREATMENT }o--o{ PRODUCT: scopes
  TREATMENT }o--o{ STANDARD: waives
  TREATMENT }o--o{ PROCEDURE: waives
  %% derived RISK-17: a treatment applies to the products it scopes, or to every product in the document when it scopes none
  %% rule RISK-13: a reduce treatment is executed by at least one control or requirement
  %% rule RISK-14: a control executing a treatment is adopted in mode system, procedure or inherited by every product the treatment applies to [RISK-17]
  %% rule RISK-15: waives only when strategy is accept; a waiver applies only within the products the treatment applies to [RISK-17]

  %% GRC (HCGF)

  INFLUENCER {
    enum[] kinds "statutory | regulatory | contractual | internal; one or more"
    string scopeRationale "why it applies; required"
  }
  INFLUENCER }o--o| EXTERNAL_REFERENCE: cites
  INFLUENCER }o--o{ SYSTEM: binds
  INFLUENCER }o--o{ EXTERNAL_REFERENCE: binds
  PRODUCT }o--o{ INFLUENCER: answers
  %% rule GRC-1: a statutory, regulatory or contractual influencer cites exactly one source
  %% rule GRC-24: only a contractual influencer binds, and only external systems or external references that have a party; binds names the counterparty (an external reference's party), e.g. a BAA or DPA sub-processor or a hosting provider
  %% rule GRC-25 (should): an external system is bound by at least one contractual influencer when an external entity representing it connects a data flow carrying a data element that triggers a statutory or regulatory influencer
  %% derived GRC-27: an influencer applies to the products that answer it; a local influencer that no product answers applies to every product in the document, and an imported one to none
  %% rule GRC-33 (should): every influencer that applies to at least one product [GRC-27] is satisfied by at least one policy or cited by at least one control objective

  POLICY {
    string statement "management intent; required"
    string approver "the accountable authority that approves the policy, e.g. executive leadership, a board or maintainers; required"
  }
  POLICY }o--o{ INFLUENCER: satisfies
  %% rule GRC-2 (should): every policy satisfies at least one influencer

  CONTROL_OBJECTIVE {
    string statement "the desired result; required"
    string[] clauses "sections or clauses of the cited influencers' sources it answers, e.g. 45 CFR 164.312(b); zero or more"
  }
  CONTROL_OBJECTIVE }o--|{ POLICY: supports
  CONTROL_OBJECTIVE }o--o{ INFLUENCER: cites
  %% rule GRC-29: a control objective has clauses only when it cites at least one influencer
  %% rule GRC-34 (should): every influencer a control objective cites is satisfied by at least one policy it supports
  %% rule GRC-22 (should): every control objective is achieved by at least one control

  STANDARD {
    string statement "the mandatory, measurable requirement; required"
  }
  STANDARD }o--|{ CONTROL_OBJECTIVE: addresses
  %% rule GRC-23 (should): every standard is enforced by at least one control

  GUIDELINE
  GUIDELINE }o--|{ STANDARD: augments

  ASSESSMENT_OBJECTIVE {
    enum[] methods "examine | interview | test; one or more"
    string evidence "what an assessor should look for; required"
  }
  ASSESSMENT_OBJECTIVE }o--o{ STANDARD: verifies
  ASSESSMENT_OBJECTIVE }o--|| CONTROL: assesses
  ASSESSMENT_OBJECTIVE }o--o{ PROCEDURE: examines
  %% rule GRC-3: an assessment objective verifies only standards its control enforces
  %% rule GRC-4: an assessment objective examines only procedures that operationalize its control
  %% rule GRC-5 (should): every control is assessed by at least one assessment objective

  CONTROL {
    string statement "the safeguard; required"
    string owner "stakeholder; required"
    enum safeguard "technical | administrative | physical; required"
  }
  CONTROL }o--|{ STANDARD: enforces
  CONTROL }o--|{ CONTROL_OBJECTIVE: achieves
  CONTROL }o--o{ TREATMENT: executes
  %% derived GRC-6: a control's influencers are those its control objectives cite; a control objective that cites none contributes the influencers its policies satisfy

  PROCEDURE {
    string steps "what is done, in order; required"
    string owner "process owner / asset custodian; required"
    string overseer "stakeholder oversight; required"
  }
  PROCEDURE }o--|| CONTROL: operationalizes

  PROFILE {
    string owner "accountable authority for the profile's selections, who decides changes to the baseline; required"
  }
  PROFILE }o--o{ PROFILE: imports
  PRODUCT }o--o{ PROFILE: selects
  %% a profile is a company-level selection of controls (OSCAL profile); a product selects the profiles that apply to it
  %% a profile may import other profiles and narrow them with exclude selections, e.g. a product line's baseline minus one control
  %% derived GRC-31: a profile includes a control when it, or a profile it imports, includes it, and it does not exclude it
  %% rule GRC-32: profile imports have no cycles

  SELECTION {
    enum choice "include | exclude; required"
    string rationale "required when exclude"
  }
  SELECTION }|--|| PROFILE: in
  SELECTION }o--|| CONTROL: names
  %% rule GRC-8: at most one selection per (profile, control) pair

  ADOPTION {
    enum mode "system | procedure | inherited | delegated | excepted | not-applicable; required"
    string rationale "required when delegated or not-applicable"
    string decidedBy "who made the governance decision; required when inherited, delegated, excepted or not-applicable"
    string delegatedTo "the downstream party that must implement the control, e.g. the deploying customer; required when delegated, otherwise none"
    string owner "who is accountable for the control in this product; the control's owner defines it"
  }
  ADOPTION }o--|| CONTROL: adopts
  ADOPTION }o--|| PRODUCT: governs
  ADOPTION }o--o| ADOPTION: inherits
  ADOPTION }o--o| EXTERNAL_REFERENCE: inherits
  ADOPTION }o--o| TREATMENT: invokes
  ADOPTION }o--o{ PROCEDURE: follows
  %% rule GRC-7: an adoption follows only procedures that operationalize the adopted control
  %% rule GRC-9: at most one adoption per (product, control) pair
  %% rule GRC-10: a product has an adoption for every control that a profile it selects includes [GRC-31] (coverage)
  %% rule GRC-11: a system adoption is implemented by at least one requirement, every requirement implementing an adoption applies to the adoption's product [PRODUCT-8], a procedure adoption follows at least one procedure, and other modes do neither
  %% rule GRC-12: when mode is inherited, inherits exactly one target; otherwise none
  %% rule GRC-13: an external reference that an adoption inherits has a party
  %% inherited means the control is provided upstream, by a party the product relies on, e.g. a cloud provider; it is coverage
  %% rule GRC-30 (should): an adoption does not inherit an external reference whose party is the operator of an environment that serves the adoption's product; that operator is downstream, so the adoption is delegated
  %% rule GRC-14: an inherited adoption adopts the same control as the adoption it inherits
  %% rule GRC-15: an inheritance chain ends at a system or procedure adoption or an external reference (no cycles)
  %% rule GRC-28: when mode is not-applicable, none of the adopted control's influencers [GRC-6] applies [GRC-27] to the adoption's product
  %% delegated means the control applies but whoever runs or deploys the product must implement it; it is not coverage
  %% rule GRC-26 (should): a system or procedure adoption has an owner
  %% rule GRC-16: when mode is excepted, invokes exactly one treatment, which is an accept treatment that applies to [RISK-17] the adoption's product and waives every standard the adopted control enforces; otherwise none

  SECURE_BASELINE
  SECURE_BASELINE }o--|{ STANDARD: encodes
  SECURE_BASELINE }o--o| EXTERNAL_REFERENCE: derives
  SECURE_BASELINE }o--o{ DEPLOYMENT_NODE: hardens
  SECURE_BASELINE }o--o{ INFRASTRUCTURE_NODE: hardens
  %% derived GRC-17: a secure baseline hardens every node contained in, or hosted by, a deployment node it hardens
  %% rule GRC-18 (should): a secure baseline derives from a CIS benchmark, DISA STIG or vendor guide

  %% derived GRC-19: a product's system security plan (SSP) is its adoptions with their controls, standards, procedures, requirements and inheritance
  %% derived GRC-20: a product's customer responsibility matrix is its delegated adoptions
  %% derived GRC-21: a product's plan of action and milestones (POA&M) is the reduce treatments and accept waivers that apply to it [RISK-17]

  %% C4 (https://c4model.com/abstractions, https://c4model.com/diagrams)
  %% The landscape, context, container and component diagrams are fully derived. Dynamic and deployment diagrams store a scope; DFDs list their elements.
  %% The C4 code level is omitted: it is derived from source, not declared intent.
  %% rule C4-1 (should): every person, system, container and component has a name and a short description
  %% rule C4-2 (should): every container and component, and every stored relationship whose ends lie in different containers or systems, has a technology

  PERSON
  PERSON }o--o{ JOB_EXECUTOR: plays

  SYSTEM {
    string owner "team that builds and runs it; required on an internal system, optional on an external one"
    boolean external "not built and owned by the team that owns this document; optional, default false"
  }
  SYSTEM }o--o{ PRODUCT: realizes
  %% rule C4-3: a ratified internal system that realizes a product contains at least one container; a proposed one may stop at its system context [DOC-2]
  %% rule C4-4: an external system contains no containers
  %% rule C4-5: only an internal system realizes a product

  CONTAINER {
    enum kind "application | data-store; required"
    string technology
  }
  CONTAINER }o--|| SYSTEM: in
  %% rule C4-6 (should): only an application container contains components

  COMPONENT {
    string technology
  }
  COMPONENT }o--|| CONTAINER: in

  SYSTEM }o--o{ REQUIREMENT: satisfies
  CONTAINER }o--o{ REQUIREMENT: satisfies
  COMPONENT }o--o{ REQUIREMENT: satisfies
  DEPLOYMENT_NODE }o--o{ REQUIREMENT: satisfies
  %% a deployment node satisfies requirements about the host itself, e.g. a hardened operating system image
  %% rule C4-8: every ratified requirement is satisfied by at least one system, container, component or deployment node, unless it serves only outcomes of purchase jobs and executes no treatment and implements no adoption

  RELATIONSHIP {
    string description "specific, consistent with direction; avoid bare 'uses'"
    string technology
  }
  RELATIONSHIP }o--|| PERSON: leaves
  RELATIONSHIP }o--|| SYSTEM: leaves
  RELATIONSHIP }o--|| CONTAINER: leaves
  RELATIONSHIP }o--|| COMPONENT: leaves
  RELATIONSHIP }o--|| PERSON: enters
  RELATIONSHIP }o--|| SYSTEM: enters
  RELATIONSHIP }o--|| CONTAINER: enters
  RELATIONSHIP }o--|| COMPONENT: enters
  RELATIONSHIP }o--|| INFRASTRUCTURE_NODE: leaves
  RELATIONSHIP }o--|| INFRASTRUCTURE_NODE: enters
  %% a relationship is unidirectional and points from the requester to the responder
  %% rule C4-10: a relationship with an infrastructure-node end appears only in deployment diagrams
  %% rule C4-11: the two ends of a relationship are distinct and neither contains the other
  %% derived C4-12: a relationship implies one between each enclosing container or system of its source and of its destination, where neither contains the other, unless one is stored
  %% derived C4-13: an implied relationship's description and technology are those of the relationships that imply it; store one at the higher level to give it a curated label
  %% rule C4-25 (should): every stored relationship with an end at an application container that contains components is implied [C4-12] by a stored relationship with that end at one of its components

  %% derived C4-14: the document has one system landscape: every system and person, and the relationships between them
  %% derived C4-15: each internal system has a system context diagram: the system plus every person and system joined to it
  %% derived C4-16: each internal system with containers has a container diagram: its containers plus the people and systems joined to them
  %% derived C4-17: each application container with components has a component diagram: its components plus the containers, people and systems joined to them

  DYNAMIC_DIAGRAM
  DYNAMIC_DIAGRAM }o--|| REQUIREMENT: illustrates
  DYNAMIC_DIAGRAM }o--o| SYSTEM: depicts
  DYNAMIC_DIAGRAM }o--o| CONTAINER: depicts
  %% the system or container a dynamic diagram depicts sets its C4 level; with neither it is a landscape-level diagram

  DYNAMIC_STEP {
    int order "position of the step in its diagram; required"
    string description "optional; overrides the relationship's description"
    enum direction "request | response; optional, default request; a response runs from the relationship's destination back to its source"
  }
  DYNAMIC_STEP }|--|| DYNAMIC_DIAGRAM: in
  DYNAMIC_STEP }o--|| RELATIONSHIP: follows
  %% rule C4-26: step order is unique among the steps in one dynamic diagram
  %% rule C4-19: a step is drawn between its relationship's ends lifted to the diagram's level [C4-12]: a component stays when the diagram depicts its container and otherwise lifts to its container; a container stays when the diagram depicts its system or any container and otherwise lifts to its system; the two drawn ends differ

  DEPLOYMENT_DIAGRAM {
    map notDeployed "container id to why it has no instance in the environment, e.g. runs in the visitor's browser; optional"
  }
  DEPLOYMENT_DIAGRAM }o--|{ SYSTEM: depicts
  DEPLOYMENT_DIAGRAM }o--|| ENVIRONMENT: covers
  %% derived C4-20: a deployment diagram shows the environment's nodes that host instances of its systems or their containers
  %% rule C4-23 (should): every container of a system a deployment diagram depicts has an instance on a node in the diagram's environment [C4-22], or is listed in its notDeployed
  %% notDeployed keys are references to CONTAINER, checked by REF-1 and REF-6 like links
  %% rule C4-24: a notDeployed key is a container of a system the diagram depicts that has no instance in the diagram's environment [C4-22]
  %% rule C4-27 (should): every ratified requirement that applies [PRODUCT-8] to a product the diagram's environment serves is satisfied by at least one system, container or component, or by a deployment node in the diagram's environment [C4-22]; a container listed in the diagram's notDeployed, such as a script that runs in the visitor's browser, and its components count

  ENVIRONMENT {
    string operator "who runs it, e.g. self-hosting operator; omit when the team that owns the document runs it"
  }
  ENVIRONMENT }o--|{ PRODUCT: serves
  %% an operator-run environment describes the reference topology the project ships, e.g. a Docker Compose host
  %% rule C4-28 (should): every ratified product that a system realizes is served by at least one environment

  DEPLOYMENT_NODE {
    string technology
  }
  DEPLOYMENT_NODE }o--o| ENVIRONMENT: belongs
  DEPLOYMENT_NODE }o--o| DEPLOYMENT_NODE: in
  %% rule C4-21: a node that no other node contains belongs to exactly one environment; a contained node belongs to none
  %% derived C4-22: a contained node's environment is that of the outermost node containing it

  SYSTEM_INSTANCE
  SYSTEM_INSTANCE }o--|| DEPLOYMENT_NODE: in
  SYSTEM_INSTANCE }o--|| SYSTEM: instantiates

  CONTAINER_INSTANCE
  CONTAINER_INSTANCE }o--|| DEPLOYMENT_NODE: in
  CONTAINER_INSTANCE }o--|| CONTAINER: instantiates

  INFRASTRUCTURE_NODE {
    string technology "e.g. DNS, load balancer, firewall"
  }
  INFRASTRUCTURE_NODE }o--|| DEPLOYMENT_NODE: in

  %% DFD (DFD3, https://github.com/adamshostack/DFD3)
  %% Five element types only: no multi-process or complex-process element.
  %% DFD elements are optional: model them only where someone threat-models. No C4 element needs a DFD counterpart.
  %% rule DFD-1 (should): every external entity, process, data store, data flow and trust boundary has a label

  EXTERNAL_ENTITY {
    string label
  }
  EXTERNAL_ENTITY }o--o| PERSON: represents
  EXTERNAL_ENTITY }o--o| SYSTEM: represents
  %% anything outside your control, including systems run by other teams
  %% rule DFD-3 (should): an external entity does not represent the system a DFD including it depicts, or the system containing the container it depicts

  PROCESS {
    string label
  }
  PROCESS }o--o| SYSTEM: represents
  PROCESS }o--o| CONTAINER: represents
  PROCESS }o--o| COMPONENT: represents
  PROCESS }o--o| INFRASTRUCTURE_NODE: represents
  %% any running code under your control, including a proxy, load balancer or ingress that terminates TLS
  %% rule DFD-4: a system a process represents is internal, and a container it represents is an application container

  DATA_STORE {
    string label
  }
  DATA_STORE }o--o| CONTAINER: represents
  DATA_STORE }o--|{ DATA_ELEMENT: stores
  %% anywhere data is stored, including files, shared memory and cookies
  %% rule DFD-5: a data store represents only a container whose kind is data-store

  DATA_ELEMENT {
    enum classification "public | internal | confidential | restricted; required"
  }
  DATA_ELEMENT }o--o{ INFLUENCER: triggers

  DATA_FLOW {
    string label
  }
  DATA_FLOW }o--o{ EXTERNAL_ENTITY: connects
  DATA_FLOW }o--o{ PROCESS: connects
  DATA_FLOW }o--o{ DATA_STORE: connects
  DATA_FLOW }o--o| EXTERNAL_ENTITY: leaves
  DATA_FLOW }o--o| PROCESS: leaves
  DATA_FLOW }o--o| DATA_STORE: leaves
  DATA_FLOW }o--|{ DATA_ELEMENT: carries
  DATA_FLOW }o--o{ RELATIONSHIP: represents
  %% a data flow is two-way by default; leaves marks the origination side when known
  %% rule DFD-6: a data flow connects exactly two distinct ends, at least one of them a process
  %% rule DFD-7: a data flow leaves at most one end, and that end is one it connects
  %% rule DFD-8: each end of a data flow represents an end of every relationship the flow represents, or an element containing it
  %% rule DFD-9: when a data flow leaves an end, every relationship it represents leaves the element that end represents, or one inside it
  %% rule DFD-10 (should): a data flow connecting an external entity and a process crosses at least one trust boundary [DFD-11], unless no trust boundary encloses the process; a process outside every boundary, such as client-side code on the user's own device, shares the external entity's trust level, and the boundary sits between it and the server
  %% derived DFD-11: a data flow crosses a trust boundary when exactly one end is inside it [DFD-15]

  TRUST_BOUNDARY {
    string label
    string crossing "what crossing is allowed; required"
  }
  TRUST_BOUNDARY }o--o{ EXTERNAL_ENTITY: encloses
  TRUST_BOUNDARY }o--o{ PROCESS: encloses
  TRUST_BOUNDARY }o--o{ DATA_STORE: encloses
  TRUST_BOUNDARY }o--o| TRUST_BOUNDARY: in
  TRUST_BOUNDARY }o--o{ CONTAINER: relies
  TRUST_BOUNDARY }o--o{ INFRASTRUCTURE_NODE: relies
  TRUST_BOUNDARY }o--o{ DEPLOYMENT_NODE: relies
  TRUST_BOUNDARY }o--o{ CONTROL: relies
  TRUST_BOUNDARY }o--o{ SYSTEM: relies
  %% rule DFD-12: every trust boundary relies on at least one container, infrastructure node, deployment node, control or system that enforces it, e.g. a host, VM, VPC or container runtime
  %% rule DFD-21: only an external system is relied on, for a boundary someone else enforces, e.g. a home router or a cloud provider's network
  %% rule DFD-13: an element is enclosed directly by at most one boundary
  %% rule DFD-14: boundary containment has no cycles
  %% derived DFD-15: an element is inside a boundary when that boundary, or one it contains, encloses it

  DATA_FLOW_DIAGRAM {
    enum level "context | detail; required"
  }
  DATA_FLOW_DIAGRAM }o--|| SYSTEM: depicts
  DATA_FLOW_DIAGRAM }o--|| CONTAINER: depicts
  DATA_FLOW_DIAGRAM }o--o{ EXTERNAL_ENTITY: includes
  DATA_FLOW_DIAGRAM }o--o{ PROCESS: includes
  DATA_FLOW_DIAGRAM }o--o{ DATA_STORE: includes
  %% unlike C4 diagrams, a DFD lists its elements: DFD elements need not map onto C4
  %% a context-level DFD is optional
  %% rule DFD-17: a context-level DFD depicts a system and includes exactly one process, which represents that system
  %% rule DFD-18 (should): in a detail DFD, every process represents a container of the depicted system, a component of the depicted container, or an infrastructure node on a node of an environment [C4-22] hosting an instance of the depicted system or the depicted container's system, or of one of that system's containers; or it connects a shown [DFD-20] data flow to a process that does
  %% rule DFD-19 (should): every data store and external entity in a DFD connects at least one data flow the DFD shows [DFD-20]
  %% derived DFD-20: a DFD shows every data flow whose two ends it includes, and every trust boundary enclosing an included element
```
