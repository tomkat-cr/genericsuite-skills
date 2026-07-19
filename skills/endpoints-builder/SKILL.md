---
name: endpoints-builder
description: Create or update GenericSuite API endpoint registrations in backend/endpoints.json. Use when the user wants to expose a CRUD entity (config_dbdef JSON) or a custom handler through the generic endpoint builder, or right after config-builder generates new entity configs. Performs idempotent JSON merges keyed on url_prefix — never duplicates, skips child entities stored inside the parent document.
argument-hint: [entity-name ...]
---

Add or update entries in the GenericSuite `backend/endpoints.json`
configuration file. A reference example of a complete endpoints file is
bundled at `references/endpoints.example.json`.

## Step 1 — Gather inputs

Ask the user (or infer from a preceding config-builder run):

1. **Endpoints file path**: default `config_dbdef/backend/endpoints.json`
   relative to the project root. If missing, confirm before creating it as
   an empty JSON array.
2. **Entities to register**: for each one, the entity config name
   (`json_file`, e.g. `invoices`) and — if available — the paths to its
   frontend/backend config_dbdef JSON files so the skill can derive
   everything else.
3. **Custom handlers** (optional): endpoints not backed by
   GenericEndpointHelper need `handler_type`, `view_func`, and methods
   provided explicitly by the user.

## Step 2 — Validation rules (apply BEFORE editing)

- **Skip `subType: "array"` children**: if the entity's frontend config has
  `"type": "child_listing"` with `"subType": "array"`, its data lives inside
  the parent document — it needs NO endpoint. Explain and skip.
- **Register `subType: "table"` children**: they live in their own table and
  DO need an endpoint.
- **No duplicate `url_prefix`**: if an entry with the same `url_prefix`
  already exists, skip it and report "already present"; only modify it when
  the user explicitly asks to update it.
- **Structure**: the file is a JSON array of objects with `name`,
  `url_prefix`, and `routes` (array of route objects).

## Step 3 — Apply the merge

Standard generic CRUD entry (one per entity):

```json
{
    "name": "<entity>",
    "url_prefix": "<entity>",
    "routes": [
        {
            "endpoint": "/",
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "handler_type": "GenericEndpointHelper",
            "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
            "params": {
                "json_file": "<entity>"
            }
        }
    ]
}
```

`<entity>` is the backend config filename without `.json` (snake_case), which
must equal the frontend config's `dbApiUrl`.

Custom-handler entry (only when the user supplies the handler):

```json
{
    "name": "<endpoint_name>",
    "url_prefix": "<endpoint_url>",
    "routes": [
        {
            "endpoint": "/",
            "methods": ["POST"],
            "handler_type": "flask",
            "view_func": "lib.models.<domain>.<module>.<function>",
            "params": {}
        }
    ]
}
```

Rules when editing:
- Preserve existing entries byte-for-byte; only append new objects at the
  end of the array.
- Keep 4-space indentation.

## Step 4 — Verify and summarize

1. Parse the result with `python3 -c "import json; json.load(open('<path>'))"`.
2. Cross-check each added `json_file` value: the backend config file
   `config_dbdef/backend/<json_file>.json` must exist — warn if it does not
   (the generic handler will fail at runtime without it).
3. Summarize: entries added, skipped duplicates, skipped array-children,
   missing backend configs warned about.
4. Remind: FastAPI-style custom routers registered in `lib/main.py` (see the
   `python-fastapi-code-builder` skill) do NOT go through endpoints.json —
   this file is for the generic endpoint builder.
