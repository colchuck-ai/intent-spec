# Examples

These documents describe six products, five real open-source ones and one made up, each at one stage of its life. Plausible appears twice, and Shiftly's company governance is a document of its own that the product imports. They are the evals for the model. Each ends with a "Couldn't express" comment listing what the author wanted to say and the model didn't allow.

The documents were written by one neutral author from public information. They are simplified and illustrative, not authoritative, and not endorsed by the projects. Numbers, owners and targets are invented where the projects don't publish them.

| File | Product | Stage |
|---|---|---|
| `shiftly.yaml` | Made-up volunteer shift scheduler | concept |
| `shiftly-governance.yaml` | Shiftly's company governance (policy, control objective, standard, control, profile), imported by `shiftly.yaml` | ratified |
| `plausible-mvp.yaml` | Plausible Analytics, around 2019 | MVP |
| `plausible-growth.yaml` | Plausible Analytics, around 2022 | growth |
| `vaultwarden.yaml` | Vaultwarden | growth |
| `home-assistant.yaml` | Home Assistant | mature |
| `mastodon.yaml` | Mastodon | mature |
| `openemr.yaml` | OpenEMR | mature, regulated |

## Shape

There is no schema yet. These documents follow the reference serialization appendix of `erd.md`, which fixes the top-level keys, the ID pattern, the reference syntax and when a field holds one value or a list. In short:

- The header holds the `DOCUMENT` fields: `intentSpec`, `id`, `version` and `stage`. Imports, when present, go in `imports`, a map from alias to `{source, version}`.
- Every other top-level key is an entity type in camelCase plural (`jobs`, `people`, `dataFlows`), mapping item IDs to items. Nothing nests: containment is the `in` link on the contained item, and an item's JSON pointer is `/<type>/<id>`.
- IDs are kebab-case and unique across the whole document. A reference is a local ID, an `alias:id` from `imports`, or the ID of an item in `externalReferences`.
- Links are fields named after the ERD verb, holding one reference when to-one and a list when to-many.
