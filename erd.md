```mermaid
erDiagram

  %% References
  %% Every link below is a reference. Its target is a local item id or an imported alias:id.
  %% Only a link drawn to EXTERNAL_REFERENCE may instead target the id of an external reference
  %% for things outside intent-spec: adoption inherits, influencer cites, secure baseline derives.

  EXTERNAL_REFERENCE {
    string title "free text; required"
    string url "optional"
    string party "who it comes from, e.g. AWS; optional"
    string version "edition or date; optional"
  }
  %% Every item has a document-unique id and a stage: proposed | ratified | deprecated; a deprecated item names its replacement (replacedBy) or, when nothing replaces it, gives a deprecationRationale.
  %% rule: a link not drawn to EXTERNAL_REFERENCE resolves to a local or imported item; an external reference there is a type error
  %% rule: where allowed, an external reference satisfies a link's cardinality; rules that inspect the target skip it
  %% rule: a ratified item does not link to a proposed item
  %% rule (should): a ratified item does not link to a deprecated item, except a review of a deprecated target
  %% rule: coverage rules apply only to items declared in this document; an imported or external system is treated as external

  %% Product
  %% Constraints and forces of progress are deliberately out of scope.

  PRODUCT
  PRODUCT }o--o{ JOB: targets
  %% rule: every ratified product targets at least one job
  %% rule: a job targeted by a ratified product has at least one ratified outcome

  JOB_EXECUTOR {
    string description "the role in the moment of doing the job; required"
  }
  %% rule (should): every job executor is motivated by at least one job

  JOB {
    string statement "required; solution-free, from the executor's perspective"
  }
  JOB }o--|| JOB_EXECUTOR: motivates
  JOB ||--o{ OUTCOME: has

  OUTCOME {
    string statement "required; solution-free and measurable"
    enum disposition "out-of-scope | overserved | deferred; optional"
    string rationale "required with a disposition"
  }
  OUTCOME }o--o{ PRODUCT: scopes
  %% a disposition applies to the products the outcome scopes, or to every product that targets its job when it scopes none
  %% rule: an outcome scopes products only when it has a disposition, and only products that target its job
  %% rule: for every ratified product that targets its job, every ratified outcome is served by at least one ratified requirement that applies to that product or has a disposition that applies to it, never both

  REQUIREMENT {
    string statement "required"
    string verification "how satisfaction is checked; required"
  }
  %% a requirement is a solution-side commitment the team builds; mandatory organisational requirements are STANDARDs
  REQUIREMENT }o--o{ OUTCOME: serves
  REQUIREMENT }o--o{ TREATMENT: executes
  REQUIREMENT }o--o{ ADOPTION: implements
  REQUIREMENT }o--o{ PRODUCT: scopes
  %% a requirement applies to the products it scopes, or to every product that targets the job of an outcome it serves when it scopes none
  %% rule: every requirement serves an outcome, executes a treatment, implements an adoption or is cited by a threat review

  %% Measurement (shared by product and governance)

  METRIC {
    string target "threshold; required"
    string frequency "required"
  }
  METRIC }o--o{ CONTROL: measures
  METRIC }o--o{ OUTCOME: measures
  %% rule: every metric measures at least one control or outcome

  %% Risk

  THREAT {
    enum category "spoofing | tampering | repudiation | information-disclosure | denial-of-service | elevation-of-privilege | other"
    enum appliesTo "external-entity | process | data-store | data-flow; zero or more; empty means not reviewed per DFD element"
  }
  THREAT }o--o{ CONTROL: threatens
  %% threatens is HCGF's sense: the threat can stop the control working as expected (not "the control mitigates the threat")
  %% rule (should): appliesTo is within the STRIDE-per-element set for the category, or the threat gives a rationale
  %% rule (should): every threat threatens at least one control

  THREAT_REVIEW {
    enum disposition "risk | covered | not-applicable"
    string rationale "required when not-applicable"
  }
  THREAT_REVIEW }o--|| THREAT: reviews
  THREAT_REVIEW }o--o| EXTERNAL_ENTITY: inspects
  THREAT_REVIEW }o--o| PROCESS: inspects
  THREAT_REVIEW }o--o| DATA_STORE: inspects
  THREAT_REVIEW }o--o| DATA_FLOW: inspects
  THREAT_REVIEW }o--o| RISK: raises
  THREAT_REVIEW }o--o{ CONTROL: cites
  THREAT_REVIEW }o--o{ REQUIREMENT: cites
  %% rule: a review inspects exactly one external entity, process, data store or data flow
  %% rule: every (threat, target) pair where the threat applies to the target's kind has exactly one review
  %% rule: a deprecated target keeps its reviews
  %% rule: raises exactly one risk when disposition is risk; otherwise none
  %% rule: cites at least one control or requirement when disposition is covered; otherwise none
  %% derived: a DFD's products are those realized by the system it depicts, or by the system containing the container it depicts
  %% derived: a review's products are the products of every DFD that includes, or shows, the element it inspects
  %% rule: a cited control is adopted in mode system, procedure or inherited by every product of the review
  %% derived: a threat poses every risk raised by a review of it

  RISK
  RISK }o--o{ OUTCOME: endangers
  %% rule: every risk has at least one treatment

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
  %% rule: a reduce treatment is executed by at least one control or requirement
  %% rule: a control executing a treatment is adopted in mode system, procedure or inherited by every product the treatment scopes
  %% rule: waives only when strategy is accept; a waiver applies only within the products the treatment scopes

  %% GRC (HCGF)

  INFLUENCER {
    enum kinds "statutory | regulatory | contractual | internal; one or more"
    string scopeRationale "why it applies; required"
  }
  INFLUENCER }o--o| EXTERNAL_REFERENCE: cites
  %% rule: a statutory, regulatory or contractual influencer cites exactly one source

  POLICY {
    string approver "executive leadership; required"
  }
  POLICY }o--o{ INFLUENCER: satisfies
  %% rule (should): every policy satisfies at least one influencer

  CONTROL_OBJECTIVE
  CONTROL_OBJECTIVE }o--|{ POLICY: supports
  CONTROL_OBJECTIVE }o--o{ INFLUENCER: cites

  STANDARD
  STANDARD }o--|{ CONTROL_OBJECTIVE: addresses

  GUIDELINE
  GUIDELINE }o--|{ STANDARD: augments

  ASSESSMENT_OBJECTIVE
  ASSESSMENT_OBJECTIVE }o--o{ STANDARD: verifies
  ASSESSMENT_OBJECTIVE }o--|| CONTROL: assesses
  ASSESSMENT_OBJECTIVE }o--o{ PROCEDURE: examines
  %% rule: an assessment objective verifies only standards its control enforces
  %% rule: an assessment objective examines only procedures that operationalize its control
  %% rule (should): every control is assessed by at least one assessment objective

  CONTROL {
    string owner "stakeholder; required"
    enum safeguard "technical | administrative | physical"
  }
  CONTROL }o--|{ STANDARD: enforces
  CONTROL }o--|{ CONTROL_OBJECTIVE: achieves
  CONTROL }o--o{ TREATMENT: executes
  %% derived: a control's influencers are those its control objectives cite, or that the policies they support satisfy

  PROCEDURE {
    string owner "process owner / asset custodian; required"
    string overseer "stakeholder oversight; required"
  }
  PROCEDURE }o--|| CONTROL: operationalizes
  PROCEDURE }o--o{ ADOPTION: implements
  %% rule: a procedure implementing an adoption operationalizes the adopted control

  PROFILE
  PROFILE ||--|{ SELECTION: has
  PRODUCT }o--o{ PROFILE: selects
  %% a profile is a company-level selection of controls (OSCAL profile); a product selects the profiles that apply to it

  SELECTION {
    enum choice "include | exclude"
    string rationale "required when exclude"
  }
  SELECTION }o--|| CONTROL: names
  %% rule: at most one selection per (profile, control) pair

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
  %% rule: at most one adoption per (product, control) pair
  %% rule: a product has an adoption for every control that a profile it selects includes (coverage)
  %% rule: a system adoption is implemented by at least one requirement, a procedure adoption by at least one procedure, other modes by neither
  %% rule: when mode is inherited, inherits exactly one target; otherwise none
  %% rule: an external reference that an adoption inherits has a party
  %% rule: an inherited adoption adopts the same control as the adoption it inherits
  %% rule: an inheritance chain ends at a system or procedure adoption or an external reference (no cycles)
  %% rule: not-applicable means the control's influencers do not apply to the product
  %% delegated means the control applies but whoever runs or deploys the product must implement it; it is not coverage
  %% rule: an excepted adoption's product is scoped by an accept treatment that waives every standard the adopted control enforces

  SECURE_BASELINE
  SECURE_BASELINE }o--|{ STANDARD: encodes
  SECURE_BASELINE }o--o| EXTERNAL_REFERENCE: derives
  SECURE_BASELINE }o--o{ DEPLOYMENT_NODE: hardens
  SECURE_BASELINE }o--o{ INFRASTRUCTURE_NODE: hardens
  %% derived: a secure baseline hardens every node nested in, or hosted by, a deployment node it hardens
  %% rule (should): a secure baseline derives from a CIS benchmark, DISA STIG or vendor guide

  %% derived: a product's system security plan (SSP) is its adoptions with their controls, standards, procedures, requirements and inheritance
  %% derived: a product's customer responsibility matrix is its delegated adoptions
  %% derived: a product's plan of action and milestones (POA&M) is the reduce treatments and accept waivers that scope it

  %% C4 (https://c4model.com/abstractions, https://c4model.com/diagrams)
  %% The landscape, context, container and component diagrams are fully derived. Dynamic and deployment diagrams store a scope; DFDs list their elements.
  %% The C4 code level is omitted: it is derived from source, not declared intent.
  %% rule (should): every person, system, container and component has a name and a short description
  %% rule (should): every container and component, and every stored relationship whose ends lie in different containers or systems, has a technology

  PERSON
  PERSON }o--o{ JOB_EXECUTOR: plays

  SYSTEM {
    string owner "team that builds and runs it; required"
    boolean external "not built and owned by the team that owns this document"
  }
  SYSTEM ||--o{ CONTAINER: contains
  SYSTEM }o--o{ PRODUCT: realizes
  %% rule: an internal system contains at least one container
  %% rule: an external system contains no containers
  %% rule: only an internal system realizes a product

  CONTAINER {
    enum kind "application | data-store"
    string technology
  }
  CONTAINER ||--o{ COMPONENT: contains
  %% rule (should): only an application container contains components

  COMPONENT {
    string technology
  }

  SYSTEM }o--o{ REQUIREMENT: satisfies
  CONTAINER }o--o{ REQUIREMENT: satisfies
  COMPONENT }o--o{ REQUIREMENT: satisfies
  %% rule: only an internal system satisfies a requirement
  %% rule: every ratified requirement is satisfied by at least one system, container or component

  RELATIONSHIP {
    string description "specific, consistent with direction; avoid bare 'uses'"
    string technology
  }
  RELATIONSHIP }o--o| PERSON: leaves
  RELATIONSHIP }o--o| SYSTEM: leaves
  RELATIONSHIP }o--o| CONTAINER: leaves
  RELATIONSHIP }o--o| COMPONENT: leaves
  RELATIONSHIP }o--o| PERSON: enters
  RELATIONSHIP }o--o| SYSTEM: enters
  RELATIONSHIP }o--o| CONTAINER: enters
  RELATIONSHIP }o--o| COMPONENT: enters
  RELATIONSHIP }o--o| INFRASTRUCTURE_NODE: leaves
  RELATIONSHIP }o--o| INFRASTRUCTURE_NODE: enters
  %% a relationship is unidirectional and points from the requester to the responder
  %% rule: a relationship leaves exactly one and enters exactly one person, system, container, component or infrastructure node
  %% rule: a relationship with an infrastructure-node end appears only in deployment diagrams
  %% rule: the two ends of a relationship are distinct and neither contains the other
  %% derived: a relationship implies one between each enclosing container or system of its source and of its destination, where neither contains the other, unless one is stored
  %% derived: an implied relationship's description and technology are those of the relationships that imply it; store one at the higher level to give it a curated label

  %% derived: the document has one system landscape: every system and person, and the relationships between them
  %% derived: each internal system has a system context diagram: the system plus every person and system joined to it
  %% derived: each internal system has a container diagram: its containers plus the people and systems joined to them
  %% derived: each application container with components has a component diagram: its components plus the containers, people and systems joined to them

  DYNAMIC_DIAGRAM
  DYNAMIC_DIAGRAM }o--|| REQUIREMENT: depicts
  DYNAMIC_DIAGRAM ||--|{ DYNAMIC_STEP: has

  DYNAMIC_STEP {
    int order "unique within the diagram"
    string description "optional; overrides the relationship's description"
  }
  DYNAMIC_STEP }o--|| RELATIONSHIP: follows
  %% rule: a step follows a relationship that joins people, systems, containers or components

  DEPLOYMENT_DIAGRAM
  DEPLOYMENT_DIAGRAM }o--|{ SYSTEM: depicts
  DEPLOYMENT_DIAGRAM }o--|| ENVIRONMENT: depicts
  %% derived: a deployment diagram shows the environment's nodes that host instances of its systems or their containers

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
  %% rule: a top-level node belongs to exactly one environment; a nested node belongs to none
  %% derived: a nested node's environment is its top-level ancestor's

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
  %% rule (should): every external entity, process, data store, data flow and trust boundary has a label

  EXTERNAL_ENTITY {
    string label
  }
  EXTERNAL_ENTITY }o--o| PERSON: represents
  EXTERNAL_ENTITY }o--o| SYSTEM: represents
  %% anything outside your control, including systems run by other teams
  %% rule: an external entity represents at most one person or system
  %% rule (should): an external entity does not represent the system a DFD including it depicts, or the system containing the container it depicts

  PROCESS {
    string label
  }
  PROCESS }o--o| SYSTEM: represents
  PROCESS }o--o| CONTAINER: represents
  PROCESS }o--o| COMPONENT: represents
  %% any running code under your control
  %% rule: a process represents at most one internal system, application container or component

  DATA_STORE {
    string label
  }
  DATA_STORE }o--o| CONTAINER: represents
  DATA_STORE }o--|{ DATA_ELEMENT: stores
  %% anywhere data is stored, including files, shared memory and cookies
  %% rule: a data store represents at most one container, and that container's kind is data-store

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
  %% rule: a data flow connects exactly two distinct ends, at least one of them a process
  %% rule: a data flow leaves at most one end, and that end is one it connects
  %% rule: each end of a data flow represents an end of every relationship the flow represents, or an element containing it
  %% rule: when a data flow leaves an end, every relationship it represents leaves the element that end represents, or one inside it
  %% rule (should): a data flow connecting an external entity and a process crosses at least one trust boundary
  %% derived: a data flow crosses a trust boundary when exactly one end is inside it

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
  %% rule: every trust boundary relies on at least one container, infrastructure node or control that enforces it
  %% rule: an element is enclosed directly by at most one boundary
  %% rule: boundary containment has no cycles
  %% derived: an element is inside a boundary when that boundary, or one it contains, encloses it

  DATA_FLOW_DIAGRAM {
    enum level "context | detail"
  }
  DATA_FLOW_DIAGRAM }o--o| SYSTEM: depicts
  DATA_FLOW_DIAGRAM }o--o| CONTAINER: depicts
  DATA_FLOW_DIAGRAM }o--o{ EXTERNAL_ENTITY: includes
  DATA_FLOW_DIAGRAM }o--o{ PROCESS: includes
  DATA_FLOW_DIAGRAM }o--o{ DATA_STORE: includes
  %% unlike C4 diagrams, a DFD lists its elements: DFD elements need not map onto C4
  %% a context-level DFD is optional
  %% rule: a DFD depicts exactly one system or container
  %% rule: a context-level DFD depicts a system and includes exactly one process, which represents that system
  %% rule (should): in a detail DFD, every process represents a container of the depicted system or a component of the depicted container, or connects a shown data flow to a process that does
  %% rule (should): every data store and external entity in a DFD connects at least one data flow the DFD shows
  %% derived: a DFD shows every data flow whose two ends it includes, and every trust boundary enclosing an included element
```
