# Examples

These documents describe six products, five real open-source ones and one made up, each at one stage of its life. Plausible appears twice. They are the evals for the model. Each ends with a "Couldn't express" comment listing what the author wanted to say and the model didn't allow.

The documents were written by one neutral author from public information. They are simplified and illustrative, not authoritative, and not endorsed by the projects. Numbers, owners and targets are invented where the projects don't publish them.

| File | Product | Stage |
|---|---|---|
| `shiftly.yaml` | Made-up volunteer shift scheduler | concept |
| `plausible-mvp.yaml` | Plausible Analytics, around 2019 | MVP |
| `plausible-growth.yaml` | Plausible Analytics, around 2022 | growth |
| `vaultwarden.yaml` | Vaultwarden | growth |
| `home-assistant.yaml` | Home Assistant | mature |
| `mastodon.yaml` | Mastodon | mature |
| `openemr.yaml` | OpenEMR | mature, regulated |

## Shape

There is no schema yet. These documents follow `erd.md` using the provisional conventions below, which are themselves under review.

- The header holds the `DOCUMENT` fields: `intentSpec`, `id`, `version` and `stage`. Imports, when present, go in `imports`, a map from alias to `{source, version}`.
- Other top-level keys are entity types, written in camelCase and plural (`jobs`, `controls`, `dataFlows`). Each one is a map keyed by item ID.
- IDs are kebab-case and unique across the whole document.
- Nothing nests. Containment in the ERD (`contains`, `has`, `hosts`) is a to-one `in` field on the contained item, holding its container's ID: an outcome has `in: <job>`, a container `in: <system>`, a dynamic step `in: <dynamic diagram>`. An item's JSON pointer is always `/<type>/<id>`.
- Every other link is a field on the item it starts from, named after the ERD verb (`serves`, `enforces`, `inspects`). A to-one link holds one ID and a to-many link holds a list. ERD lines with the same source and verb are one field: a link that can target several entity types (such as `leaves`) still holds a plain ID, or a list when to-many (such as `inspects`), and rule REF-6 checks each target's type.
- An item has a `stage` field only where its stage differs from the document's `stage`. External references have no stage. A deprecated item names its replacement in `replacedBy`, or says why nothing replaces it in `deprecationRationale`.
- Any item may have `name` and `description`, as the ERD's item conventions state. Dates such as `reviewBy` are `YYYY-MM-DD` strings; the YAML 1.2 JSON or core schema keeps them unquoted strings.
- A reference is a local ID, an `alias:id` from `imports`, or the ID of an item in `externalReferences`.
