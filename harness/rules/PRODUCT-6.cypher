// id: PRODUCT-6
// severity: error
// hint: link the requirement to an outcome (serves), treatment (executes) or adoption (implements), or cite it from a threat review
MATCH (r:Requirement {doc: $doc})
WHERE NOT EXISTS { (r)-[:SERVES|EXECUTES|IMPLEMENTS]->() }
  AND NOT EXISTS { (:ThreatReview {doc: $doc})-[:CITES]->(r) }
RETURN '/requirements/' + r.id AS pointer, 'serves, executes, implements nothing and no threat review cites it' AS detail
