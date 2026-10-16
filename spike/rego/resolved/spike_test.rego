# Unit tests for what the conformance examples don't reach: GRC-31 on its own
# (exclude, import chains, cycles), and ruleWaivers on a warning.
package intent.spike_test

import data.intent.report
import data.intent.rules.grc
import rego.v1

doc := {
	"stage": "proposed",
	"imports": {"gov": {"source": "gov.yaml", "version": "^1"}},
	"products": {"p": {"selects": ["line"]}},
	"profiles": {"base": {}, "line": {"imports": ["base", "gov:corp"]}, "loop": {"imports": ["line"]}},
	"selections": {
		"s1": {"in": "base", "choice": "include", "names": "c1"},
		"s2": {"in": "base", "choice": "include", "names": "c2"},
		"s3": {"in": "line", "choice": "exclude", "names": "c2"},
		"s4": {"in": "loop", "choice": "include", "names": "c3"},
	},
	"controls": {"c1": {}, "c2": {}, "c3": {}},
}

gov := {
	"stage": "ratified",
	"profiles": {"corp": {}},
	"selections": {"g1": {"in": "corp", "choice": "include", "names": "c9"}},
	"controls": {"c9": {}},
}

test_grc31_import_chain_and_exclude if {
	# line imports base (c1, c2) and gov:corp (c9), and excludes c2
	grc.includes("d:line") == {"d:c1", "gov:c9"} with input as {"document": "d", "documents": {"d": doc, "gov": gov}, "aliases": {"d": {"gov": "gov"}}}
}

test_grc31_exclude_only_narrows_importers if {
	grc.includes("d:base") == {"d:c1", "d:c2"} with input as {"document": "d", "documents": {"d": doc, "gov": gov}, "aliases": {"d": {"gov": "gov"}}}
}

test_grc31_cycle_terminates if {
	# loop -> line -> base, and a cycle back from base to loop
	cyclic := json.patch(doc, [{"op": "add", "path": "/profiles/base/imports", "value": ["loop"]}])
	grc.includes("d:base") == {"d:c1", "d:c2", "d:c3", "gov:c9"} with input as {"document": "d", "documents": {"d": cyclic, "gov": gov}, "aliases": {"d": {"gov": "gov"}}}
}

test_grc10_reports_each_unadopted_control if {
	details := {f.detail | some f in report.findings; f.rule == "GRC-10"} with input as {"document": "d", "documents": {"d": doc, "gov": gov}, "aliases": {"d": {"gov": "gov"}}}
	details == {
		"no adoption of c1, which selected profile line includes",
		"no adoption of c9, which selected profile line includes",
	}
}

test_grc10_import_adoption_counts if {
	adopted := json.patch(doc, [{"op": "add", "path": "/adoptions", "value": {
		"a1": {"governs": "p", "adopts": "c1", "mode": "system"},
		"a2": {"governs": "p", "adopts": "gov:c9", "mode": "inherited"},
	}}])
	count({f | some f in report.findings; f.rule == "GRC-10"}) == 0 with input as {"document": "d", "documents": {"d": adopted, "gov": gov}, "aliases": {"d": {"gov": "gov"}}}
}

# A stand-in warning rule, to exercise waivers without porting one.
warning := {"title": "TEST-1", "custom": {"severity": "warning", "hint": "h"}}

error := {"title": "TEST-2", "custom": {"severity": "error", "hint": "h"}}

waiving := {"stage": "proposed", "controls": {"c1": {"ruleWaivers": {"TEST-1": "does not apply", "TEST-2": "nor this"}}}}

fake := {
	report.finding(warning, "/controls/c1", "w"),
	report.finding(error, "/controls/c1", "e"),
}

test_waiver_applies_to_warning_only if {
	result := report with input as {"document": "w", "documents": {"w": waiving}, "aliases": {}}
		with data.intent.rules as {"fake": {"violation": fake}}
		with data.intent.graph.violation as set()
	{[f.rule, f.rationale] | some f in result.waived} == {["TEST-1", "does not apply"]}
	{f.rule | some f in result.findings} == {"TEST-2"}
	result.errors == 1
}
