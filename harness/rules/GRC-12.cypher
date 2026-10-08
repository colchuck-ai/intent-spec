// id: GRC-12
// severity: error
// hint: an inherited adoption inherits exactly one adoption or external reference; other modes inherit nothing
MATCH (a:Adoption {doc: $doc})
WITH a, COUNT { (a)-[:INHERITS]->() } AS n
WHERE (a.mode = 'inherited' AND n <> 1) OR (coalesce(a.mode, '') <> 'inherited' AND n > 0)
RETURN '/adoptions/' + a.id AS pointer,
       coalesce(a.mode, 'no-mode') + ' adoption inherits ' + n + ' targets' AS detail
