// id: GRC-33
// severity: warning
// hint: satisfy the influencer with a policy, or cite it from a control objective
// GRC-27: an influencer applies to the products that answer it; a local influencer that no product
// answers applies to every product in the document (imported influencers are not items here)
MATCH (i:Influencer {doc: $doc})
WHERE (EXISTS { MATCH (:Product {doc: $doc})-[:ANSWERS]->(i) }
       OR (NOT EXISTS { MATCH (:Product)-[:ANSWERS]->(i) } AND EXISTS { MATCH (:Product {doc: $doc}) }))
  AND NOT EXISTS { MATCH (:Policy {doc: $doc})-[:SATISFIES]->(i) }
  AND NOT EXISTS { MATCH (:ControlObjective {doc: $doc})-[:CITES]->(i) }
RETURN '/influencers/' + i.id AS pointer, 'applies to a product but no policy satisfies it and no control objective cites it' AS detail
