// id: RISK-7
// severity: error
// hint: a covered review cites at least one control or requirement; remove cites from any other review
MATCH (r:ThreatReview {doc: $doc})
WITH r, COUNT { MATCH (r)-[:CITES]->() } AS n
WHERE (r.disposition = 'covered' AND n = 0) OR (coalesce(r.disposition, '') <> 'covered' AND n > 0)
RETURN '/threatReviews/' + r.id AS pointer,
       'disposition ' + coalesce(r.disposition, '(none)') + ' cites ' + n + ' controls or requirements' AS detail
