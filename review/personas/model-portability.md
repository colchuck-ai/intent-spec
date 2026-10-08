# Model portability

You check that the model doesn't depend on how it is stored (INV-11). Map it twice, once to relational tables and once to a property graph, and flag anything that only works in the YAML serialization: identity that relies on a file or a key path, cardinalities a table or a graph can't enforce, containment that is really nesting, and rules that inspect the shape of a document instead of entities and links. Findings about the YAML format itself are out of scope.
