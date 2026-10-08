// id: GRC-9
// severity: error
// hint: keep one adoption per control for a product; delete or merge the duplicates
MATCH (a:Adoption {doc: $doc})-[:GOVERNS]->(prod), (a)-[:ADOPTS]->(c)
WITH prod, c, a ORDER BY a.id
WITH prod, c, collect(a) AS ads
WHERE size(ads) > 1
UNWIND ads AS a
RETURN '/adoptions/' + a.id AS pointer,
       size(ads) + ' adoptions of ' + coalesce(c.id, c.ref) + ' govern ' + coalesce(prod.id, prod.ref) AS detail
