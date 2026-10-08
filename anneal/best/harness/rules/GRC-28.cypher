// id: GRC-28
// severity: error
// hint: an influencer of the control applies to this product, so it cannot be not-applicable; adopt it in another mode, or stop the influencer applying
// Imports are followed: an alias:id target resolves (RESOLVES_TO) to the item in a loaded document.
MATCH (a:Adoption {doc: $doc, mode: 'not-applicable'})-[:ADOPTS]->()-[:RESOLVES_TO*0..1]->(c:Control)
MATCH (a)-[:GOVERNS]->(prod)
MATCH (c)-[:ACHIEVES]->()-[:RESOLVES_TO*0..1]->(co:ControlObjective)
// GRC-6: a control's influencers are those its control objectives cite; a control objective that cites
// none contributes the influencers its policies satisfy.
CALL {
  WITH co
  MATCH (co)-[:CITES]->(ir)
  OPTIONAL MATCH (ir)-[:RESOLVES_TO]->(ii)
  RETURN coalesce(ii, ir) AS i
UNION
  WITH co
  WITH co WHERE NOT EXISTS { MATCH (co)-[:CITES]->() }
  MATCH (co)-[:SUPPORTS]->()-[:RESOLVES_TO*0..1]->(:Policy)-[:SATISFIES]->(ir)
  OPTIONAL MATCH (ir)-[:RESOLVES_TO]->(ii)
  RETURN coalesce(ii, ir) AS i
}
WITH DISTINCT a, c, prod, i
// GRC-27: an influencer applies to the products that answer it; a local influencer no product answers
// applies to every product in the document, and an imported one (from another document) to none.
WHERE EXISTS { MATCH (prod)-[:ANSWERS]->(y) WHERE y = i OR (y)-[:RESOLVES_TO]->(i) }
   OR (i:Influencer AND prod:Product AND i.doc = prod.doc AND NOT EXISTS { MATCH (:Product)-[:ANSWERS]->(i) })
RETURN '/adoptions/' + a.id AS pointer,
       'influencer ' + coalesce(i.id, i.ref) + ' of ' + c.id + ' applies to ' + prod.id AS detail
