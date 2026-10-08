# intent-spec

A unified data model for describing a product across product management, engineering, security, and governance, risk and compliance. It defines the entities, the relationships between them, and the rules those entities and relationships must obey. It starts from established models instead of inventing new ones: Jobs to be Done for product intent, C4 for architecture, DFD3 and STRIDE for threat modeling, and HCGF for governance.

**Status:** a public scratchpad. The model is being worked out in the open, and parts of it are wrong. That's the point: being ambitious and finding out where it's wrong beats thinking small and never learning anything.

## Goal

The model should be:

- **Simple:** the fewest entities, links and rules that can still express real products.
- **Complete:** able to express what many kinds of companies, in different domains and at different stages, need to say about their products.
- **Accurate:** faithful to the established models it builds on. They anchor questions of principle (INV-9), and we depart from one only when the evidence shows that unification is worth the cost of leaving a standard people already know (INV-10).
- **Composable:** governance is defined once and adopted by many products, and one product's intent can be implemented across many repos.
- **Agent-friendly:** easy for agents to read, query and edit, with stable IDs and rules that say what's wrong and how to fix it.

The model is the deliverable. How it is stored, whether as YAML files, SQL tables or a graph database, is not.

## How we get there

We treat the design as a search for the best model, not the first one that works. A model that fits the few products checked so far can sit in a local minimum: every finding against it looks fixed, but only because nothing has pushed on it from a new direction. New companies and new reviewers supply that push, so every change has to hold up against many products from many points of view.

![A cost curve with a shallow local minimum and a deeper global minimum. New companies and new reviewers move the model out of the shallow dip.](docs/minima.svg)

The process works like simulated annealing. Each round disturbs the model with new examples and rotated reviewers, then lets it settle through fixes.

```mermaid
flowchart LR
  sim["Simulate companies<br/>example products"] --> load["Load into the harness<br/>graph + runnable rules"]
  load --> review["Review panel<br/>personas × examples"]
  review --> triage{"Triage<br/>each finding"}
  triage -- "reject, defer, duplicate<br/>(reason recorded)" --> log[("Beads")]
  triage -- "accept" --> fix["Fix one at a time<br/>verified by the harness"]
  triage -- "touches an invariant" --> human{{"Human decision"}}
  human --> fix
  fix --> done{"Converged?<br/>no new P1s,<br/>fewer P2s"}
  done -- "no: rotate reviewers,<br/>add companies" --> sim
  done -- "yes" --> stable(["Stable model"])
```

1. **Simulate companies.** Example products span domains and lifecycle stages: a concept, an MVP, growth-stage and mature products, and a regulated one ([review/examples](review/examples)).
2. **Load them into a test harness.** A Neo4j database holds each example as a graph, and every rule runs as a query against it. Each rule also has an invalid example that breaks it, as a regression test ([harness](harness)). The harness and the YAML examples are test fixtures, not a product.
3. **Review from many perspectives.** A panel of reviewer personas, including product, end user, architecture, threat modeling, GRC, an agent user and a simplicity advocate, reports where the model can't express something, forces the wrong shape, or carries more than it needs ([review/personas](review/personas)).
4. **Fix and repeat.** Findings are triaged, fixed and re-checked ([review/loop.md](review/loop.md)). A human decides anything that touches an invariant. We stop when a round finds no new P1s and fewer P2s than the round before.

## Repository

- [erd.md](erd.md): the model, which holds its entities, links and rules.
- [review](review): example companies, reviewer personas and the review loop.
- [harness](harness): the Neo4j test harness and the rules written as Cypher.
- [journal.md](journal.md): how the model was built, and why it changed.

## Invariants

These hold for every version of the model. Creating, changing or deleting an invariant needs a human decision, and so does any change that contradicts one. Cite them by ID. IDs are never reused, so a removed invariant leaves a gap.

- **INV-1. Intent only.** The model describes what a product is meant to be, never what is observed at runtime. Detecting drift between intent and reality, and compiling intent into a running product, are out of scope.
- **INV-7. One way to refer to anything.** An item can point to an item in its own document, to an item in a document it imports, or to an external reference: something that will never be described in intent-spec, such as a law or a provider's SOC 2 report. References work the same way in every layer, which is what lets governance be defined once and adopted by many products. Importing something never creates an obligation; only an explicit adoption does.
- **INV-9. Established models are the anchors.** JTBD, C4, DFD3 and HCGF are the source the unified model draws from. When a design question turns on principle, the answer starts from what the source model says and why.
- **INV-10. Every change earns its place.** Every addition is justified by an example that needs it. Adding, removing or changing an established model's elements or relationships, including making a stored link derived, goes through review and a human decision. It is accepted only when the benefit of unification outweighs the cost of leaving a model people already know. Simplicity alone is never reason enough.
- **INV-11. The model does not depend on how it is stored.** Entities, links and rules are defined without reference to any file format or database. Any storage that keeps them, whether YAML, SQL or a graph, is a valid form of the model, and none is the model.
- **INV-12. Each concept exists once.** Product, engineering, security and GRC share one model, and their items link to each other directly. When two disciplines mean the same thing, they use the same entity. When they mean different things, the model names the difference.
- **INV-13. Every item has a stable identity.** An item's ID is unique and keeps its meaning across versions. Items are deprecated, pointing to a replacement, rather than deleted or renamed.

## Open

- How the model specifies anything that is derived, not stored.
- The risk model: cause and consequence, treatments, scoring (for example CVSS).
- Which way dependencies run between the product-intent repo and the repos that implement it.
- Business process layer.
