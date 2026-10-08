// id: DOC-3
// severity: error
// hint: waive only a (should) rule by its ERD ID; fix an error-severity rule's finding instead of waiving it
MATCH (n:Item {doc: $doc}) WHERE n._waived IS NOT NULL
MATCH (e:EntityType {name: n.type})
UNWIND n._waived AS id
OPTIONAL MATCH (r:Rule {id: id})
WITH e, n, id, r WHERE r IS NULL OR r.severity <> 'warning'
RETURN '/' + e.key + '/' + n.id AS pointer,
       'ruleWaivers: ' + id + CASE WHEN r IS NULL THEN ' is not a rule ID' ELSE ' is an error-severity rule and cannot be waived' END AS detail
