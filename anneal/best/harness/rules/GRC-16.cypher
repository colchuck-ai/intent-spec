// id: GRC-16
// severity: error
// hint: an excepted adoption invokes one accept treatment that applies to its product and waives every standard the control enforces; other modes invoke none
MATCH (a:Adoption {doc: $doc})
WITH a, COUNT { (a)-[:INVOKES]->() } AS n
CALL {
  WITH a, n
  WITH a, n WHERE (a.mode = 'excepted' AND n <> 1) OR (coalesce(a.mode, '') <> 'excepted' AND n > 0)
  RETURN coalesce(a.mode, 'no-mode') + ' adoption invokes ' + n + ' treatments' AS detail
UNION
  WITH a
  MATCH (a)-[:INVOKES]->(t:Treatment) WHERE a.mode = 'excepted' AND coalesce(t.strategy, '') <> 'accept'
  RETURN 'invokes ' + t.id + ', a ' + coalesce(t.strategy, 'no-strategy') + ' treatment' AS detail
UNION
  WITH a
  // RISK-17: a treatment applies to the products it scopes, or to every product in the document when it scopes none
  MATCH (a)-[:INVOKES]->(t:Treatment), (a)-[:GOVERNS]->(prod)
  WHERE a.mode = 'excepted'
    AND CASE WHEN EXISTS { MATCH (t)-[:SCOPES]->() }
             THEN NOT EXISTS { MATCH (t)-[:SCOPES]->(prod) }
             ELSE NOT prod:Product END
  RETURN 'invokes ' + t.id + ', which does not apply to ' + coalesce(prod.id, prod.ref) AS detail
UNION
  WITH a
  MATCH (a)-[:INVOKES]->(t:Treatment), (a)-[:ADOPTS]->(c:Control)-[:ENFORCES]->(s)
  WHERE a.mode = 'excepted' AND NOT s:Unresolved AND NOT EXISTS { MATCH (t)-[:WAIVES]->(s) }
  RETURN 'invokes ' + t.id + ', which does not waive ' + coalesce(s.id, s.ref) + ' that ' + c.id + ' enforces' AS detail
}
RETURN '/adoptions/' + a.id AS pointer, detail
