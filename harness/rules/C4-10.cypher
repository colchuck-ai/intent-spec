// id: C4-10
// severity: error
// hint: a relationship with an infrastructure node end belongs only in deployment diagrams; remove the dynamic step that follows it
// Derived diagrams (landscape, context, container, component) never show infrastructure nodes, so only dynamic steps can break this.
MATCH (r:Relationship {doc: $doc})-[:LEAVES|ENTERS]->(:InfrastructureNode)
MATCH (st:DynamicStep {doc: $doc})-[:FOLLOWS]->(r)
RETURN DISTINCT '/relationships/' + r.id AS pointer,
       'relationship with an infrastructure node end is followed by dynamic step ' + st.id AS detail
