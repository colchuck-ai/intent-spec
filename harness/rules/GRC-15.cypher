// id: GRC-15
// severity: error
// hint: make the inheritance chain end at a system or procedure adoption or an external reference, and break any cycle
// Imported targets (:Ref:Imported) end the visible chain and are skipped (REF-2).
MATCH (a:Adoption {doc: $doc})
WHERE EXISTS { MATCH (a)-[:INHERITS]->() }
CALL {
  WITH a
  MATCH (a)-[:INHERITS*1..]->(b) WHERE EXISTS { MATCH (b)-[:INHERITS*1..]->(b) }
  RETURN 'inheritance chain has a cycle' AS detail
UNION
  WITH a
  MATCH (a)-[:INHERITS*1..]->(e:Adoption)
  WHERE NOT EXISTS { MATCH (e)-[:INHERITS]->() } AND NOT coalesce(e.mode, '') IN ['system', 'procedure']
  RETURN 'inheritance chain ends at ' + e.id + ', a ' + coalesce(e.mode, 'no-mode') + ' adoption' AS detail
}
RETURN DISTINCT '/adoptions/' + a.id AS pointer, detail
