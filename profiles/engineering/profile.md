# Engineering reviewer profile

This profile is for the agent or person in the **engineering reviewer** role. It gives a reviewer's lens grounded in two frameworks:

- **C4 model** (Simon Brown, https://c4model.com): the static structure of software systems at several levels of abstraction, plus supporting views.
- **DFD3** (Adam Shostack, https://github.com/adamshostack/DFD3): a precisely defined, versioned notation for data flow diagrams, used for threat modelling.

Use it to review any model, specification or set of diagrams that claims to describe software architecture in C4 terms, data flows in DFD3 terms, or both. It is not a tutorial. It says what to check, and which framework passage backs each check.

---

## 1. Role summary

The engineering reviewer asks whether the model or specification under review describes a software architecture **precisely, consistently and checkably**, at the right level of abstraction, so that a reader can:

1. tell which software systems exist, who owns each, and which one is in scope,
2. zoom from system → containers → components without the levels mixing,
3. see every relationship, its direction, its intent and its technology,
4. see how software is deployed in each environment,
5. get a DFD3-conformant data-flow view that is complete enough to threat-model.

Questions the reviewer keeps asking:

- **Abstraction:** Is every element's type explicit? Can an element end up at the wrong level, for example a message bus as a container or a JAR as a component?
- **Precision:** Are the properties the frameworks expect (name, description, technology, labels) present, and is each enforced at the framework's own strength (must vs should, §4.4)?
- **Relationships:** Are they unidirectional, labelled to match their direction, and carrying technology where expected?
- **Model vs view:** Is each diagram a view over one underlying model, with a declared scope, or a hand-drawn picture that can drift from the other diagrams?
- **Cross-framework consistency:** When a DFD element or flow corresponds to a C4 element or relationship, do kinds, endpoints and directions agree?
- **Completeness for threat modelling:** Could an omitted flow, store or boundary quietly shrink what gets threat-modelled?

---

## 2. C4 model glossary

All quotes come from c4model.com. All 23 pages listed in §8 loaded (fetched 2026-10-05).

### 2.1 What C4 is
- "A set of hierarchical abstractions - software systems, containers, components, and code", "a set of hierarchical diagrams - system context, containers, components, and code", "an additional set of supporting diagrams - system landscape, dynamic, and deployment", "Notation independent", "Tooling independent". (https://c4model.com/)
- An "'abstraction-first' approach to diagramming software architecture". "The small set of abstractions and diagram types makes the C4 model easy to learn and use." (https://c4model.com/abstractions)
- Purpose: "maps of your code', at various levels of detail" (https://c4model.com/introduction). It is "inspired by UML and the 4+1 model", built "to minimise the gap between the software architecture model/description and the source code" (https://c4model.com/faq).
- Scope limit: "The focus of the C4 model is the static structures that make up a software system". Business processes, workflows, state machines, domain and data models are out of scope; supplement with UML, BPML, ArchiMate or ER diagrams (https://c4model.com/faq).
- Process neutrality: C4 "implies nothing about the process of delivering software" (https://c4model.com/faq).
- Fit: designed for "custom-built, bespoke software systems". It is "less suited" to "embedded systems/firmware" and heavily customised platforms ("SAP and Salesforce"), though System Context and Container diagrams may still help. For libraries, frameworks and SDKs, "you might be better off using something like UML" (https://c4model.com/faq).
- History: roots around 2006–2009. Diagram types named in early 2010. "C4" first used in early 2011. The fourth level was renamed "classes" → "code" around 2015–2016, and switched in talks by March 2018 (https://c4model.com/history, https://c4model.com/faq).

### 2.2 Abstractions
The core sentence (https://c4model.com/abstractions):
> "A software system is made up of one or more containers (applications and data stores), each of which contains one or more components, which in turn are implemented by one or more code elements (classes, interfaces, objects, functions, etc). And people (actors, roles, personas, named individuals, etc) use the software systems that we build."

| Abstraction | Definition (C4's words) | Notes for the reviewer |
|---|---|---|
| **Person** | "people (actors, roles, personas, named individuals, etc) use the software systems that we build" (/abstractions) | C4 has no separate Person page. |
| **Software system** | "the highest level of abstraction and describes something that delivers value to its users, whether they are human or not." It includes the system being modelled "and the other software systems upon which your software system depends (or vice versa)". (/abstractions/software-system) | Boundary heuristic: "something a single software development team is building, owns, has responsibility for, and can see the internal implementation details of", often one repo, often "the boundary of a single team", maybe deployed together. Usually **not** systems: "product domains, bounded contexts, business capabilities, feature teams, tribes, or squads". C4 calls it "the hardest of the C4 model abstractions to define". |
| **Container** | "Not Docker! … a container represents an application or a data store. A container is something that needs to be running in order for the overall software system to work." "Essentially a runtime boundary around some code that is being executed or some data that is being stored." (/abstractions/container) | Examples: server-side web app, client-side web app, desktop app, mobile app, server-side console app/batch, **a single serverless function**, database **schema**, blob/content store or CDN, file system (or part of one), **a single shell script**. Deployment is "a separate concern". |
| **Component** | "a grouping of related functionality encapsulated behind a well-defined interface". "Components are not separately deployable units… it's the container that's the deployable unit… all components inside a container execute in the same process space." (/abstractions/component) | Packaging (JAR, DLL, module, namespace, folder) is "an orthogonal concern". Those are "typically not" components or containers, though a 1:1 mapping can happen. Shared helper/utility code used across components is called "inevitable". |
| **Code** | "components are made up of one or more code elements constructed with the basic building blocks of the programming language that you're using - classes, interfaces, enums, functions, objects, etc." (/abstractions/code) | Diagrams at this level are optional and best generated by tooling (§2.3). |

Key container FAQ positions (/abstractions/container):
- **Web app, one container or two?** A server-rendered app that produces mostly static HTML is one container. With "a significant quantity of JavaScript" (an SPA), it is "two containers", which makes it explicit "that these are two separate process spaces, communicating via an inter-process/remote communication mechanism (e.g. JSON/HTTPS)".
- **JAR/assembly/DLL/module?** "Typically not. A container is a runtime construct".
- **S3/RDS/CDN: system or container?** "Treat them as containers because they are an integral part of your software architecture, although they are hosted elsewhere". You "have ownership and responsibility for the buckets" and schemas.
- **Terminology:** "feel free to change the terminology if needed."

Microservices (/abstractions/microservices):
- Whether a microservice is modelled as "a group of one or more containers" (for example an API container plus a database-schema container) or "promoted" to a software system "depends upon the ownership of the individual services". It turns on whether they are "an implementation detail inside a single software system or … separate software systems that are (or could be) owned by separate teams" (Conway's Law stage).
- Container pairs can be shown as grouped: "you could draw a box around each pair".

Queues and topics (/abstractions/queues-and-topics):
- "Incorrect: Model the message bus as a C4 container." "Correct: Explicitly model queues and topics as C4 containers." "Correct: Implicitly model message-based interactions using a 'via' notation on relationships."
- "A message queue is essentially a data store". Modelling queues as containers also separates them from "their deployment topology".
- Pub/sub: arrows can be reversed to show publishers and subscribers. It is "just a different way of telling the same story."
- Ownership open question: if services A and B are separate software systems linked by queue X, "who owns the container? … Ownership will impact the diagrams."

Abstractions FAQ (/abstractions/faq):
- Terminology may change: "Just make sure that everybody explicitly understands it."
- Adding levels is "an advanced manoeuvre", only if "you're willing to put the effort into precisely defining those additional levels". The usual reasons people ask are misuse of the levels, or wanting to model "organisational constructs or groupings … subsystems, bounded contexts, layers, libraries".
- "The power of the C4 model is the small set of fixed/named hierarchical abstractions".

### 2.3 Diagrams
"You don't need to use all 4 levels of diagram; only those that add value - the system context and container diagrams are sufficient for most software development teams." (https://c4model.com/diagrams)

| Diagram | Scope | Primary elements | Supporting elements | Audience | Recommended? |
|---|---|---|---|---|---|
| System context (/diagrams/system-context) | "A single software system." | "The software system in scope." | "People … and software systems (external dependencies) that are directly connected to the software system in scope." Typically "you don't have responsibility or ownership of them." | Everybody | **Yes**, "for all software development teams" |
| Container (/diagrams/container) | "A single software system." | "Containers within the software system in scope." | "People and software systems directly connected to the containers." | Technical people, including ops/support | **Yes** |
| Component (/diagrams/component) | "A single container." | "Components within the container in scope." | "Containers (within the software system in scope) plus people and software systems directly connected to the components." | Architects, developers | **No**: only if it adds value; "consider automating their creation" |
| Code (/diagrams/code) | "A single component." | Code elements ("classes, interfaces, objects, functions, database tables, etc") | — | Architects, developers | **No**: IDEs generate it on demand |
| System landscape (/diagrams/system-landscape) | "An enterprise/organisation/department/etc." | "People and software systems related to the chosen scope." | — | Everybody | **Yes**, "particularly for larger organisations"; "really just a system context diagram without a specific focus on a particular software system" |
| Dynamic (/diagrams/dynamic) | "A particular feature, story, use case, etc." | "Your choice - you can show software systems, containers, or components interacting at runtime." | (same) | Everybody | **No**: "use sparingly". Based on the UML communication diagram, with "numbered interactions to indicate ordering". Collaboration and sequence styles "show the same information". |
| Deployment (/diagrams/deployment) | "One or more software systems within a single deployment environment (e.g. production, staging, development, etc)." | "Deployment nodes, software system instances, and container instances." | "Infrastructure nodes used in the deployment" | Technical people, including infra/ops | **Yes** |

Deployment definitions (/diagrams/deployment):
- "A **deployment node** represents where an instance of a software system/container is running". It can be physical, virtualised (IaaS, PaaS, VM), containerised (Docker) or an execution environment (DB server, app server). "Deployment nodes can be nested."
- **Infrastructure nodes**: "DNS services, load balancers, firewalls, etc."
- Cloud provider icons are fine, but "make sure any icons you use are included in your diagram key/legend".
- Container diagram note: deployment concerns such as "clustering, load balancers, replication, failover" belong in "one or more deployment diagrams, one per environment" (/diagrams/container).

### 2.4 Notation rules (https://c4model.com/diagrams/notation)
C4 is "notation independent". The test is "whether each diagram can stand alone, and be (mostly) understood without a narrative."
- **Diagrams:** a title "describing the diagram type and scope". A "key/legend explaining the notation". Acronyms "understandable by all audiences, or explained in the diagram key/legend".
- **Elements:** "The type of every element should be explicitly specified (e.g. Person, Software System, Container or Component)". "Every element should have a short description, to provide an 'at a glance' view of key responsibilities". "Every container and component should have a technology explicitly specified."
- **Relationships:** "Every line should represent a unidirectional relationship". "Every line should be labelled, the label being consistent with the direction and intent of the relationship … ideally avoiding single words like, 'Uses'". "Relationships between containers (typically these represent inter-process communication) should have a technology/protocol explicitly labelled."
- **Colours:** not dictated by C4. Keep them consistent, and mind "black and white printers, color blindness".
- **Key/legend:** all diagrams should have one, "This applies to diagrams created with notations such as UML, ArchiMate and SysML too".
- **Alternatives:** C4 can be drawn in UML or ArchiMate, or as non-box visualisations such as force-directed graphs and interactive zoomable diagrams.

### 2.5 Review checklist (https://c4model.com/diagrams/checklist), verbatim items
- *General:* title? diagram type understood? diagram scope understood? key/legend?
- *Elements:* every element has a name? type (level of abstraction) understood? what every element does understood? technology choices understood "where applicable"? acronyms? colours? shapes? icons? border styles? element sizes?
- *Relationships:* every arrow labelled with intent? "Does the description match the relationship direction?" technology choices "(e.g. protocols for inter-process communication)" where applicable? acronyms? colours? arrow heads? line styles?

### 2.6 Common problems (https://c4model.com/introduction)
Single diagram: notation unexplained or inconsistent; "purpose and meaning of elements is ambiguous"; relationships missing; relationships unlabelled; generic terms like "business logic"; unexplained acronyms; "Technology choices are missing"; "Levels of abstraction are mixed".
Across diagrams: inconsistent notation; "naming of elements is not consistent between diagrams"; unclear reading order; "no clear transition between one diagram and the next".

### 2.7 Diagram FAQ positions (https://c4model.com/diagrams/faq, https://c4model.com/faq)
- **Dependencies or data flow?** "This is your choice … make sure that the description of the line matches the direction of the arrow." "sends customer update events to" beats "customer update events".
- **Rate of change:** context changes slowest, then containers, then components (frequently); code becomes outdated "very quickly". Automated generation sources: service catalogs (landscape/context), logs/OpenTelemetry (containers), static analysis (components), and IaC or cloud configuration (deployment).
- **Scale:** split large diagrams into "a larger number of simpler diagrams", each telling "a different part of the same overall story, at the same level of abstraction", for example one per service with its "nearest afferent (inbound) and efferent (outbound) dependencies". This is "trivial with a modelling tool". Think of the "software architecture model as being a data structure that you can visualise in different ways".
- **arc42 mapping:** Context and Scope → System Context; Building Block View L1/L2/L3 → Container/Component/Code.

---

## 3. DFD3 glossary

Source: https://github.com/adamshostack/DFD3. The repo (branch `master`, latest commit `5f2e791 "Update README.md"`) contains only `README.md`, `LICENSE` and four icon PNGs (`rectangle.png`, `rounded-rectangle.png`, `cylinder-256.png`, `arrow.png`). There are no separate spec, stencil or example files. Everything below is from the DFD3 README.

### 3.1 Goal
DFD3 "defines a 'v3 DFD' precisely" and encourages treating diagramming techniques "like code", to be "specified and evolved over time, and labeled with a version." It is "'opinionated.' The design is aggressively simple to prioritize easy learning and use over expressiveness. It's just enough information to enable threat modeling and put type information into the picture."

### 3.2 Elements
| Element | Symbol | Definition (DFD3's words) |
|---|---|---|
| **External entity** | sharp-cornered rectangle | "Anything outside your control. Examples include people and systems run by other organizations or even divisions." It is **relative to perspective**: "If you're modeling Mint, then the bank's systems would be external entities." Definition §1.1: "a person or code outside your control". |
| **Process** | rounded rectangle | "Any running code which is under your control, including compiled, scripts, shell commands, SQL stored procedures, et cetera." |
| **Data store** | drum (cylinder) | "Anywhere data is stored, including files, databases, shared memory, S3, cookies, et cetera." |
| **Data flow** | arrow | "All the ways that processes can talk to data stores, external entities, or each other." Flows "are usually two way (bi-directional). A dot can be used to represent the origination side." The rationale section adds that initiation "can be shown with one arrowhead filled, the other open." |
| **Trust boundary** | dashed/dotted closed shape | "A closed shape drawn with a dashed or dotted line. Usually a box." |

### 3.3 Normative rules ("Must, must not, should, should not are used per IETF norms")
1. "A V3 DFD uses 5 symbols." (the five above)
2. "All lines are solid, except those used for trust boundaries, which are dashed or dotted. (There is no 'multi-process' symbol in DFD3.)"
3. "It **must not** depend on the use of color, but can use color for additional information."
4. "All elements **should** have a label."
5. "You **may** have a context diagram if the system is complex. One is not required."

### 3.4 Rationales
- Rounded rectangles over circles, because they are more space-efficient.
- Boxed boundaries, because they "clearly show what's inside, in a way that arcs often fail to do", and dashes and dots print clearly in black and white.
- Double-headed arrows, because they are "easier to draw", though they "don't show initiation of a connection, which is sad".
- No "complex processes" (concentric circles), because "when to use them was never made clear".
- Drums over Yourdon-style double lines, because drums are easier to draw in software tools.
- Lineage: Gane and Sarson (1979) used rounded rectangles. Yourdon and De Marco used sharp rectangles for external entities.

---

## 4. How C4 and DFD3 compose

### 4.1 Overlaps and differences
| Topic | C4 | DFD3 | Reviewer implication |
|---|---|---|---|
| Purpose | Static structure, communication | "Just enough information to enable threat modeling" | Best treated as two views of one model, with explicit correspondences between them. |
| Runtime code you own | Software system (yours), container (application), component | Process: "any running code which is under your control" | A process can correspond to a system, a container or a component. One DFD can mix C4 levels unless a level is chosen deliberately. |
| Stored data | Container (data store): DB **schema**, blob store, file system, **queue/topic** | Data store: "files, databases, shared memory, S3, cookies" | Every C4 data-store container should map to a DFD data store. Not every DFD data store (cookies, shared memory) is a C4 container. |
| Outside things | Person; external software system ("you don't have responsibility or ownership") | External entity: "anything outside your control", **relative to the modeller's perspective** | People and external systems map to external entities. "External" depends on the perspective, so it is not a fixed property of the thing. |
| Connections | Relationship: **unidirectional**, labelled by intent, technology between containers | Data flow: **usually bidirectional**, origination marked optionally, must touch a process | One DFD flow may correspond to a request/response pair of C4 relationships. The initiator corresponds to the source of the request relationship. |
| Boundaries | System boundary (ownership/team), container = runtime boundary, nested deployment nodes | Trust boundary: closed dashed shape | Trust boundaries are a separate concept. They often coincide with C4 or deployment boundaries but need not. |
| Colour | Free, but consistent and accessible | "Must not depend on the use of color" | Meaning must never be carried by colour alone. |
| Context diagram | System context is **recommended** | Context DFD is **optional** ("may") | The two frameworks weigh the context view differently. |
| Versioning of notation | Not versioned | Explicitly "v3", and argues notations should be versioned | A specification using DFD3 should state which DFD version it conforms to. |
| Code level | Optional, generated | n/a | Code-level detail adds nothing to DFD3 threat modelling. |

### 4.2 Correspondence rules a combined model should satisfy
These follow from the definitions above. They are a reviewer's synthesis, not text from either framework.
- An external entity corresponds to a C4 person or an external software system, or to nothing in C4.
- A process corresponds to code under your control: a software system you own, an application container or a component.
- A data store corresponds to a data-store container (including a queue or topic), or to nothing in C4 (cookies, shared memory).
- If a data flow corresponds to one or more C4 relationships, its two ends correspond to those relationships' endpoints (or to elements that contain them).
- Every data flow has at least one process end. A C4 relationship between two external systems, or between a person and an external system, therefore has no DFD flow inside your model.

### 4.3 Model vs views
C4 recommends thinking of "the software architecture model as being a data structure that you can visualise in different ways", and splitting large diagrams by focus (https://c4model.com/faq). Each C4 diagram type defines a scope, primary elements and supporting elements (§2.3). A rigorous specification can therefore define each diagram as a scope plus a derivation rule, rather than as a hand-maintained list of boxes. DFD3 says nothing about this, so a combined model has to choose how a DFD's contents are determined.

### 4.4 Strength of requirements
C4 notation and checklist items are phrased as "should" or as questions. DFD3 uses IETF MUST/SHOULD/MAY explicitly. A specification that turns either framework into validation rules should carry a severity (error vs warning) that preserves the original strength. Turning a "should" into a hard error, or silently dropping it, misstates the framework.

---

## 5. Review checklist

Each item names the framework concept behind it. "Model" means the model or specification under review.

### 5.1 C4 elements
- [ ] **E1** Every element has an explicit type: person, software system, container or component. *(Notation: "type of every element should be explicitly specified"; Checklist)*
- [ ] **E2** Every element has a name. *(Checklist: "Does every element have a name?")*
- [ ] **E3** Every element has a short description of its key responsibilities, not generic terms such as "business logic". *(Notation; Introduction)*
- [ ] **E4** Every container and every component has an explicit technology. *(Notation)*
- [ ] **E5** Every container belongs to exactly one software system, and every component to exactly one container. *(Abstractions)*
- [ ] **E6** A software system you own has at least one container. External systems are not decomposed, because "you don't have responsibility or ownership" of them. *(Abstractions; System context)*
- [ ] **E7** Each container is either an application or a data store. *(Container: "represents an application or a data store")*
- [ ] **E8** Managed data services you own buckets or schemas in (S3, RDS) are containers of your system, not external systems. *(Container FAQ)*
- [ ] **E9** Queues and topics are data-store containers. The message bus itself is not a container. A "via" on relationships is an accepted alternative. *(Queues and topics)*
- [ ] **E10** Components are not deployed on their own. Only containers and software systems have deployment instances. *(Component: "not separately deployable units")*
- [ ] **E11** Components belong to containers that run code. Components inside a data-store container need a justification. *(Component: "behind a well-defined interface", "same process space")*
- [ ] **E12** An SPA plus its server is two containers. JARs, DLLs, modules, packages, namespaces and folders are not containers or components. *(Container FAQ; Component FAQ)*
- [ ] **E13** Software systems are not product domains, bounded contexts, business capabilities or teams. *(Software system)*
- [ ] **E14** System boundaries follow ownership. Microservices are container groups when one team owns them, and separate systems when separate teams do. *(Software system; Microservices)*
- [ ] **E15** Any extra abstraction level is precisely defined and is not an organisational grouping. *(Abstractions FAQ)*
- [ ] **E16** Acronyms and abbreviations are explained. *(Notation; Checklist)*

### 5.2 Relationships
- [ ] **R1** Every relationship has exactly one source and one destination, so it is unidirectional. *(Notation)*
- [ ] **R2** Every relationship has a label stating its intent, specific rather than a bare "Uses". *(Notation; Checklist)*
- [ ] **R3** The label reads from source to destination ("sends X to"). *(Checklist: "Does the description match the relationship direction?"; Diagrams FAQ)*
- [ ] **R4** Relationships between containers carry a technology or protocol. Check other inter-process relationships too, for example container ↔ external system. *(Notation; Checklist "where applicable")*
- [ ] **R5** The model chooses dependency or data-flow semantics for relationships and applies the choice consistently. *(Diagrams FAQ)*
- [ ] **R6** No view mixes abstraction levels beyond what C4 lists as supporting elements for that diagram type. *(Introduction; §2.3 tables)*

### 5.3 Diagrams and views
- [ ] **D1** Every diagram has a type, a scope, and a title stating both. *(Notation; Checklist General)*
- [ ] **D2** Every diagram has a key or legend, including for icons, colours, shapes, line styles and arrowheads. *(Notation; Checklist)*
- [ ] **D3** Diagram contents match C4's primary and supporting elements for that type. Ideally they are derived from one model, not maintained by hand. *(§2.3; C4 FAQ "model as … data structure")*
- [ ] **D4** System context and container diagrams are scoped to one software system you own. Component diagrams are scoped to one container. *(Scope tables)*
- [ ] **D5** Element names are consistent across diagrams, and there is a clear zoom path from each diagram to the next. *(Introduction)*
- [ ] **D6** Dynamic diagrams are scoped to a feature, story or use case and have numbered interactions. The same relationship can appear at more than one step, and step labels can differ from the static relationship label. *(Dynamic)*
- [ ] **D7** Each deployment diagram covers exactly one environment, and every node and instance in it belongs to that environment. Environments are named consistently. *(Deployment; Container notes "one per environment")*
- [ ] **D8** Deployment nodes nest. System and container instances are hosted by nodes. Infrastructure nodes (DNS, load balancers, firewalls) are shown where relevant. Every instance's container belongs to a system in scope. *(Deployment)*
- [ ] **D9** Clustering, replication, failover and load balancers live in deployment views, not on containers. *(Container notes)*
- [ ] **D10** A system landscape scope (enterprise, organisation, department) is concrete enough to determine which systems and people belong to it. *(System landscape)*
- [ ] **D11** Recommended views are present: system context, container and deployment, plus system landscape for larger organisations. Component and code views appear only where they add value. *(Diagrams pages)*

### 5.4 DFD3
- [ ] **F1** Exactly five element types are used: external entity, process, data store, data flow, trust boundary. There is no multi-process or complex-process element. *(DFD3 Definition 1, 2; Rationale)*
- [ ] **F2** Every element, flow and trust boundary has a label. This is a "should". *(Definition 4)*
- [ ] **F3** Every data flow connects two elements, and at least one of them is a process. There are no entity↔entity, entity↔store or store↔store flows. *(Data flow definition)*
- [ ] **F4** Flows are treated as bidirectional unless origination is marked. Where origination is marked, it is one of the flow's two ends. *(Data flow; Rationale)*
- [ ] **F5** Trust boundaries are closed shapes. Which elements they enclose, and so which flows cross them, is unambiguous. *(Trust boundary)*
- [ ] **F6** Labelling an element external follows the "outside your control" test from the stated perspective. *(External entity, Mint/bank example)*
- [ ] **F7** Nothing depends on colour alone. *(Definition 3, "must not")*
- [ ] **F8** A context-level DFD is optional and is present only if the system is complex. *(Definition 5)*
- [ ] **F9** The model states which DFD version it follows. *(Goal: "labeled with a version")*

### 5.5 Cross-framework consistency
- [ ] **X1** The kind correspondences in §4.2 hold for every DFD element that corresponds to a C4 element.
- [ ] **X2** Flow endpoints agree with the endpoints of the relationships they correspond to, and the initiator agrees with the request direction.
- [ ] **X3** Completeness: every inter-process relationship that touches your processes has a DFD flow, and every data-store container has a DFD data store. Without this, threat modelling inherits gaps from omissions. *(DFD3: "just enough information to enable threat modeling")*
- [ ] **X4** Trust boundaries are reviewed against system, container and deployment boundaries. A mismatch is acceptable, but it should be intentional.

---

## 6. Red flags and anti-patterns

1. **Message bus as a container.** C4 says this is incorrect. Model queues and topics instead.
2. **Docker container ≡ C4 container.** C4: "Not Docker!"
3. **JARs, DLLs, packages, folders, namespaces or bounded contexts as components, containers or systems.** C4 calls these organisational, not runtime, constructs.
4. **Owned managed data services (S3 buckets, RDS schemas) modelled as external systems.**
5. **Product domains, business capabilities or teams modelled as software systems.**
6. **Bidirectional C4 relationships**, or one relationship standing for both directions.
7. **Unlabelled or "Uses"-labelled relationships**, or labels that read against the arrow.
8. **Missing technology** on containers, components or inter-container relationships.
9. **Hand-maintained diagrams that drift**, for example the same element named differently in two diagrams.
10. **Mixed abstraction levels** in one view, for example components on a container diagram, or a DFD mixing system-level and component-level processes without a stated reason.
11. **Deployment details on containers** (replicas, load balancers, failover) instead of per-environment deployment views.
12. **Multi-environment deployment diagrams**, or inconsistent environment names.
13. **Colour-only meaning**, or no key/legend.
14. **Complex or multi-process DFD elements**, or extra DFD symbol types.
15. **Flows that touch no process**, or flows with more than two ends.
16. **Framework "should"s enforced as hard errors, or silently ignored.**
17. **Code-level diagrams kept by hand** for long-lived documentation.
18. **Coverage gaps by omission**: a DFD that leaves out a flow or store, so it never gets threat-modelled.
19. **Perspective-blind "external"**: a system marked external in one model and internal in another, with no stated perspective.

---

## 7. Open questions in and between the frameworks

1. **What a software system is.** C4 itself calls it "the hardest of the C4 model abstractions to define". The ownership heuristic breaks down for shared platforms and for queues co-owned by several systems. C4 asks "who owns the container?" and gives no answer.
2. **Components in data stores.** C4 lists "database tables" as code elements in a code diagram but does not say whether a data-store container has components.
3. **Relationships involving infrastructure nodes and instances.** The deployment page text names infrastructure nodes but does not define the relationships between them and instances. The examples on that page are images only.
4. **Dynamic diagram steps.** C4 shows numbered interactions but does not say whether a step is the static relationship itself or a separate thing with its own label.
5. **Implied relationships across levels.** The pages read do not say whether a container-level relationship implies a system-level one.
6. **System landscape membership.** "Related to the chosen scope" gives no rule for deciding which systems and people belong.
7. **Trust-boundary nesting and overlap.** DFD3 defines only "a closed shape". It does not say whether boundaries may nest or overlap, or what crossing means when they do.
8. **Granularity of DFD processes.** DFD3 does not tie a process to any level of abstraction. C4 warns against mixing levels. A combined model must pick a level per DFD.
9. **Origination marker.** DFD3 gives two notations, "a dot" and "one arrowhead filled, the other open". They mean the same thing, and a specification should pick one.
10. **Data elements.** Neither framework defines what a flow carries or what a store holds. Threat modelling usually needs data classification, which comes from outside both.
11. **Context diagrams.** C4 recommends a system context diagram for every team. DFD3 makes a context DFD optional. The two can coexist, but whether one can be derived from the other is unspecified.
12. **Direction semantics.** C4 lets relationships mean dependency or data flow. DFD3 flows are always data movement. Mapping a dependency-style relationship such as "reads from" onto a flow inverts the visual direction.

---

## 8. Sources

All fetched 2026-10-05. Every page listed loaded successfully. Images on C4 pages (example diagrams, keys) were not readable as text, so no claims here rest on their content.

**C4 model** (Simon Brown)
- https://c4model.com/
- https://c4model.com/introduction
- https://c4model.com/history
- https://c4model.com/abstractions
- https://c4model.com/abstractions/software-system
- https://c4model.com/abstractions/container
- https://c4model.com/abstractions/component
- https://c4model.com/abstractions/code
- https://c4model.com/abstractions/microservices
- https://c4model.com/abstractions/queues-and-topics
- https://c4model.com/abstractions/faq
- https://c4model.com/diagrams
- https://c4model.com/diagrams/system-context
- https://c4model.com/diagrams/container
- https://c4model.com/diagrams/component
- https://c4model.com/diagrams/code
- https://c4model.com/diagrams/system-landscape
- https://c4model.com/diagrams/dynamic
- https://c4model.com/diagrams/deployment
- https://c4model.com/diagrams/notation
- https://c4model.com/diagrams/checklist
- https://c4model.com/diagrams/faq
- https://c4model.com/faq

**DFD3** (Adam Shostack)
- https://github.com/adamshostack/DFD3 (cloned at `master`, commit `5f2e791`). Contents: `README.md` (the whole specification), `LICENSE`, `icons/rectangle.png`, `icons/rounded-rectangle.png`, `icons/cylinder-256.png`, `icons/arrow.png`. The repo has no other spec, stencil or example files.
- Referenced from the DFD3 README but not fetched: Gane and Sarson, *Structured Systems Analysis* (1979), and Richard Botting's CS372 notes (web.archive.org link).
