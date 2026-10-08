// id: GRC-26
// severity: warning
// hint: name who is accountable for the control in this product with owner
MATCH (a:Adoption {doc: $doc})
WHERE a.mode IN ['system', 'procedure'] AND trim(coalesce(a.owner, '')) = ''
RETURN '/adoptions/' + a.id AS pointer, a.mode + ' adoption has no owner' AS detail
