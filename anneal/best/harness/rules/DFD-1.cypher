// id: DFD-1
// severity: warning
// hint: give the DFD element a label
MATCH (n:Item {doc: $doc})
WHERE n.type IN ['EXTERNAL_ENTITY', 'PROCESS', 'DATA_STORE', 'DATA_FLOW', 'TRUST_BOUNDARY']
  AND (n.label IS NULL OR trim(toString(n.label)) = '')
MATCH (e:EntityType {name: n.type})
RETURN '/' + e.key + '/' + n.id AS pointer, 'has no label' AS detail
