# GRC: governance, risk and compliance rules (spike: GRC-31, GRC-10).
package intent.rules.grc

import data.intent.lib.ref
import data.intent.report.finding
import rego.v1

# Every profile in the checked document and its imports, by ref.key.
profiles[ref.key(p)] := p if {
	some scope in ref.scopes
	some id, item in ref.doc(scope).profiles
	p := {"scope": scope, "id": id, "key": "profiles", "item": item}
}

# The controls a profile's own selections include or exclude (choice), by ref.key.
# A selection and the control it names are read in the selection's document.
selected(k, choice) := {ref.key(c) |
	some scope in ref.scopes
	some s in ref.doc(scope).selections
	s.choice == choice
	ref.key(ref.resolve(scope, s["in"])) == k
	c := ref.resolve(scope, s.names)
}

excluders(c) := {k | some k, _ in profiles; c in selected(k, "exclude")}

# A profile's imports that do not exclude control c, read in the profile's document.
imports_keeping(c) := {k: {q |
	some r in ref.refs(p.item, "imports")
	q := ref.key(ref.resolve(p.scope, r))
	not q in excluders(c)
} |
	some k, p in profiles
}

# derived GRC-31: a profile includes a control when it, or a profile it imports, includes it,
# and it does not exclude it. Rego has no recursive rules, so the closure is reachability:
# from profile k, follow imports only through profiles that do not exclude c, and look
# for a profile that includes c. graph.reachable terminates on cycles (GRC-32).
includes(k) := {c |
	some p, _ in profiles
	some c in selected(p, "include")
	not k in excluders(c)
	some q in graph.reachable(imports_keeping(c), {k})
	c in selected(q, "include")
}

# Controls a product adopts, by ref.key, from adoptions that govern it.
adopted[a.governs] contains ref.key(ref.resolve("", a.adopts)) if some a in input.document.adoptions

# METADATA
# title: GRC-10
# description: A product has an adoption for every control that a profile it selects includes [GRC-31] (coverage).
# custom:
#   severity: error
#   hint: add an adoption (any mode) that governs the product and adopts the control, or exclude the control in a profile
violation contains finding(rego.metadata.rule(), ref.pointer("products", id), detail) if {
	some id, product in input.document.products
	some r in ref.refs(product, "selects")
	p := ref.resolve("", r)
	p.key == "profiles"
	some c in includes(ref.key(p))
	not c in object.get(adopted, id, set())
	detail := sprintf("no adoption of %s, which selected profile %s includes", [split(c, "|")[1], p.id])
}
