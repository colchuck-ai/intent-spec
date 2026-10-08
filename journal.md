# Journal

Notable events and decisions in building intent-spec, kept as raw material for a future blog post about how it was made. Git and beads already record *what* changed. This file records *why it was interesting*: the bet, the surprises, the reversals and the numbers.

Add an entry when something would make a reader stop: a human decision on a gate, an invariant or process change, a reversal, a result that challenges the approach, or round-end numbers. Newest last. Each entry has a date and title, two to five sentences, and evidence (commit SHAs, bead IDs).

## Thesis: why one document, and why now

Product, engineering, security and GRC each hold part of a product's context, and each keeps it in its own tool: engineers document architecture in git, product managers keep jobs to be done in a product tool, GRC keeps policies in a GRC platform. The context was split because the people accountable for it have different skills, and each tool fits one group's skills. Agents level that out. When everyone works through an agent, a technical interface such as a versioned document in git stops being a barrier for product or GRC, so for the first time all four groups can work on the same model. intent-spec is a bet that this is the moment to merge them.

## 2026-09-30: one contract for a whole product

The goal was set as one versioned document describing a product's intent end to end, plus a contract (JSON Schema plus runnable semantic rules) that checks it. Instead of inventing a model, it stitches together established ones: Jobs to be Done for product intent, C4 for architecture, Shostack's DFD3 for threat modeling and ComplianceForge's HCGF for governance, with OSCAL-style profiles added later. Early invariants: the document always wins, it holds intent only and never runtime state, and references and imports work the same way in every layer.

## 2026-10-05: choosing a medium for the model

The model was first written as a Mermaid ERD, which forced decisions about notation itself. Abstract placeholder entities (ITEM, ELEMENT, REFERENCE) were removed in favour of explicit links between concrete entities. Every link became a single action verb pointing from the dependent item to its anchor ("procedure operationalizes control"). A first multi-role review ended with the instruction "err on the side of keeping it simple". Evidence: 57ac503, erd.md.

## 2026-10-06: a panel of experts and hand-written examples

Rather than review the ERD in the abstract, seven example documents were written by hand for real products at different stages: a concept product, Plausible (MVP and growth), Vaultwarden, Home Assistant, Mastodon and OpenEMR, the regulated one. Each ends with a "couldn't express" section. Thirteen reviewer personas then critiqued the model through those examples: product, JTBD, the job executor, architecture, DevOps, threat modeling, risk, governance, HCGF, compliance, an agent user, a schema designer and a simplicity advocate. The loop runs on beads molecules, and the orchestrating session keeps no state of its own, so the loop can stop and resume at any point. Evidence: afa4637, 2889d52, review/loop.md.

## 2026-10-07: round 1, 89 findings

Round 1 filed 89 findings (9 P1, 71 P2, 9 P3). 33 were fixed, 31 were duplicates, 14 were rejected and 11 were deferred. Human gates decided anything that touched an invariant. One telling rejection: a product-management reviewer wanted goals and hypotheses ("will people pay for privacy-first analytics?"). It was rejected because a bet is the team's strategy, not the product's intent, and measurable progress already fits outcomes and metrics. Evidence: review-mol-0os, review-mol-e1v.2.

## 2026-10-07: simplicity met domain fidelity, and INV-9 was born

A simplicity-driven fix removed GUIDELINE from the HCGF chain, and another proposed deriving HCGF links instead of storing them. The human reverted the first and rejected the second: "GUIDELINE is a core element of the HCGF model." That became an invariant: core elements and relationships of C4, DFD3, HCGF and JTBD stay as their source defines them, and simplicity alone is never reason enough to change them. The same rule later caught the removal of JTBD's "overserved" outcome, which was restored. Evidence: 1b0fed3, df28283, 718fbdf.

## 2026-10-07: flat beats nested, twice

The examples nested items (component inside container inside system), so moving a component changed its JSON pointer and every diff line above it. The model was flattened: every entity type is one map keyed by ID, and containment is an ordinary `in` link. Later the human asked whether hierarchical paths would give quicker context, since hierarchies rarely change. After weighing it (C4 components do move during refactors, and products target jobs rather than own them), the decision was to keep the model flat. Evidence: b68a67d, INV-3.

## 2026-10-07: fixers clobbering each other

Fixes applied one at a time still collided: two fixes changed the same entity, or one rewrote every example right before another. Triage now ends with a planning step that orders overlapping fixes using bead dependencies plus a comment explaining why. The plan exists only on the beads, so it disappears when they close. A gap turned up later: a deferred finding still blocked others, so deferring now removes those dependencies. Evidence: 97a88a6, 00e3952.

## 2026-10-07: round 2, and is this loop worth it?

Round 2 filed 59 findings (1 P1, 44 P2, 14 P3), and the model barely grew: entities 36 to 37, links 116 to 120, rules 103 to 112. Then the human asked whether the loop was making the product better or just generating material. The honest answer was mixed. Fixes created new findings, many P2s were "rule X misfires in case Y" that a validator would find mechanically, and thirteen domain experts kept pushing scope. The response: defer new scope (8 findings), report model size every round, and build an executable validator before round 3. Evidence: review-mol-e81, review-mol-829, review-8ii, e7c0644.

## 2026-10-08: it's a graph

Writing and reviewing the model as YAML felt clunky, because the model is really a graph. The next direction is to load example documents into a local Neo4j database. There both people and agents can see and query how a product's jobs, systems, threats and controls connect, and changes to the model can be tested against the loaded graph.

