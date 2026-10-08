// id: RISK-16
// severity: error
// hint: make the review inspect at least one target, and split it so each review inspects targets of one kind (external entities, processes, data stores or data flows)
MATCH (r:ThreatReview {doc: $doc})
// REF-2: imported targets count toward "at least one" but have no known kind
WITH r, COUNT { MATCH (r)-[:INSPECTS]->() } AS n,
     COLLECT { MATCH (r)-[:INSPECTS]->(x:Item) RETURN DISTINCT x.type } AS kinds
WHERE n = 0 OR size(kinds) > 1
RETURN '/threatReviews/' + r.id AS pointer,
       CASE WHEN n = 0 THEN 'inspects no target'
            ELSE 'inspects targets of several kinds: ' + reduce(s = head(kinds), k IN tail(kinds) | s + ', ' + k) END AS detail
