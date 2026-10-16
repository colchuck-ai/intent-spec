# References: rules every link obeys, in every layer (spike: REF-3; REF-1 lives in the graph).
package intent.rules.ref

import data.intent.graph as g
import data.intent.report.finding
import rego.v1

# METADATA
# title: REF-3
# description: >-
#   A ratified item does not link to a proposed item [DOC-2]. Imported targets count, with
#   the stage of their own document; an external reference has no stage.
# custom:
#   severity: error
#   hint: ratify the target too, or keep the linking item proposed
violation contains finding(rego.metadata.rule(), g.pointer(s), detail) if {
	some s, item in g.items
	g.local(s)
	item.stage == "ratified"
	some l in item.links
	g.items[l.to].stage == "proposed"
	detail := sprintf("%s -> %s, which is proposed", [l.verb, l.ref])
}
