// id: REF-1
// severity: error
// hint: point the link at an item declared in this document, or at alias:id for an alias in imports whose document declares that id
// A target is unresolved when it is a local id that names no item, an alias:id whose alias is not in imports,
// or an alias:id whose import's source document is loaded (LOADED_AS) but declares no item with that id.
MATCH (s:Item {doc: $doc})-[r]->(x:Ref {doc: $doc})
MATCH (e:EntityType {name: s.type})
OPTIONAL MATCH (:Document {doc: $doc})-[:HAS]->(i:Import {alias: split(x.ref, ':')[0]})
OPTIONAL MATCH (i)-[:LOADED_AS]->(src:Document)
WITH s, r, x, e, i, src
WHERE x:Unresolved
   OR i IS NULL
   OR (src IS NOT NULL AND NOT EXISTS { MATCH (x)-[:RESOLVES_TO]->() })
RETURN '/' + e.key + '/' + s.id AS pointer,
       r.verb + ' -> ' + x.ref + ' does not resolve' + CASE WHEN src IS NOT NULL THEN ' in ' + src.doc ELSE '' END AS detail
