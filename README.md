# intent-spec

A versioned contract for one document that describes a whole product: product intent, engineering architecture, governance, security and business process. It is the context an agent needs to take a product through its full lifecycle.

## Invariants

These hold for every version of the contract. Creating, changing or deleting an invariant needs a human decision, and so does any change that contradicts one. Cite them by ID.

- **INV-1. The document always wins.** It describes intent only. It holds no observed or runtime state, and correcting drift or compiling intent into a deployed product is out of scope.
- **INV-2. The deliverable is a versioned contract with two layers:** syntactic checks (JSON Schema) and semantic checks (rules). Rules are runnable, not prose: each has an ID, a selector, a predicate, a JSON pointer to the problem and a hint for fixing it. Every invalid example names the rule ID or schema path it breaks.
- **INV-3. Every item has a stable, document-unique ID.** Each entity type is one flat map keyed by ID, not a list, and containment is a link like any other, never nesting. An item's JSON pointer is always `/<type>/<id>`, so it stays stable when items move. Loaders must reject duplicate keys.
- **INV-4. Distribution follows a package-manager model.** A document declares aliased imports pinned to versions. A lockfile records each import's source, digest and a snapshot of the items referenced. Removing or renaming an ID is a breaking change, so deprecated items stay in place with a pointer to their replacement, or a rationale when nothing replaces them.
- **INV-5. Intent has lifecycle stages**, for example proposed, ratified and deprecated. Stages are intent, not observed state.
- **INV-6. Coverage applies to what a scope selects:** every selected item has exactly one disposition. Importing something never creates an obligation.
- **INV-7. References and imports work the same way in every layer.** A reference targets a local item, an imported item, or an external reference (free-text title, optional URL and party) for things that will never publish intent-spec, such as a provider's SOC 2 report or a law. Each link in the ERD declares whether it accepts an external reference (job cites, outcome cites, adoption inherits, influencer cites, secure baseline derives); every other link must resolve to a local or imported item. Where allowed, an external reference satisfies the link's cardinality, but rules that inspect the target skip it.
- **INV-8. The model has no abstract placeholder entities.** Links go to concrete entities. Each link is labelled with a single action verb and points from the dependent item to its anchor.
- **INV-9. Established models stay intact.** C4 follows c4model.com, DFDs follow DFD3, governance follows HCGF and product intent follows JTBD. Their core elements and relationships stay as the source model defines them. Removing, merging or replacing one, or making a stored link derived, needs a very strong reason and a human decision; simplicity (INV-10) alone is never enough. DFD elements stay separate from C4 elements and may optionally represent them.
- **INV-10. Keep it simple.** Every addition is justified by an example that needs it.

## Open

- How the contract specifies anything that is derived, not stored.
- The risk model: cause and consequence, treatments, scoring.
- Which way dependencies run between the product-intent repo and the repos that implement it.
- Business process layer.
