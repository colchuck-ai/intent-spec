// id: GRC-10
// severity: error
// hint: add an adoption (any mode) that governs the product and adopts the control, or exclude the control in a profile
// GRC-31: a profile includes a control when it, or a profile it imports, includes it, and it does not exclude it.
// Unrolled: some import path p0 -> ... -> pk where pk has an include selection for the control and no profile
// on the path has an exclude selection for it. Imported profiles' selections live in the lockfile, so only
// local profiles are followed.
MATCH (prod:Product {doc: $doc})-[:SELECTS]->(p0:Profile)
MATCH path = (p0)-[:IMPORTS*0..]->(pk:Profile)
MATCH (s:Selection {choice: 'include'})-[:IN]->(pk)
MATCH (s)-[:NAMES]->(c)
WHERE NOT c:Unresolved
  AND NONE(p IN nodes(path) WHERE EXISTS {
        MATCH (x:Selection {choice: 'exclude'})-[:IN]->(p) MATCH (x)-[:NAMES]->(c) })
  AND NOT EXISTS { MATCH (a:Adoption)-[:GOVERNS]->(prod) MATCH (a)-[:ADOPTS]->(c) }
WITH DISTINCT prod, c, p0
RETURN '/products/' + prod.id AS pointer,
       'no adoption of ' + coalesce(c.id, c.ref) + ', which selected profile ' + p0.id + ' includes' AS detail
