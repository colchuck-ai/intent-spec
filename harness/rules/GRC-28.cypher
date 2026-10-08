// id: GRC-28
// severity: error
// hint: an influencer of the control applies to this product, so it cannot be not-applicable; adopt it in another mode, or stop the influencer applying
MATCH (a:Adoption {doc: $doc, mode: 'not-applicable'})-[:ADOPTS]->(c:Control)
MATCH (a)-[:GOVERNS]->(prod)
MATCH (c)-[:ACHIEVES]->(co:ControlObjective)
// GRC-6: a control's influencers are those its control objectives cite; a control objective that cites
// none contributes the influencers its policies satisfy. Imported objectives and policies are not followed.
CALL {
  WITH co
  MATCH (co)-[:CITES]->(i)
  RETURN i
UNION
  WITH co
  WITH co WHERE NOT EXISTS { MATCH (co)-[:CITES]->() }
  MATCH (co)-[:SUPPORTS]->(:Policy)-[:SATISFIES]->(i)
  RETURN i
}
WITH DISTINCT a, c, prod, i
// GRC-27: an influencer applies to the products that answer it; a local influencer no product answers
// applies to every product in the document, and an imported one to none.
WHERE EXISTS { MATCH (prod)-[:ANSWERS]->(i) }
   OR (i:Influencer AND prod:Product AND NOT EXISTS { MATCH (:Product)-[:ANSWERS]->(i) })
RETURN '/adoptions/' + a.id AS pointer,
       'influencer ' + coalesce(i.id, i.ref) + ' of ' + c.id + ' applies to ' + prod.id AS detail
