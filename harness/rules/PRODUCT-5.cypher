// id: PRODUCT-5
// severity: error
// hint: serve the outcome with a ratified requirement that applies to the product, or give it a disposition that applies to it, not both (unless overserved)
MATCH (d:Document {doc: $doc})
MATCH (p:Product {doc: $doc})-[:TARGETS]->(j)<-[:IN]-(o:Outcome {doc: $doc})
WHERE coalesce(p.stage, d.stage) = 'ratified' AND coalesce(o.stage, d.stage) = 'ratified'   // DOC-2
// PRODUCT-7: a disposition applies to the products the outcome scopes, or to every product targeting its job when it scopes none
WITH d, p, o,
     o.disposition IS NOT NULL
       AND (NOT EXISTS { (o)-[:SCOPES]->() } OR EXISTS { (o)-[:SCOPES]->(p) }) AS disposed
// PRODUCT-8: a requirement applies to the products it scopes; when it scopes none it applies to every product
// targeting the job of an outcome it serves, which includes p because it serves o and p targets o's job
WITH p, o, disposed, COUNT {
  MATCH (r:Requirement {doc: $doc})-[:SERVES]->(o)
  WHERE coalesce(r.stage, d.stage) = 'ratified'
    AND (EXISTS { (r)-[:SCOPES]->(p) } OR NOT EXISTS { (r)-[:SCOPES]->() })
} AS served
WHERE (served = 0 AND NOT disposed)
   OR (served > 0 AND disposed AND o.disposition <> 'overserved')
RETURN '/outcomes/' + o.id AS pointer,
       CASE WHEN served = 0
            THEN 'for product ' + p.id + ': no ratified requirement serves it and no disposition applies'
            ELSE 'for product ' + p.id + ': served by a requirement yet disposition ' + o.disposition + ' applies' END AS detail
