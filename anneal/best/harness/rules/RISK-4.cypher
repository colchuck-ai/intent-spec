// id: RISK-4
// severity: error
// hint: add one threat review that inspects the target for this threat, or merge the reviews so the pair is inspected by exactly one
// REF-5: coverage covers threats and DFD elements declared in this document.
// The second clause (one disposition per review for all its targets) holds by construction: disposition is a single attribute.
MATCH (t:Threat {doc: $doc})
UNWIND coalesce(t.appliesTo, []) AS kind
MATCH (e:Item {doc: $doc})
WHERE e.type IN ['EXTERNAL_ENTITY', 'PROCESS', 'DATA_STORE', 'DATA_FLOW']
  AND toLower(replace(e.type, '_', '-')) = kind
WITH DISTINCT t, e, COLLECT { MATCH (r:ThreatReview {doc: $doc})-[:REVIEWS]->(t) WHERE (r)-[:INSPECTS]->(e) RETURN r.id } AS reviews
WHERE size(reviews) <> 1
MATCH (k:EntityType {name: e.type})
RETURN '/threats/' + t.id AS pointer,
       CASE WHEN size(reviews) = 0 THEN 'no review inspects /' + k.key + '/' + e.id
            ELSE '/' + k.key + '/' + e.id + ' is inspected by ' + size(reviews) + ' reviews: ' + reduce(s = head(reviews), x IN tail(reviews) | s + ', ' + x) END AS detail
