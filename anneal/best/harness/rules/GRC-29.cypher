// id: GRC-29
// severity: error
// hint: clauses quote the cited influencers' sources; cite the influencer, or remove the clauses
MATCH (o:ControlObjective {doc: $doc})
WHERE size(coalesce(o.clauses, [])) > 0
  AND NOT EXISTS { MATCH (o)-[:CITES]->() }
RETURN '/controlObjectives/' + o.id AS pointer, 'has clauses but cites no influencer' AS detail
