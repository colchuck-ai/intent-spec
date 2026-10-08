// id: GRC-10
// severity: error
// hint: add an adoption (any mode) that governs the product and adopts the control, or exclude the control in a profile
// GRC-31: a profile includes a control when it, or a profile it imports, includes it, and it does not exclude it.
// Unrolled: some import path p0 -> ... -> pk where pk has an include selection for the control and no profile
// on the path has an exclude selection for it. Imports are followed: a selected or imported profile, a named
// control or an adopted control given as alias:id resolves (RESOLVES_TO) to the item in a loaded document.
MATCH (prod:Product {doc: $doc})-[:SELECTS]->(p0r)
OPTIONAL MATCH (p0r)-[:RESOLVES_TO]->(p0i)
WITH prod, coalesce(p0i, p0r) AS p0
MATCH path = (p0:Profile)-[:IMPORTS|RESOLVES_TO*0..]->(pk:Profile)
MATCH (s:Selection {choice: 'include'})-[:IN]->(pk)
MATCH (s)-[:NAMES]->(cr)
OPTIONAL MATCH (cr)-[:RESOLVES_TO]->(ci)
WITH prod, p0, path, coalesce(ci, cr) AS c
WHERE NOT c:Unresolved
  AND NONE(p IN nodes(path) WHERE EXISTS {
        MATCH (x:Selection {choice: 'exclude'})-[:IN]->(p), (x)-[:NAMES]->(y) WHERE y = c OR (y)-[:RESOLVES_TO]->(c) })
  AND NOT EXISTS {
        MATCH (a:Adoption)-[:GOVERNS]->(prod), (a)-[:ADOPTS]->(y) WHERE y = c OR (y)-[:RESOLVES_TO]->(c) }
WITH DISTINCT prod, c, p0
RETURN '/products/' + prod.id AS pointer,
       'no adoption of ' + coalesce(c.id, c.ref) + ', which selected profile ' + p0.id + ' includes' AS detail
