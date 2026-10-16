# Risk: threat and threat review rules (spike: RISK-4).
package intent.rules.risk

import data.intent.lib.ref
import data.intent.report.finding
import rego.v1

# The item type each appliesTo kind names.
kinds := {
	"external-entity": "externalEntities",
	"process": "processes",
	"data-store": "dataStores",
	"data-flow": "dataFlows",
}

# METADATA
# title: RISK-4
# description: >-
#   Every (threat, target) pair where the threat applies to the target's kind is inspected
#   by exactly one review. (One review records one disposition for every target it
#   inspects: that holds by construction, as disposition is a single attribute.)
#   REF-5: covers threats and DFD elements declared in this document.
# custom:
#   severity: error
#   hint: add one threat review that inspects the target for this threat, or merge the reviews so the pair is inspected by exactly one
violation contains finding(rego.metadata.rule(), ref.pointer("threats", id), detail) if {
	some id, threat in input.document.threats
	some kind in object.get(threat, "appliesTo", [])
	key := kinds[kind]
	some target, _ in input.document[key]
	reviews := sort([rid |
		some rid, review in input.document.threatReviews
		review.reviews == id
		target in ref.refs(review, "inspects")
	])
	count(reviews) != 1
	detail := inspected(ref.pointer(key, target), reviews)
}

inspected(p, []) := sprintf("no review inspects %s", [p])

inspected(p, reviews) := sprintf("%s is inspected by %d reviews: %s", [p, count(reviews), concat(", ", reviews)]) if {
	count(reviews) > 1
}
