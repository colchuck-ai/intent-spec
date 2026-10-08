// id: GRC-14
// severity: error
// hint: inherit an adoption of the same control, or change what this adoption adopts
MATCH (a:Adoption {doc: $doc})-[:INHERITS]->(b:Adoption)
MATCH (a)-[:ADOPTS]->(c1), (b)-[:ADOPTS]->(c2)
WHERE c1 <> c2
RETURN '/adoptions/' + a.id AS pointer,
       'adopts ' + coalesce(c1.id, c1.ref) + ' but inherits ' + b.id + ', which adopts ' + coalesce(c2.id, c2.ref) AS detail
