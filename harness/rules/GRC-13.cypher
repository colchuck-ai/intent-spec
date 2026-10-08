// id: GRC-13
// severity: error
// hint: give the inherited external reference a party (the upstream provider), e.g. party: AWS
MATCH (a:Adoption {doc: $doc})-[:INHERITS]->(x:ExternalReference)
WHERE trim(coalesce(x.party, '')) = ''
RETURN '/externalReferences/' + x.id AS pointer, 'inherited by ' + a.id + ' but has no party' AS detail
