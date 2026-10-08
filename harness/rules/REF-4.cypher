// id: REF-4
// severity: warning
// hint: link to the deprecated item's replacement, or deprecate this item too
// Imported targets are skipped: their resolved stage lives in the lockfile snapshot, which is not loaded.
MATCH (d:Document {doc: $doc}), (s:Item {doc: $doc})-[r]->(t:Item {doc: $doc})
WHERE r.verb IS NOT NULL AND NOT t:ExternalReference
  AND coalesce(s.stage, d.stage) = 'ratified'   // DOC-2
  AND coalesce(t.stage, d.stage) = 'deprecated'
  AND NOT (s:ThreatReview AND r.verb = 'inspects')   // a review of a deprecated target is kept (RISK-5)
MATCH (e:EntityType {name: s.type})
RETURN '/' + e.key + '/' + s.id AS pointer, r.verb + ' -> ' + t.id + ', which is deprecated' AS detail