## 2026-10-08: the graph loader found what two review rounds missed

The first thing the Neo4j loader did, before Neo4j was even running, was compare every field in the examples against the ERD. It found 67 values that YAML had silently cut short. Flow-style lines like `{description: Lights, sensors and hubs reached over Zigbee, Z-Wave, owner: ...}` contain unquoted commas, so YAML read the description as just "Lights" and turned the rest into empty fields. Thirteen expert reviewers read these files across two rounds and none noticed, because people (and models) read the prose, not the parse. Evidence: the "quote comma-separated values" commit.

## 2026-10-08: YAML in git, graph in Neo4j

The question was whether the graph or the YAML should be the source of truth. The answer: load, change in the graph, export to save. A small Python harness reads the ERD itself, so the mapping follows the model with no extra code: items become nodes, link fields become relationships named after their verbs, and the ERD becomes a browsable meta-graph. Export writes changes back into the YAML in place, so comments and order survive. Loading and exporting all seven examples gives a byte-identical result, and an edit made in Neo4j shows up as an ordinary three-line git diff. The first rules are now Cypher queries (REF-1, REF-6, link cardinality, PRODUCT-1). Each was checked by planting a violation and watching it fire. Evidence: harness/.

## 2026-10-08: 86 rules in an afternoon, and two seconds to run them

Six agents ported the ERD's prose rules to Cypher in parallel, one section each. Each agent wrote only its own rule files and tested on a private copy of an example, so none of them overwrote another's work. Each rule had to catch a planted violation and stay silent on a clean copy before it counted. The result: 86 rule files plus generated checks for link cardinality, required attributes and enum values. Three rules (DOC-1, RISK-5 and the part of REF that describes behaviour) can't be checked from a single document, because they compare versions. The whole set runs against all seven examples in about two seconds. It found 4 errors and 26 warnings, filed as 15 beads. Most are cases the examples got wrong, but one pattern appears in three unrelated examples (a user's flow into an app in their own browser crosses no trust boundary), which suggests the rule is what's wrong. Evidence: harness/rules, b3ec92f and the commits just before it, label harness-finding.

## 2026-10-08: an executable checker changed a decision

In round 2 a reviewer asked for a way to record why a warning doesn't apply, and it was rejected because the model already says enough on paper. Once the rules ran, openemr raised a GRC-25 warning on every check: patient-chosen SMART apps receive health data with no BAA, which is correct, since those apps aren't business associates under HIPAA. A warning that is expected, can't be silenced and fires on every run teaches people to ignore warnings. The decision was reversed: an item may now waive a warning-severity rule with a rationale, and the checker reports it as waived instead of dropping it. Errors can't be waived. The same pass relaxed DFD-10, because a user and the app in their own browser share a trust level. That pattern showed up in three unrelated examples, which pointed at the rule rather than the examples. Evidence: review-qud, review-9q8.

## 2026-10-08: the orchestrator ran out of room

The loop was designed so the orchestrating session keeps no state, and it still filled 43% of its context in two days. The cause wasn't findings but supervision: every fixer reported back, and the orchestrator checked each result itself, more than a hundred times. The fix is one more level of delegation. A fix-runner subagent now works through the queue and reports a single line, and the orchestrator pauses at 25% context. The same change brought the Neo4j harness into the runbook: fixers prove each fix with `check`, reviewers use the graph as evidence, and a round can't close its fixes while the checker reports errors. Evidence: 29fd026.

## 2026-10-08: the model is the deliverable, not the file

Halfway into building lockfile tooling, the human stepped back: the goal is a data model (entities, relationships, rules) that is simple, complete, accurate, composable and agent-friendly across many kinds of companies. Whether it lives in YAML, SQL or a graph database is beside the point. The work had drifted into the contract's packaging: JSON Schema, pointers, a lockfile format. Three invariants about serialization (INV-2, INV-3, INV-4) were retired, the ERD's serialization notes moved to an appendix marked as a test fixture, and the lockfile agent was stopped before it wrote anything. The examples and the Neo4j harness are now framed as what they had become: a test bench for searching toward a global minimum, not the product. Evidence: 38358b1, 9149f95, review-8ii.

## 2026-10-08: the round trip was only byte-identical because nothing imported

Adding the first importing example (shiftly now adopts governance from a separate shiftly-governance document) showed that harness export silently deleted a document's imports. The "byte-identical round trip" had held only because no example used imports, so a guarantee checked on the examples was only as strong as the examples. The same change turned every rule into a regression test: 96 minimal invalid documents, each naming the one rule it breaks, all passing, with no rule found wrong. Evidence: ce869d8, 1605aac, 4f06a2a, review-8ii.

## 2026-10-08: the invariants, rewritten as principles

Asked what an invariant even is, the answer became: a line every version of the model keeps, which settles disputes ahead of time and marks what the loop may not change without a human. Measured against that, three of the old invariants were really design conventions (lifecycle stages, coverage, verb direction) and moved into the ERD. The human softened INV-9: established models are philosophical anchors to reality, not texts that must stay intact; any departure instead has to earn its place through review (INV-10). Three were added: the model does not depend on how it is stored (INV-11, guarding against the drift just reversed), each concept exists once across disciplines (INV-12, the unification itself), and items keep a stable identity (INV-13). Seven remain: 1, 7, 9, 10, 11, 12, 13.
