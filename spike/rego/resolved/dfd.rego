# DFD: data flow diagram rules (spike: DFD-8).
package intent.rules.dfd

import data.intent.graph as g
import data.intent.report.finding
import rego.v1

ends(relationship) := g.out(relationship, "leaves") | g.out(relationship, "enters")

# Containment (in) over every item, imported ones included.
containment := {x: g.out(x, "in") | some x, _ in g.items}

# e represents an end of the relationship, or an element containing one
# (component in container in system).
represents_end(e, relationship) if {
	some x in g.out(e, "represents")
	some z in ends(relationship)
	x in graph.reachable(containment, {z})
}

# METADATA
# title: DFD-8
# description: Each end of a data flow represents an end of every relationship the flow represents, or an element containing it.
# custom:
#   severity: error
#   hint: make each end of the flow represent an end of every relationship the flow represents (or the container or system enclosing it), or drop the relationship from represents
violation contains finding(rego.metadata.rule(), g.pointer(flow), detail) if {
	some flow in g.local_of("dataFlows")
	some relationship in g.out(flow, "represents")
	some e in g.out(flow, "connects")
	not represents_end(e, relationship)
	detail := sprintf("end %s represents no end of relationship %s or element containing one", [g.items[e].id, g.items[relationship].id])
}
