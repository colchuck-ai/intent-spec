// id: GRC-34
// severity: warning
// hint: have a policy this control objective supports satisfy the influencer, or drop the citation
MATCH (o:ControlObjective {doc: $doc})-[:CITES]->(i)
WHERE NOT EXISTS { MATCH (o)-[:SUPPORTS]->(p:Policy)-[:SATISFIES]->(i) }
  AND NOT EXISTS { MATCH (o)-[:SUPPORTS]->(:Imported) }   // an imported policy's links are not visible here [REF-2]
RETURN '/controlObjectives/' + o.id AS pointer,
       'cites ' + coalesce(i.id, i.ref) + ', which no supported policy satisfies' AS detail
