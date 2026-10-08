// id: RISK-2
// severity: warning
// hint: link the threat to the controls it threatens, or cite a control or requirement in one of its reviews
MATCH (t:Threat {doc: $doc})
WHERE NOT EXISTS { MATCH (t)-[:THREATENS]->() }
  AND NOT EXISTS { MATCH (r:ThreatReview {doc: $doc})-[:REVIEWS]->(t) WHERE EXISTS { MATCH (r)-[:CITES]->() } }
RETURN '/threats/' + t.id AS pointer, 'threatens no control and no review of it cites a control or requirement' AS detail
