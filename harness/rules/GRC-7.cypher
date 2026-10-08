// id: GRC-7
// severity: error
// hint: follow only procedures that operationalize the adopted control, or fix the procedure's operationalizes link
MATCH (a:Adoption {doc: $doc})-[:FOLLOWS]->(p:Procedure)
MATCH (a)-[:ADOPTS]->(c)
WHERE NOT c:Unresolved                                  // REF-1 reports those
  AND NOT EXISTS { MATCH (p)-[:OPERATIONALIZES]->(c) }  // imported controls are one shared :Ref node, so this compares them too
RETURN '/adoptions/' + a.id AS pointer,
       'follows ' + p.id + ', which does not operationalize ' + coalesce(c.id, c.ref) AS detail
