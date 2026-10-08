// id: REF-3
// severity: error
// hint: ratify the target too, or keep the linking item proposed
// Imported targets are skipped: their resolved stage lives in the lockfile snapshot, which is not loaded.
MATCH (d:Document {doc: $doc}), (s:Item {doc: $doc})-[r]->(t:Item {doc: $doc})
WHERE r.verb IS NOT NULL AND NOT t:ExternalReference
  AND coalesce(s.stage, d.stage) = 'ratified'   // DOC-2
  AND coalesce(t.stage, d.stage) = 'proposed'
MATCH (e:EntityType {name: s.type})
RETURN '/' + e.key + '/' + s.id AS pointer, r.verb + ' -> ' + t.id + ', which is proposed' AS detail
