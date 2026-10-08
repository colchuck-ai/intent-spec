// id: RISK-18
// severity: warning
// hint: a flow that crosses a trust boundary is exposed; record the review as covered or risk, or inspect that flow in a separate review
MATCH (r:ThreatReview {doc: $doc, disposition: 'not-applicable'})-[:INSPECTS]->(f:DataFlow)
// DFD-11: a data flow crosses a boundary when exactly one end is inside it
// DFD-15: an element is inside a boundary when that boundary, or one it contains, encloses it
MATCH (b:TrustBoundary {doc: $doc})
WHERE COUNT {
  MATCH (f)-[:CONNECTS]->(e)
  WHERE EXISTS { MATCH (b2:TrustBoundary)-[:IN*0..]->(b) WHERE (b2)-[:ENCLOSES]->(e) }
} = 1
RETURN DISTINCT '/threatReviews/' + r.id AS pointer,
       'not-applicable, but inspects ' + f.id + ', which crosses trust boundary ' + b.id AS detail
