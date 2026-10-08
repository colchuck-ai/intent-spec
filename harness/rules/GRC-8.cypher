// id: GRC-8
// severity: error
// hint: keep one selection per control in a profile; delete or merge the duplicates
MATCH (s:Selection {doc: $doc})-[:IN]->(p), (s)-[:NAMES]->(c)
WITH p, c, s ORDER BY s.id
WITH p, c, collect(s) AS sels
WHERE size(sels) > 1
UNWIND sels AS s
RETURN '/selections/' + s.id AS pointer,
       size(sels) + ' selections in ' + coalesce(p.id, p.ref) + ' name ' + coalesce(c.id, c.ref) AS detail
