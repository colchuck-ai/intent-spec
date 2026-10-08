// id: RISK-12
// severity: error
// hint: add a treatment that treats this risk
MATCH (k:Risk {doc: $doc})
WHERE NOT EXISTS { MATCH (:Treatment)-[:TREATS]->(k) }
RETURN '/risks/' + k.id AS pointer, 'no treatment treats this risk' AS detail
