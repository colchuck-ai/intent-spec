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
  }
  DOCUMENT ||--o{ IMPORT: has

  IMPORT {
    string alias "local prefix in alias:id; unique in the document"
    string source "where the imported document is fetched from; required"
    string version "semver range; required"
  }
  %% the lockfile sits beside the document and, per import alias, records source, resolved version, digest and a snapshot of the referenced items
  %% rule DOC-1: removing or renaming an item id is a breaking change (major version)

  %% References
  %% Every link below is a reference. Its target is a local item id or an imported alias:id.
  %% Only a link drawn to EXTERNAL_REFERENCE may instead target the id of an external reference
  %% for things outside intent-spec: job cites, outcome cites, adoption inherits, influencer cites, secure baseline derives.

  EXTERNAL_REFERENCE {
    string title "free text; required"
    string url "optional"
    string party "who it comes from, e.g. AWS; optional"
    string version "edition or date; optional"
  }
  %% Every item has a document-unique id. Containment between items (contains, has, hosts) is a to-one link from the contained item to its container, like any other link; items never nest.
  %% Every item has a stage: proposed | ratified | deprecated; a deprecated item names its replacement (replacedBy) or, when nothing replaces it, gives a deprecationRationale.
  %% rule REF-1: a link not drawn to EXTERNAL_REFERENCE resolves to a local or imported item; an external reference there is a type error
  %% rule REF-2: where allowed, an external reference satisfies a link's cardinality; rules that inspect the target skip it
  %% rule REF-3: a ratified item does not link to a proposed item
  %% rule REF-4 (should): a ratified item does not link to a deprecated item, except a review of a deprecated target
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
    string description "the role in the moment of doing the job; required"
  }
  %% rule PRODUCT-3 (should): every job executor is motivated by at least one job

  JOB {
    string statement "required; solution-free, from the executor's perspective"
  }
  JOB }o--|| JOB_EXECUTOR: motivates
  JOB }o--o{ EXTERNAL_REFERENCE: cites
  JOB ||--o{ OUTCOME: has

  OUTCOME {
    string statement "required; solution-free and measurable"
    enum disposition "out-of-scope | overserved | deferred; optional"
    string rationale "required with a disposition"
  }
  OUTCOME }o--o{ PRODUCT: scopes
  OUTCOME }o--o{ EXTERNAL_REFERENCE: cites
  %% derived PRODUCT-7: a disposition applies to the products the outcome scopes, or to every product that targets its job when it scopes none
  %% rule PRODUCT-4: an outcome scopes products only when it has a disposition, and only products that target its job
  %% rule PRODUCT-5: for every ratified product that targets its job, every ratified outcome is served by at least one ratified requirement that applies to that product [PRODUCT-8] or has a disposition that applies to it [PRODUCT-7], never both

  REQUIREMENT {
    string statement "required"
    string verification "how satisfaction is checked; required"
  }
  %% a requirement is a solution-side commitment the team builds; mandatory organisational requirements are STANDARDs
  REQUIREMENT }o--o{ OUTCOME: serves
  REQUIREMENT }o--o{ TREATMENT: executes
  REQUIREMENT }o--o{ ADOPTION: implements
  REQUIREMENT }o--o{ PRODUCT: scopes
  %% derived PRODUCT-8: a requirement applies to the products it scopes, or to every product that targets the job of an outcome it serves when it scopes none
  %% rule PRODUCT-6: every requirement serves an outcome, executes a treatment, implements an adoption or is cited by a threat review

  %% Measurement (shared by product and governance)

  METRIC {
    string target "threshold; required"
    string frequency "required"
  }
  METRIC }o--o{ CONTROL: measures
  METRIC }o--o{ OUTCOME: measures
  %% rule METRIC-1: every metric measures at least one control or outcome

  %% Risk

  THREAT {
    enum category "spoofing | tampering | repudiation | information-disclosure | denial-of-service | elevation-of-privilege | other"
    enum appliesTo "external-entity | process | data-store | data-flow; zero or more; empty means not reviewed per DFD element"
  }
  THREAT }o--o{ CONTROL: threatens
  %% threatens is HCGF's sense: the threat can stop the control working as expected (not "the control mitigates the threat")
  %% rule RISK-1 (should): appliesTo is within the STRIDE-per-element set for the category, or the threat gives a rationale
  %% rule RISK-2 (should): every threat threatens at least one control

  THREAT_REVIEW {
    enum disposition "risk | covered | not-applicable"
    string rationale "required when not-applicable"
  }
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
  %% derived RISK-8: a DFD's products are those realized by the system it depicts, or by the system containing the container it depicts
  %% derived RISK-9: a review's products are the products [RISK-8] of every DFD that includes, or shows [DFD-20], an element it inspects
  %% rule RISK-10: when disposition is covered, for every product of the review [RISK-9], at least one cited control is adopted in mode system, procedure or inherited by that product, or at least one cited requirement is satisfied by a system that realizes that product, or by a container or component in one
  %% derived RISK-11: a threat poses every risk raised by a review of it

  RISK
  RISK }o--o{ OUTCOME: endangers
  %% rule RISK-12: every risk has at least one treatment

  TREATMENT {
    enum strategy "avoid | reduce | transfer | accept"
    string owner "accountable person; for accept, who accepted; required"
    date reviewBy "required when reduce or accept"
    string rationale "required unless reduce; names the removed feature, the receiving party, or why the risk is accepted"
  }
  TREATMENT }o--|{ RISK: treats
  TREATMENT }o--|{ PRODUCT: scopes
  TREATMENT }o--o{ STANDARD: waives
  TREATMENT }o--o{ PROCEDURE: waives
  %% rule RISK-13: a reduce treatment is executed by at least one control or requirement
  %% rule RISK-14: a control executing a treatment is adopted in mode system, procedure or inherited by every product the treatment scopes
  %% rule RISK-15: waives only when strategy is accept; a waiver applies only within the products the treatment scopes

  %% GRC (HCGF)

  INFLUENCER {
    enum kinds "statutory | regulatory | contractual | internal; one or more"
    string scopeRationale "why it applies; required"
  }
  INFLUENCER }o--o| EXTERNAL_REFERENCE: cites
  INFLUENCER }o--o{ SYSTEM: binds
  %% rule GRC-1: a statutory, regulatory or contractual influencer cites exactly one source
  %% rule GRC-24: only a contractual influencer binds, and only external systems; binds names the counterparty, e.g. a BAA or DPA sub-processor
  %% rule GRC-25 (should): an external system is bound by at least one contractual influencer when an external entity representing it connects a data flow carrying a data element that triggers a statutory or regulatory influencer

  POLICY {
    string approver "executive leadership; required"
  }
  POLICY }o--o{ INFLUENCER: satisfies
  %% rule GRC-2 (should): every policy satisfies at least one influencer

  CONTROL_OBJECTIVE
  CONTROL_OBJECTIVE }o--|{ POLICY: supports
  CONTROL_OBJECTIVE }o--o{ INFLUENCER: cites
  %% rule GRC-22 (should): every control objective is achieved by at least one control

  STANDARD
  STANDARD }o--|{ CONTROL_OBJECTIVE: addresses
  %% rule GRC-23 (should): every standard is enforced by at least one control

  GUIDELINE
  GUIDELINE }o--|{ STANDARD: augments

  ASSESSMENT_OBJECTIVE {
    enum methods "examine | interview | test; one or more"
    string evidence "what an assessor should look for; required"
  }
  ASSESSMENT_OBJECTIVE }o--o{ STANDARD: verifies
  ASSESSMENT_OBJECTIVE }o--|| CONTROL: assesses
  ASSESSMENT_OBJECTIVE }o--o{ PROCEDURE: examines
  %% rule GRC-3: an assessment objective verifies only standards its control enforces
  %% rule GRC-4: an assessment objective examines only procedures that operationalize its control
  %% rule GRC-5 (should): every control is assessed by at least one assessment objective

  CONTROL {
    string owner "stakeholder; required"
    enum safeguard "technical | administrative | physical"
  }
  CONTROL }o--|{ STANDARD: enforces
  CONTROL }o--|{ CONTROL_OBJECTIVE: achieves
  CONTROL }o--o{ TREATMENT: executes
  %% derived GRC-6: a control's influencers are those its control objectives cite, or that the policies they support satisfy

  PROCEDURE {
    string owner "process owner / asset custodian; required"
    string overseer "stakeholder oversight; required"
  }
  PROCEDURE }o--|| CONTROL: operationalizes
  PROCEDURE }o--o{ ADOPTION: implements
  %% rule GRC-7: a procedure implementing an adoption operationalizes the adopted control

  PROFILE
  PROFILE ||--|{ SELECTION: has
  PRODUCT }o--o{ PROFILE: selects
  %% a profile is a company-level selection of controls (OSCAL profile); a product selects the profiles that apply to it

  SELECTION {
    enum choice "include | exclude"
    string rationale "required when exclude"
  }
  SELECTION }o--|| CONTROL: names
  %% rule GRC-8: at most one selection per (profile, control) pair

  ADOPTION {
    enum mode "system | procedure | inherited | delegated | excepted | not-applicable"
    string rationale "required when delegated or not-applicable"
    string decidedBy "required when not-applicable"
    string delegatedTo "the downstream party that must implement the control, e.g. the deploying customer; required when delegated, otherwise none"
  }
  ADOPTION }o--|| CONTROL: adopts
  ADOPTION }o--|| PRODUCT: governs
  ADOPTION }o--o| ADOPTION: inherits
  ADOPTION }o--o| EXTERNAL_REFERENCE: inherits
  %% rule GRC-9: at most one adoption per (product, control) pair
  %% rule GRC-10: a product has an adoption for every control that a profile it selects includes (coverage)
  %% rule GRC-11: a system adoption is implemented by at least one requirement, a procedure adoption by at least one procedure, other modes by neither
  %% rule GRC-12: when mode is inherited, inherits exactly one target; otherwise none
  %% rule GRC-13: an external reference that an adoption inherits has a party
  %% rule GRC-14: an inherited adoption adopts the same control as the adoption it inherits
  %% rule GRC-15: an inheritance chain ends at a system or procedure adoption or an external reference (no cycles)
  %% guidance: not-applicable means the control's influencers [GRC-6] do not apply to the product
  %% delegated means the control applies but whoever runs or deploys the product must implement it; it is not coverage
  %% rule GRC-16: an excepted adoption's product is scoped by an accept treatment that waives every standard the adopted control enforces

  SECURE_BASELINE
  SECURE_BASELINE }o--|{ STANDARD: encodes
  SECURE_BASELINE }o--o| EXTERNAL_REFERENCE: derives
  SECURE_BASELINE }o--o{ DEPLOYMENT_NODE: hardens
  SECURE_BASELINE }o--o{ INFRASTRUCTURE_NODE: hardens
  %% derived GRC-17: a secure baseline hardens every node contained in, or hosted by, a deployment node it hardens
  %% rule GRC-18 (should): a secure baseline derives from a CIS benchmark, DISA STIG or vendor guide

  %% derived GRC-19: a product's system security plan (SSP) is its adoptions with their controls, standards, procedures, requirements and inheritance
  %% derived GRC-20: a product's customer responsibility matrix is its delegated adoptions
  %% derived GRC-21: a product's plan of action and milestones (POA&M) is the reduce treatments and accept waivers that scope it

  %% C4 (https://c4model.com/abstractions, https://c4model.com/diagrams)
  %% The landscape, context, container and component diagrams are fully derived. Dynamic and deployment diagrams store a scope; DFDs list their elements.
  %% The C4 code level is omitted: it is derived from source, not declared intent.
  %% rule C4-1 (should): every person, system, container and component has a name and a short description
  %% rule C4-2 (should): every container and component, and every stored relationship whose ends lie in different containers or systems, has a technology

  PERSON
  PERSON }o--o{ JOB_EXECUTOR: plays

  SYSTEM {
    string owner "team that builds and runs it; required"
    boolean external "not built and owned by the team that owns this document"
  }
  SYSTEM ||--o{ CONTAINER: contains
  SYSTEM }o--o{ PRODUCT: realizes
  %% rule C4-3: an internal system that realizes a product contains at least one container
  %% rule C4-4: an external system contains no containers
  %% rule C4-5: only an internal system realizes a product

  CONTAINER {
    enum kind "application | data-store"
    string technology
  }
  CONTAINER ||--o{ COMPONENT: contains
  %% rule C4-6 (should): only an application container contains components

  COMPONENT {
    string technology
  }

  SYSTEM }o--o{ REQUIREMENT: satisfies
  CONTAINER }o--o{ REQUIREMENT: satisfies
  COMPONENT }o--o{ REQUIREMENT: satisfies
  %% rule C4-7: only an internal system satisfies a requirement
  %% rule C4-8: every ratified requirement is satisfied by at least one system, container or component

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
  DYNAMIC_DIAGRAM ||--|{ DYNAMIC_STEP: has
  %% the system or container a dynamic diagram depicts sets its C4 level; with neither it is a landscape-level diagram

  DYNAMIC_STEP {
    int order "unique within the diagram"
    string description "optional; overrides the relationship's description"
    enum direction "request | response; optional, default request; a response runs from the relationship's destination back to its source"
  }
  DYNAMIC_STEP }o--|| RELATIONSHIP: follows
  %% rule C4-19: each end of a step's relationship is a person or a system, a container when the diagram depicts its system or any container, or a component when the diagram depicts its container

  DEPLOYMENT_DIAGRAM {
    map notDeployed "container id to why it has no instance in the environment, e.g. runs in the visitor's browser; optional"
  }
  DEPLOYMENT_DIAGRAM }o--|{ SYSTEM: depicts
  DEPLOYMENT_DIAGRAM }o--|| ENVIRONMENT: covers
  %% derived C4-20: a deployment diagram shows the environment's nodes that host instances of its systems or their containers
  %% rule C4-23 (should): every container of a system a deployment diagram depicts has an instance on a node in the diagram's environment [C4-22], or is listed in its notDeployed
  %% rule C4-24: a notDeployed key is a container of a system the diagram depicts that has no instance in the diagram's environment [C4-22]

  ENVIRONMENT {
    string operator "who runs it, e.g. self-hosting operator; omit when the team that owns the document runs it"
  }
  ENVIRONMENT }o--|{ PRODUCT: serves
  %% an operator-run environment describes the reference topology the project ships, e.g. a Docker Compose host

  DEPLOYMENT_NODE {
    string technology
  }
  DEPLOYMENT_NODE }o--o| ENVIRONMENT: belongs
  DEPLOYMENT_NODE |o--o{ DEPLOYMENT_NODE: contains
  DEPLOYMENT_NODE ||--o{ SYSTEM_INSTANCE: hosts
  DEPLOYMENT_NODE ||--o{ CONTAINER_INSTANCE: hosts
  DEPLOYMENT_NODE ||--o{ INFRASTRUCTURE_NODE: hosts
  %% rule C4-21: a node that no other node contains belongs to exactly one environment; a contained node belongs to none
  %% derived C4-22: a contained node's environment is that of the outermost node containing it

  SYSTEM_INSTANCE
  SYSTEM_INSTANCE }o--|| SYSTEM: instantiates

  CONTAINER_INSTANCE
  CONTAINER_INSTANCE }o--|| CONTAINER: instantiates

  INFRASTRUCTURE_NODE {
    string technology "e.g. DNS, load balancer, firewall"
  }

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
  %% any running code under your control
  %% rule DFD-4: a system a process represents is internal, and a container it represents is an application container

  DATA_STORE {
    string label
  }
  DATA_STORE }o--o| CONTAINER: represents
  DATA_STORE }o--|{ DATA_ELEMENT: stores
  %% anywhere data is stored, including files, shared memory and cookies
  %% rule DFD-5: a data store represents only a container whose kind is data-store

  DATA_ELEMENT {
    enum classification "public | internal | confidential | restricted"
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
  %% rule DFD-10 (should): a data flow connecting an external entity and a process crosses at least one trust boundary [DFD-11]
  %% derived DFD-11: a data flow crosses a trust boundary when exactly one end is inside it [DFD-15]

  TRUST_BOUNDARY {
    string label
    string crossing "what crossing is allowed; required"
  }
  TRUST_BOUNDARY }o--o{ EXTERNAL_ENTITY: encloses
  TRUST_BOUNDARY }o--o{ PROCESS: encloses
  TRUST_BOUNDARY }o--o{ DATA_STORE: encloses
  TRUST_BOUNDARY |o--o{ TRUST_BOUNDARY: contains
  TRUST_BOUNDARY }o--o{ CONTAINER: relies
  TRUST_BOUNDARY }o--o{ INFRASTRUCTURE_NODE: relies
  TRUST_BOUNDARY }o--o{ CONTROL: relies
  TRUST_BOUNDARY }o--o{ SYSTEM: relies
  %% rule DFD-12: every trust boundary relies on at least one container, infrastructure node, control or system that enforces it
  %% rule DFD-21: only an external system is relied on, for a boundary someone else enforces, e.g. a home router or a cloud provider's network
  %% rule DFD-13: an element is enclosed directly by at most one boundary
  %% rule DFD-14: boundary containment has no cycles
  %% derived DFD-15: an element is inside a boundary when that boundary, or one it contains, encloses it

  DATA_FLOW_DIAGRAM {
    enum level "context | detail"
  }
  DATA_FLOW_DIAGRAM }o--|| SYSTEM: depicts
  DATA_FLOW_DIAGRAM }o--|| CONTAINER: depicts
  DATA_FLOW_DIAGRAM }o--o{ EXTERNAL_ENTITY: includes
  DATA_FLOW_DIAGRAM }o--o{ PROCESS: includes
  DATA_FLOW_DIAGRAM }o--o{ DATA_STORE: includes
  %% unlike C4 diagrams, a DFD lists its elements: DFD elements need not map onto C4
  %% a context-level DFD is optional
  %% rule DFD-17: a context-level DFD depicts a system and includes exactly one process, which represents that system
  %% rule DFD-18 (should): in a detail DFD, every process represents a container of the depicted system or a component of the depicted container, or connects a shown [DFD-20] data flow to a process that does
  %% rule DFD-19 (should): every data store and external entity in a DFD connects at least one data flow the DFD shows [DFD-20]
  %% derived DFD-20: a DFD shows every data flow whose two ends it includes, and every trust boundary enclosing an included element
```
