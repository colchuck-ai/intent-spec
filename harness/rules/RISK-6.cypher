// id: RISK-6
// severity: error
// hint: a review with disposition risk raises exactly one risk; remove raises from any other review
MATCH (r:ThreatReview {doc: $doc})
WITH r, COUNT { MATCH (r)-[:RAISES]->() } AS n
WHERE (r.disposition = 'risk' AND n <> 1) OR (coalesce(r.disposition, '') <> 'risk' AND n > 0)
RETURN '/threatReviews/' + r.id AS pointer,
       'disposition ' + coalesce(r.disposition, '(none)') + ' raises ' + n + ' risks' AS detail
