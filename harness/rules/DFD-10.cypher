// id: DFD-10
// severity: warning
// hint: enclose the process in a trust boundary that the external entity is outside, or vice versa
MATCH (f:DataFlow {doc: $doc})-[:CONNECTS]->(ee:ExternalEntity), (f)-[:CONNECTS]->(p:Process)
// DFD-11: the flow crosses b when exactly one end is inside b;
// DFD-15: an element is inside b when b, or a boundary b contains, encloses it
WHERE NOT EXISTS {
  MATCH (b:TrustBoundary {doc: $doc})
  WHERE EXISTS { MATCH (b)<-[:IN*0..]-(:TrustBoundary)-[:ENCLOSES]->(ee) }
     <> EXISTS { MATCH (b)<-[:IN*0..]-(:TrustBoundary)-[:ENCLOSES]->(p) }
}
RETURN '/dataFlows/' + f.id AS pointer,
       'flow between ' + ee.id + ' and ' + p.id + ' crosses no trust boundary' AS detail
