// id: SCHEMA-LINK
// severity: error
// hint: the ERD requires this link (|| or |{ at the target), or allows only one target (|| or o|)
MATCH (e:EntityType)-[l:LINK]->()
WITH e, l.verb AS verb, max(toInteger(l.required)) = 1 AS required, max(toInteger(l.many)) = 1 AS many
MATCH (s:Item {doc: $doc, type: e.name})
WITH e, s, verb, required, many, COUNT { (s)-[r]->() WHERE r.verb = verb } AS n
WHERE (required AND n = 0) OR (NOT many AND n > 1)
RETURN '/' + e.key + '/' + s.id AS pointer,
       CASE WHEN n = 0 THEN 'missing required link ' + verb ELSE verb + ' allows one target, has ' + n END AS detail
