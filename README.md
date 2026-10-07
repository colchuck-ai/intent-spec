# intent-spec

A versioned contract for one document that describes a whole product: product intent, engineering architecture, governance, security and business process. It is the context an agent needs to take a product through its full lifecycle.

## Invariants

These hold for every version of the contract. Creating, changing or deleting an invariant needs a human decision, and so does any change that contradicts one. Cite them by ID.

- **INV-1. The document always wins.** It describes intent only. It holds no observed or runtime state, and correcting drift or compiling intent into a deployed product is out of scope.
- **INV-2. The deliverable is a versioned contract with two layers:** syntactic checks (JSON Schema) and semantic checks (rules). Rules are runnable, not prose: each has an ID, a selector, a predicate, a JSON pointer to the problem and a hint for fixing it. Every invalid example names the rule ID or schema path it breaks.
- **INV-3. Every item has a stable, document-unique ID.** Nesting only shows what contains what. It is never part of an address. Items are maps keyed by ID, not lists, so JSON pointers stay stable when items move. Loaders must reject duplicate keys.
- **INV-4. Distribution follows a package-manager model.** A document declares aliased imports pinned to versions. A lockfile records each import's source, digest and a snapshot of the items referenced. Removing or renaming an ID is a breaking change, so deprecated items stay in place with a pointer to their replacement.
- **INV-5. Intent has lifecycle stages**, for example proposed, ratified and deprecated. Stages are intent, not observed state.
- **INV-6. Coverage applies to what a scope selects:** every selected item has exactly one disposition. Importing something never creates an obligation.
- **INV-7. References and imports work the same way in every layer.** A reference targets a local item, an imported item, or an external reference (free-text title, optional URL and party) for things that will never publish intent-spec, such as a provider's SOC 2 report or a law. An external reference satisfies a link's cardinality, but rules that inspect the target skip it.
- **INV-8. The model has no abstract placeholder entities.** Links go to concrete entities. Each link is labelled with a single action verb and points from the dependent item to its anchor.
- **INV-9. C4 follows c4model.com and DFDs follow DFD3.** DFD elements stay separate from C4 elements and may optionally represent them.
- **INV-10. Keep it simple.** Every addition is justified by an example that needs it.

## Open

- How the contract specifies anything that is derived, not stored.
- The risk model: cause and consequence, treatments, scoring.
- Which way dependencies run between the product-intent repo and the repos that implement it.
- Business process layer.
