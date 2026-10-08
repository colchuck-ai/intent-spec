// id: RISK-14
// severity: error
// hint: give each product the treatment applies to an adoption of this control in mode system, procedure or inherited, or narrow the treatment's scopes
MATCH (c:Control {doc: $doc})-[:EXECUTES]->(t:Treatment)
// RISK-17: a treatment applies to the products it scopes, or to every product in the document when it scopes none
WITH c, t, CASE WHEN EXISTS { MATCH (t)-[:SCOPES]->() }
                THEN COLLECT { MATCH (t)-[:SCOPES]->(p) RETURN p }
                ELSE COLLECT { MATCH (p:Product {doc: $doc}) RETURN p } END AS products
UNWIND products AS p
WITH c, t, p
WHERE NOT EXISTS {
  MATCH (a:Adoption)-[:ADOPTS]->(c)
  WHERE (a)-[:GOVERNS]->(p) AND a.mode IN ['system', 'procedure', 'inherited']
}
RETURN '/controls/' + c.id AS pointer,
       'executes ' + t.id + ' but is not adopted in mode system, procedure or inherited by ' + coalesce(p.id, p.ref) AS detail
