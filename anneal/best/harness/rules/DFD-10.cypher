// id: DFD-10
// severity: warning
// hint: enclose the process in a trust boundary that the external entity is outside, or vice versa; a client-side process on the user's device belongs outside every boundary
MATCH (f:DataFlow {doc: $doc})-[:CONNECTS]->(ee:ExternalEntity), (f)-[:CONNECTS]->(p:Process)
// a process no boundary encloses shares the external entity's trust level (e.g. client-side code)
WHERE EXISTS { MATCH (:TrustBoundary {doc: $doc})-[:ENCLOSES]->(p) }
  // DFD-11: the flow crosses b when exactly one end is inside b;
  // DFD-15: an element is inside b when b, or a boundary b contains, encloses it
  AND NOT EXISTS {
    MATCH (b:TrustBoundary {doc: $doc})
    WHERE EXISTS { MATCH (b)<-[:IN*0..]-(:TrustBoundary)-[:ENCLOSES]->(ee) }
       <> EXISTS { MATCH (b)<-[:IN*0..]-(:TrustBoundary)-[:ENCLOSES]->(p) }
  }
RETURN '/dataFlows/' + f.id AS pointer,
       'flow between ' + ee.id + ' and ' + p.id + ' crosses no trust boundary' AS detail
