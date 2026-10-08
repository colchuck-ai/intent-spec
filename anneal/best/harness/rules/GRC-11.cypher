// id: GRC-11
// severity: error
// hint: a system adoption needs implementing requirements that apply to its product; a procedure adoption needs follows; other modes have neither
MATCH (a:Adoption {doc: $doc})
CALL {
  WITH a
  WITH a WHERE a.mode = 'system' AND NOT EXISTS { MATCH (:Requirement)-[:IMPLEMENTS]->(a) }
  RETURN 'system adoption is implemented by no requirement' AS detail
UNION
  WITH a
  MATCH (r:Requirement)-[:IMPLEMENTS]->(a)
  WHERE coalesce(a.mode, '') <> 'system'
  RETURN coalesce(a.mode, 'no-mode') + ' adoption is implemented by requirement ' + r.id AS detail
UNION
  WITH a
  // PRODUCT-8: a requirement applies to the products it scopes; when it scopes none it applies, among others,
  // to every product governed by an adoption it implements, so only a requirement with scopes can miss.
  MATCH (r:Requirement)-[:IMPLEMENTS]->(a), (a)-[:GOVERNS]->(prod)
  WHERE EXISTS { MATCH (r)-[:SCOPES]->() } AND NOT EXISTS { MATCH (r)-[:SCOPES]->(prod) }
  RETURN 'requirement ' + r.id + ' implements it but does not apply to ' + coalesce(prod.id, prod.ref) AS detail
UNION
  WITH a
  WITH a WHERE a.mode = 'procedure' AND NOT EXISTS { MATCH (a)-[:FOLLOWS]->() }
  RETURN 'procedure adoption follows no procedure' AS detail
UNION
  WITH a
  WITH a WHERE coalesce(a.mode, '') <> 'procedure' AND EXISTS { MATCH (a)-[:FOLLOWS]->() }
  RETURN coalesce(a.mode, 'no-mode') + ' adoption follows procedures' AS detail
}
RETURN '/adoptions/' + a.id AS pointer, detail
