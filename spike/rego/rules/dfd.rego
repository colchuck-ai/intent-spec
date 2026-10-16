# DFD: data flow diagram rules (spike: DFD-8).
package intent.rules.dfd

import data.intent.lib.ref
import data.intent.report.finding
import rego.v1

local(id) := ref.index[""][id]

ends(relationship) := array.concat(ref.refs(relationship, "leaves"), ref.refs(relationship, "enters"))

# Containment (in) as a graph over the checked document's items.
containment[id] := {t | some t in ref.refs(e.item, "in")} if some id, e in ref.index[""]

# e represents an end of the relationship, or an element containing one
# (component in container in system).
represents_end(e, relationship) if {
	some x in ref.refs(e, "represents")
	some z in ends(relationship)
	x in graph.reachable(containment, {z})
}

# METADATA
# title: DFD-8
# description: Each end of a data flow represents an end of every relationship the flow represents, or an element containing it.
# custom:
#   severity: error
#   hint: make each end of the flow represent an end of every relationship the flow represents (or the container or system enclosing it), or drop the relationship from represents
violation contains finding(rego.metadata.rule(), ref.pointer("dataFlows", id), detail) if {
	some id, flow in input.document.dataFlows
	some rid in ref.refs(flow, "represents")
	relationship := input.document.relationships[rid]
	some eid in ref.refs(flow, "connects")
	e := local(eid).item

	# REF-2/REF-5: skip ends and relationship ends that are imported or unresolved
	every x in ref.refs(e, "represents") { local(x) }
	every z in ends(relationship) { local(z) }

	not represents_end(e, relationship)
	detail := sprintf("end %s represents no end of relationship %s or element containing one", [eid, rid])
}
