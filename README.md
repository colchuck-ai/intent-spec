# intent-spec

A versioned contract for one document that describes a whole product: product intent, engineering architecture, governance, security and business process. It is the context an agent needs to take a product through its full lifecycle.

## Decisions

1. **The document always wins.** It describes intent only. It holds no observed state, and correcting drift or compiling intent into a deployed product is out of scope.
2. **The deliverable is a versioned contract.** It has two layers: syntactic checks (JSON Schema) and semantic checks (rules). Every invalid example names the rule ID or schema path it breaks.
3. **Semantic rules are runnable, not prose.** Each rule has an ID, a selector, a predicate, a JSON pointer to the problem and a hint for fixing it.
4. **Every item has a stable, document-unique ID.** Nesting only shows what contains what. It is never part of an address.
5. **Distribution follows a package-manager model.** A document declares aliased imports pinned to versions. A lockfile records each import's source, digest and a snapshot of the items referenced. Removing or renaming an ID is a breaking change, so deprecated items stay in place with a pointer to their replacement.
6. **Intent has lifecycle stages**, for example proposed, ratified and deprecated. Stages are intent, not observed state.
7. **Coverage is recorded explicitly.** If something must be considered, the document records that it was, with a disposition. For example, every (threat, target) pair gets a review.
8. **Any reference can point outside intent-spec.** A reference targets a local item, an imported item, or an external reference (free-text title, optional URL and party) for things that will never publish intent-spec, such as a provider's SOC 2 report or a law. An external reference satisfies a link's cardinality, but rules that inspect the target skip it.

## Open

- How the contract specifies anything that is derived, not stored.
- The risk model: cause and consequence, treatments, scoring.
- Which way dependencies run between the product-intent repo and the repos that implement it.
- Business process layer.
