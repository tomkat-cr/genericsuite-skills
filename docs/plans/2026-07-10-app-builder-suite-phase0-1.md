# GenericSuite App-Builder Skill Suite — Phase 0 + 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the foundations (map-driven reference sync) and the Phase-1 skills (`menu-builder`, `endpoints-builder`, `python-fastapi-code-builder`) of the app-builder suite, per the design doc at `docs/design/2026-07-09-app-builder-skill-suite-design.md`.

**Architecture:** Claude Skills are instruction documents (`skills/<name>/SKILL.md`) plus bundled `references/` exemplars and `evals/evals.json` test definitions. Reference exemplars are copies of canonical files from the `genericsuite-basecamp` repo, kept fresh by a map-driven sync script (a generalization of the existing `update-gs-docs` skill). No application code is written here — the deliverables are skill documents, reference maps, eval definitions, and playground fixtures.

**Tech Stack:** Markdown SKILL.md files, Bash (POSIX-ish, per `docs/codeStyle.md` of basecamp), Python 3 stdlib (json validation), skill-creator eval framework.

**Working directory for ALL tasks:** `/Users/carlosramirez/desarrollo/genericsuite/packages/genericsuite-skills` (this is its own git repo — commit here, not in the superproject).

## Global Constraints

- Shell scripts: `#!/bin/bash`, `set -euo pipefail`, quote all expansions `"${var}"`, no `read -p` (use `echo` + `read VAR < /dev/tty`), handle macOS vs Linux (`perl -pi -e` over `sed -i`).
- Commit message style: `Add:`/`Change:`/`Fix:` prefix + ticket `[GS-254]`, matching repo history.
- Every new skill: `SKILL.md` frontmatter with `name`, `description` (~100 words max, drives triggering), `argument-hint`; registered in `.claude-plugin/marketplace.json`; listed in `CLAUDE.md` skills table; `evals/evals.json` with ≥2 test cases.
- Skill-generated test outputs go under `playground/` (repo convention).
- Backend result shape is non-negotiable: `{"error": bool, "error_message": str|None, "resultset": Any}`.
- Eval expectations must include at least one runtime-validity assertion, not only file/structure checks (lesson recorded in the design doc, 2026-07-10).
- `select_elements` valid forms: constant-name string, or inline array of `{title, value}` objects; bare-string arrays are invalid.

---

### Task 1: Map-driven reference sync (Phase 0)

Generalize `skills/update-gs-docs` from a hardcoded curl list into a map-driven sync that prefers a local basecamp checkout and falls back to GitHub raw URLs.

**Files:**
- Create: `skills/update-gs-docs/reference_map.txt`
- Rewrite: `skills/update-gs-docs/scripts/update-gs-docs.sh`
- Modify: `skills/update-gs-docs/SKILL.md`
- Modify: `Makefile` (add `sync-references` target)

**Interfaces:**
- Consumes: nothing (first task).
- Produces: `bash skills/update-gs-docs/scripts/update-gs-docs.sh [branch]` honoring `BASECAMP_DIR` env var; `reference_map.txt` line format `source-path-in-basecamp|dest-path-in-this-repo` (later tasks append lines to it); `make sync-references`.

- [ ] **Step 1: Write `skills/update-gs-docs/reference_map.txt`**

Covers the five files the old script synced, plus destinations that Tasks 2–4 will consume (their basecamp sources already exist, so syncing them now is safe and lets later tasks be pure consumers):

```
# reference_map.txt — map of basecamp files to local skill reference copies
# Format: <path relative to genericsuite-basecamp repo root>|<path relative to this repo root>
# Lines starting with # and blank lines are ignored.

# config-builder (legacy gs_docs layout, kept for path stability)
mkdocs_root/en/Configuration-Guide/index.md|skills/config-builder/gs_docs/en/Configuration-Guide/index.md
mkdocs_root/en/Configuration-Guide/Generic-CRUD-Editor-Configuration.md|skills/config-builder/gs_docs/en/Configuration-Guide/Generic-CRUD-Editor-Configuration.md
mkdocs_root/code/configuration-guide/crud_editor_config_classes.py|skills/config-builder/gs_docs/code/configuration-guide/crud_editor_config_classes.py
mkdocs_root/code/fastapitemplate/README.md|skills/config-builder/gs_docs/code/fastapitemplate/README.md
scripts/new-project-from-template.sh|skills/config-builder/scripts/new-project-from-template.sh

# menu-builder
mkdocs_root/code/exampleapp/apps/config_dbdef/backend/app_main_menu.json|skills/menu-builder/references/app_main_menu.example.json

# endpoints-builder
mkdocs_root/code/exampleapp/apps/config_dbdef/backend/endpoints.json|skills/endpoints-builder/references/endpoints.example.json

# python-fastapi-code-builder
mkdocs_root/code/exampleapp/apps/api-fastapi/lib/routers/fda_food_endpoint.py|skills/python-fastapi-code-builder/references/routers/fda_food_endpoint.py
mkdocs_root/code/exampleapp/apps/api-fastapi/lib/routers/food_moments.py|skills/python-fastapi-code-builder/references/routers/food_moments.py
mkdocs_root/code/exampleapp/apps/api-fastapi/lib/models/external_apis/fda_food_endpoint.py|skills/python-fastapi-code-builder/references/models/fda_food_endpoint_model.py
mkdocs_root/code/exampleapp/apps/api-fastapi/lib/models/admin_food/food_moments.py|skills/python-fastapi-code-builder/references/models/food_moments_model.py
mkdocs_root/code/exampleapp/apps/api-fastapi/lib/main.py|skills/python-fastapi-code-builder/references/main.py
mkdocs_root/code/configuration-guide/crud_editor_config_classes.py|skills/python-fastapi-code-builder/references/crud_editor_config_classes.py
```

- [ ] **Step 2: Rewrite `skills/update-gs-docs/scripts/update-gs-docs.sh`**

```bash
#!/bin/bash
# skills/update-gs-docs/scripts/update-gs-docs.sh
# Map-driven sync of reference files from genericsuite-basecamp into the
# skills' references/ (and legacy gs_docs/) directories.
#
# Usage:
#   bash skills/update-gs-docs/scripts/update-gs-docs.sh [branch]
#   BASECAMP_DIR=/path/to/genericsuite-basecamp bash skills/update-gs-docs/scripts/update-gs-docs.sh
#
# Modes:
#   - If BASECAMP_DIR is set (or ../genericsuite-basecamp exists), copy files
#     from the local checkout (fast, works offline).
#   - Otherwise download each file from GitHub raw on the given branch
#     (default: develop).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
REPO_ROOT="$(dirname "$(dirname "$(dirname "${SCRIPT_DIR}")")")"
MAP_FILE="${REPO_ROOT}/skills/update-gs-docs/reference_map.txt"

BRANCH="${1:-develop}"
BASECAMP_DIR="${BASECAMP_DIR:-}"
RAW_BASE="https://raw.githubusercontent.com/tomkat-cr/genericsuite-basecamp/refs/heads/${BRANCH}"

if [ -z "${BASECAMP_DIR}" ] && [ -d "${REPO_ROOT}/../genericsuite-basecamp" ]; then
    BASECAMP_DIR="${REPO_ROOT}/../genericsuite-basecamp"
fi

if [ ! -f "${MAP_FILE}" ]; then
    echo "Error: map file not found: ${MAP_FILE}"
    exit 1
fi

changed=0
unchanged=0
failed=0

while IFS='|' read -r src dest; do
    # Skip comments and blank lines
    case "${src}" in
        \#*|"") continue ;;
    esac
    dest_path="${REPO_ROOT}/${dest}"
    mkdir -p "$(dirname "${dest_path}")"
    tmp_file="$(mktemp)"
    if [ -n "${BASECAMP_DIR}" ]; then
        if ! cp "${BASECAMP_DIR}/${src}" "${tmp_file}" 2>/dev/null; then
            echo "FAILED (local copy): ${src}"
            failed=$((failed + 1))
            rm -f "${tmp_file}"
            continue
        fi
    else
        if ! curl -fsSL "${RAW_BASE}/${src}" -o "${tmp_file}"; then
            echo "FAILED (download): ${src}"
            failed=$((failed + 1))
            rm -f "${tmp_file}"
            continue
        fi
    fi
    if [ -f "${dest_path}" ] && cmp -s "${tmp_file}" "${dest_path}"; then
        unchanged=$((unchanged + 1))
        rm -f "${tmp_file}"
    else
        mv "${tmp_file}" "${dest_path}"
        echo "CHANGED: ${dest}"
        changed=$((changed + 1))
    fi
done < "${MAP_FILE}"

echo ""
echo "Reference sync complete: ${changed} changed, ${unchanged} unchanged, ${failed} failed."
if [ "${failed}" -gt 0 ]; then
    exit 1
fi
```

- [ ] **Step 3: Run the sync against the local basecamp checkout**

Run (from repo root `packages/genericsuite-skills`):
```bash
BASECAMP_DIR=../genericsuite-basecamp bash skills/update-gs-docs/scripts/update-gs-docs.sh
```
Expected: `CHANGED:` lines for every new `skills/*/references/**` file (they didn't exist yet); existing `gs_docs` files report unchanged (the schema copy was already synced on 2026-07-10); final line `... 0 failed.` and exit code 0.

- [ ] **Step 4: Verify synced copies are byte-identical to their sources**

Run:
```bash
while IFS='|' read -r src dest; do
    case "${src}" in \#*|"") continue ;; esac
    cmp "../genericsuite-basecamp/${src}" "${dest}" || echo "MISMATCH: ${dest}"
done < skills/update-gs-docs/reference_map.txt; echo "verify done"
```
Expected: only `verify done` (no MISMATCH lines).

- [ ] **Step 5: Update `skills/update-gs-docs/SKILL.md`**

Replace the `## Scripts` section body with:

```markdown
## Scripts

- `scripts/update-gs-docs.sh`: Map-driven sync of reference files from the
  `genericsuite-basecamp` repository into this repo's skills. The file list
  lives in `skills/update-gs-docs/reference_map.txt` (format:
  `<basecamp-relative-path>|<this-repo-relative-path>`, `#` comments allowed).
  If `BASECAMP_DIR` points to a local basecamp checkout (or
  `../genericsuite-basecamp` exists, as in the GenericSuite superproject), it
  copies locally; otherwise it downloads from GitHub raw on the branch given
  as first argument (default `develop`). Run it via `make sync-references`.
  When adding a new skill that needs basecamp exemplars, append lines to
  `reference_map.txt` and re-run — do not hand-copy files.
```

- [ ] **Step 6: Add the Make target**

In `Makefile`, replace the `update-gs-docs:` target with:

```makefile
update-gs-docs: sync-references

sync-references:
	bash skills/update-gs-docs/scripts/update-gs-docs.sh $(BRANCH)
```

Run: `make sync-references`
Expected: same summary line as Step 3, `0 failed`.

- [ ] **Step 7: Commit**

```bash
git checkout -b feature/GS-254-app-builder-skills 2>/dev/null || git checkout feature/GS-254-app-builder-skills
git add skills/update-gs-docs skills/menu-builder skills/endpoints-builder skills/python-fastapi-code-builder skills/config-builder Makefile
git commit -m "Change: generalize update-gs-docs into map-driven reference sync with local BASECAMP_DIR mode; seed references for menu-builder, endpoints-builder and python-fastapi-code-builder [GS-254]"
```

---

### Task 2: `menu-builder` skill (Phase 1)

**Files:**
- Create: `skills/menu-builder/SKILL.md`
- Create: `skills/menu-builder/evals/evals.json`
- Create: `playground/gs-billing-app/config_dbdef/backend/app_main_menu.json` (eval fixture)
- Modify: `.claude-plugin/marketplace.json`
- Modify: `CLAUDE.md` (skills table)

**Interfaces:**
- Consumes: `skills/menu-builder/references/app_main_menu.example.json` (synced by Task 1).
- Produces: the `menu-builder` skill, invoked as `/menu-builder [ComponentName ...]`; Task 5 points config-builder/jsx-code-builder at it.

- [ ] **Step 1: Write `skills/menu-builder/SKILL.md`**

````markdown
---
name: menu-builder
description: Create or update GenericSuite app menu entries in backend/app_main_menu.json. Use when the user wants to add a CRUD editor, page, or menu group to the application menu, or right after config-builder/jsx-code-builder generate a new component that needs a menu entry. Performs idempotent JSON merges — never duplicates entries, never rewrites unrelated ones.
argument-hint: [ComponentName ...]
---

Add or update entries in the GenericSuite `backend/app_main_menu.json`
configuration file. A reference example of a complete menu file is bundled at
`references/app_main_menu.example.json`.

## Step 1 — Gather inputs

Ask the user (or infer from a preceding config-builder / jsx-code-builder run):

1. **Menu file path**: default `config_dbdef/backend/app_main_menu.json`
   relative to the project root (ExampleApp uses
   `apps/config_dbdef/backend/`). If the file does not exist, confirm before
   creating it with a `Home` `nav_link` entry as the first element.
2. **Entries to add**: for each one —
   - `title` (display name)
   - `element`: `<ComponentName>_EditorData` for CRUD editors, or the
     component name for plain pages
   - `type`: `editor` (CRUD editor, inside a dropdown) or `nav_link`
     (top-level page)
   - `sec_group`: `users` (regular users) or `admin` (superusers only)
3. **Menu group**: which `nav_dropdown` group the entry belongs to
   (`title` of an existing group, or a new group's title + `location`,
   usually `top_menu`).

## Step 2 — Validation rules (apply BEFORE editing)

- **Masters only**: child-listing components (frontend config
  `"type": "child_listing"`) never get menu entries — they are reached
  through their parent's form. If asked to add one, explain and skip it.
- **No duplicates**: if any group already contains an entry with the same
  `element`, skip it and report "already present" — do not add twice and do
  not overwrite its title/sec_group unless the user explicitly asks to
  update it.
- **Structure**: the file is a JSON array. Groups are objects with
  `title`, `location`, `type: "nav_dropdown"`, `sec_group`, and
  `sub_menu_options` (array). Editor entries are objects with `type`,
  `sec_group`, `title`, `element`.

## Step 3 — Apply the merge

Read the current file, then produce the updated JSON:

New editor entry (goes inside a group's `sub_menu_options`):

```json
{
    "type": "editor",
    "sec_group": "users",
    "title": "Display Title",
    "element": "ComponentName_EditorData"
}
```

New menu group (appended to the top-level array):

```json
{
    "title": "Menu Group Title",
    "location": "top_menu",
    "type": "nav_dropdown",
    "sec_group": "users",
    "sub_menu_options": []
}
```

Rules when editing:
- Preserve the order and content of every existing entry byte-for-byte
  (only add; never reformat unrelated objects).
- Keep 4-space indentation (repo convention for config_dbdef files).
- Append new entries at the END of the target group's `sub_menu_options`;
  append new groups at the END of the array.

## Step 4 — Verify and summarize

1. Parse the result with `python3 -c "import json; json.load(open('<path>'))"`
   to prove it is valid JSON.
2. Show the user a summary: entries added, entries skipped (duplicates /
   child listings), groups created.
3. Remind: the `element` name must exist in the frontend — for editors it is
   the `<ComponentName>_EditorData` function registered via App.jsx's
   componentMap (use the `jsx-code-builder` skill to generate it).
````

- [ ] **Step 2: Create the eval fixture `playground/gs-billing-app/config_dbdef/backend/app_main_menu.json`**

```json
[
    {
        "title": "Home",
        "location": "top_menu",
        "type": "nav_link",
        "path": "/",
        "element": "HomePage",
        "hard_prefix": false,
        "reload": true
    },
    {
        "title": "Billing",
        "location": "top_menu",
        "type": "nav_dropdown",
        "sec_group": "users",
        "sub_menu_options": [
            {
                "type": "editor",
                "sec_group": "users",
                "title": "Invoices",
                "element": "Invoices_EditorData"
            }
        ]
    }
]
```

- [ ] **Step 3: Write `skills/menu-builder/evals/evals.json`**

```json
{
    "skill_name": "menu-builder",
    "evals": [
        {
            "id": 1,
            "prompt": "Add menu entries for the Customers editor (component Customers, regular users) into a new 'Contacts' menu group, and for the Invoices editor (component Invoices, regular users) into the existing 'Billing' group. The menu file is at playground/gs-billing-app/config_dbdef/backend/app_main_menu.json. Write the updated file to playground/menu-builder-test/eval-1/app_main_menu.json (copy the original there first, then edit the copy).",
            "expected_output": "Updated app_main_menu.json with a new Contacts group containing Customers_EditorData; Billing group unchanged because Invoices_EditorData already exists",
            "files": [
                "playground/gs-billing-app/config_dbdef/backend/app_main_menu.json"
            ],
            "expectations": [
                "Output file parses as valid JSON (runtime validity)",
                "A new nav_dropdown group titled 'Contacts' exists with location top_menu and sec_group users",
                "The Contacts group's sub_menu_options contains exactly one editor entry with element 'Customers_EditorData'",
                "The Billing group still contains exactly ONE entry with element 'Invoices_EditorData' (duplicate was skipped, not added)",
                "Reports that Invoices_EditorData was skipped as already present",
                "The Home nav_link entry is preserved unchanged (same keys and values)"
            ]
        },
        {
            "id": 2,
            "prompt": "Add a menu entry for the InvoiceLines component (its frontend config playground/gs-billing-app/config_dbdef/frontend/invoice_lines.json has type child_listing) and for the Accounts editor (component Accounts, admin-only) in a new 'Accounting' group. Menu file: playground/gs-billing-app/config_dbdef/backend/app_main_menu.json. Write the result to playground/menu-builder-test/eval-2/app_main_menu.json (copy the original there first, then edit the copy).",
            "expected_output": "Accounts added under a new Accounting group with sec_group admin; InvoiceLines refused because child listings never get menu entries",
            "files": [
                "playground/gs-billing-app/config_dbdef/backend/app_main_menu.json",
                "playground/gs-billing-app/config_dbdef/frontend/invoice_lines.json"
            ],
            "expectations": [
                "Output file parses as valid JSON (runtime validity)",
                "No entry with element containing 'InvoiceLines' exists anywhere in the output",
                "Explains that child_listing components are accessed through the parent form and get no menu entry",
                "A new group titled 'Accounting' contains an editor entry with element 'Accounts_EditorData' and sec_group 'admin'"
            ]
        }
    ]
}
```

- [ ] **Step 4: Validate skill structure and JSON**

Run:
```bash
(cd skills/skill-creator && python3 -m scripts.quick_validate ../../skills/menu-builder)
python3 -c "import json; json.load(open('skills/menu-builder/evals/evals.json')); json.load(open('playground/gs-billing-app/config_dbdef/backend/app_main_menu.json')); print('OK')"
```
Expected: quick_validate reports the skill as valid (name/description frontmatter present); `OK`. (quick_validate resolves the path relative to its own working directory, hence the `cd skills/skill-creator` + `../../skills/<name>` form used throughout this plan.)

- [ ] **Step 5: Register the skill**

In `.claude-plugin/marketplace.json`, add to the `code-generation-skills` plugin's `skills` array:

```json
        "./skills/menu-builder"
```

In `CLAUDE.md`, add a row to the "Skills in this Repository" table:

```markdown
| `skills/menu-builder/` | Adds/updates menu entries in backend/app_main_menu.json (idempotent JSON merge) |
```

Run: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('OK')"`
Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add skills/menu-builder playground/gs-billing-app/config_dbdef/backend/app_main_menu.json .claude-plugin/marketplace.json CLAUDE.md
git commit -m "Add: menu-builder skill — idempotent app_main_menu.json merges with evals and playground fixture [GS-254]"
```

---

### Task 3: `endpoints-builder` skill (Phase 1)

**Files:**
- Create: `skills/endpoints-builder/SKILL.md`
- Create: `skills/endpoints-builder/evals/evals.json`
- Create: `playground/gs-billing-app/config_dbdef/backend/endpoints.json` (eval fixture)
- Modify: `.claude-plugin/marketplace.json`
- Modify: `CLAUDE.md` (skills table)

**Interfaces:**
- Consumes: `skills/endpoints-builder/references/endpoints.example.json` (Task 1); playground backend/frontend entity configs.
- Produces: the `endpoints-builder` skill, invoked as `/endpoints-builder [entity ...]`; Task 5 points other skills at it.

- [ ] **Step 1: Write `skills/endpoints-builder/SKILL.md`**

````markdown
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
            "handler_type": "flask" ,
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
````

- [ ] **Step 2: Create the eval fixture `playground/gs-billing-app/config_dbdef/backend/endpoints.json`**

```json
[
    {
        "name": "invoices",
        "url_prefix": "invoices",
        "routes": [
            {
                "endpoint": "/",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "handler_type": "GenericEndpointHelper",
                "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
                "params": {
                    "json_file": "invoices"
                }
            }
        ]
    }
]
```

- [ ] **Step 3: Write `skills/endpoints-builder/evals/evals.json`**

```json
{
    "skill_name": "endpoints-builder",
    "evals": [
        {
            "id": 1,
            "prompt": "Register API endpoints for these gs-billing-app entities: invoices, invoice_lines and customers. Their configs are under playground/gs-billing-app/config_dbdef/ (frontend/ and backend/). The endpoints file is playground/gs-billing-app/config_dbdef/backend/endpoints.json. Write the updated file to playground/endpoints-builder-test/eval-1/endpoints.json (copy the original there first, then edit the copy).",
            "expected_output": "endpoints.json gains customers and invoice_lines entries (invoice_lines is a subType table child); invoices skipped as already present",
            "files": [
                "playground/gs-billing-app/config_dbdef/backend/endpoints.json",
                "playground/gs-billing-app/config_dbdef/frontend/invoices.json",
                "playground/gs-billing-app/config_dbdef/frontend/invoice_lines.json",
                "playground/gs-billing-app/config_dbdef/frontend/customers.json"
            ],
            "expectations": [
                "Output file parses as valid JSON (runtime validity)",
                "Contains exactly ONE entry with url_prefix 'invoices' (duplicate skipped, reported as already present)",
                "Contains an entry with url_prefix 'invoice_lines' using GenericEndpointHelper and params.json_file 'invoice_lines' (child is subType table, so it IS registered)",
                "Contains an entry with url_prefix 'customers' with methods GET, POST, PUT, DELETE",
                "Every added route's view_func is 'lib.util.generic_endpoint_builder.generic_route_handler'",
                "The pre-existing invoices entry is preserved unchanged"
            ]
        },
        {
            "id": 2,
            "prompt": "The gs-billing-app has a child entity whose frontend config playground/endpoints-builder-test/fixtures/daily_notes.json has type child_listing and subType array. Register endpoints for it and for the vendors entity (playground/gs-billing-app/config_dbdef/frontend/vendors.json). Endpoints file: playground/gs-billing-app/config_dbdef/backend/endpoints.json. Write the result to playground/endpoints-builder-test/eval-2/endpoints.json (copy the original there first, then edit the copy).",
            "expected_output": "vendors registered; daily_notes refused because subType array children live inside the parent document",
            "files": [
                "playground/gs-billing-app/config_dbdef/backend/endpoints.json",
                "playground/gs-billing-app/config_dbdef/frontend/vendors.json"
            ],
            "expectations": [
                "Output file parses as valid JSON (runtime validity)",
                "No entry with url_prefix 'daily_notes' exists in the output",
                "Explains that subType array children need no endpoint because their data lives in the parent document",
                "Contains an entry with url_prefix 'vendors' using GenericEndpointHelper"
            ]
        }
    ]
}
```

- [ ] **Step 4: Create the eval-2 fixture `playground/endpoints-builder-test/fixtures/daily_notes.json`**

```json
{
    "baseUrl": "daily_notes",
    "title": "Daily Notes",
    "name": "Daily Note",
    "component": "DailyNotes",
    "dbApiUrl": "daily_notes",
    "type": "child_listing",
    "subType": "array",
    "array_name": "notes",
    "parentUrl": "invoices",
    "primaryKeyName": "id",
    "fieldElements": [
        {"name": "id", "required": true, "label": "ID", "type": "_id", "readonly": true, "hidden": true},
        {"name": "note", "required": true, "label": "Note", "type": "text", "listing": true}
    ]
}
```

- [ ] **Step 5: Validate skill structure and JSON**

Run:
```bash
(cd skills/skill-creator && python3 -m scripts.quick_validate ../../skills/endpoints-builder)
python3 -c "import json; [json.load(open(p)) for p in ['skills/endpoints-builder/evals/evals.json','playground/gs-billing-app/config_dbdef/backend/endpoints.json','playground/endpoints-builder-test/fixtures/daily_notes.json']]; print('OK')"
```
Expected: skill valid; `OK`.

- [ ] **Step 6: Register the skill**

`.claude-plugin/marketplace.json` — add to `code-generation-skills` skills array:
```json
        "./skills/endpoints-builder"
```

`CLAUDE.md` table row:
```markdown
| `skills/endpoints-builder/` | Adds/updates API endpoint registrations in backend/endpoints.json (idempotent JSON merge) |
```

Run: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('OK')"`
Expected: `OK`

- [ ] **Step 7: Commit**

```bash
git add skills/endpoints-builder playground/gs-billing-app/config_dbdef/backend/endpoints.json playground/endpoints-builder-test .claude-plugin/marketplace.json CLAUDE.md
git commit -m "Add: endpoints-builder skill — idempotent endpoints.json merges with evals and playground fixtures [GS-254]"
```

---

### Task 4: `python-fastapi-code-builder` skill (Phase 1)

**Files:**
- Create: `skills/python-fastapi-code-builder/SKILL.md`
- Create: `skills/python-fastapi-code-builder/evals/evals.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `CLAUDE.md` (skills table)

**Interfaces:**
- Consumes: `skills/python-fastapi-code-builder/references/**` (synced by Task 1: `routers/fda_food_endpoint.py`, `routers/food_moments.py`, `models/fda_food_endpoint_model.py`, `models/food_moments_model.py`, `main.py`, `crud_editor_config_classes.py`).
- Produces: the `python-fastapi-code-builder` skill, invoked as `/python-fastapi-code-builder [feature-name]`.

- [ ] **Step 1: Write `skills/python-fastapi-code-builder/SKILL.md`**

````markdown
---
name: python-fastapi-code-builder
description: Generate GenericSuite Python backend code — custom FastAPI endpoints and business-logic model modules built on the genericsuite-be abstraction layer (GenericDbHelper, BlueprintOne, standard result shape). Use when the user needs a backend endpoint or feature beyond the generic CRUD handlers, such as wrapping an external API, computed/aggregate endpoints, or custom actions. Not for plain CRUD entities (use config-builder + endpoints-builder for those).
argument-hint: [feature-name]
---

Generate custom GenericSuite backend code following the canonical patterns
bundled under `references/`:

- `references/routers/fda_food_endpoint.py` — FastAPI router wrapping an
  external API (POST with JSON body)
- `references/routers/food_moments.py` — FastAPI router for entity-specific
  custom actions
- `references/models/fda_food_endpoint_model.py` — model (business logic)
  layer for the external-API case
- `references/models/food_moments_model.py` — model layer using
  GenericDbHelper for DB access
- `references/main.py` — how routers are registered with `include_router`

READ the relevant reference files before generating — they are the source of
truth for idioms. Key architecture rules (non-negotiable):

1. **Two layers, always**: `lib/routers/<feature>.py` (framework wiring,
   FastAPI-specific) + `lib/models/<domain>/<feature>.py` (business logic,
   framework-agnostic — written against `genericsuite.util.*`, never
   importing `fastapi`).
2. **Standard result shape**: every model function returns
   `{"error": bool, "error_message": str | None, "resultset": Any}` —
   usually via `return_resultset_jsonified_or_exception()`.
3. **DB access**: MongoDB-style query syntax only (the DbAbstractor
   translates); parameterized values, never string-built queries.
4. **Security**: never log raw user input (sanitize newlines first); wrap
   AI/user-provided URLs and paths with `is_safe_url()` /
   `is_safe_local_path()` from genericsuite; secrets only via `Config`
   (env vars), never hardcoded.

## Step 1 — Gather requirements

Ask the user:

1. **Feature name** (snake_case, becomes the module name) and one-line
   purpose.
2. **Domain folder**: subdirectory under `lib/models/` (e.g.
   `external_apis`, `billing`, `utilities`).
3. **HTTP method(s)** and request parameters (name, type, required,
   default).
4. **What it does**: external API call, DB read/aggregate, custom write
   action? Which tables (config_dbdef backend JSON names) are involved?
5. **Auth**: JWT-protected (default, via `get_current_user`) or public?
6. **Project root**: where `lib/` lives (default `server/` for
   fastapitemplate-style projects, `apps/api-fastapi/` for
   exampleapp-style). Output to `playground/` when testing this skill.

## Step 2 — Generate the model layer

File: `lib/models/<domain>/<feature>.py` (create
`lib/models/<domain>/__init__.py` if the folder is new).

Template (adapt from `references/models/fda_food_endpoint_model.py`):

```python
"""
<Feature description>
"""
from typing import Optional

from genericsuite.util.framework_abs_layer import Response, BlueprintOne
from genericsuite.util.app_logger import log_debug
from genericsuite.util.jwt import AuthorizedRequest
from genericsuite.util.utilities import (
    get_request_body,
    return_resultset_jsonified_or_exception,
)
from genericsuite.config.config_from_db import app_context_and_set_env

DEBUG = False


def <feature>(
    request: AuthorizedRequest,
    blueprint: BlueprintOne,
    other_params: Optional[dict] = None,
) -> Response:
    """
    <Docstring: what it does, params, returns>
    """
    if other_params is None:
        other_params = {}
    params = get_request_body(request)

    app_context = app_context_and_set_env(request=request,
                                          blueprint=blueprint)
    if app_context.has_error():
        return return_resultset_jsonified_or_exception(
            app_context.get_error_resultset()
        )

    # ... business logic building `result` as
    # {"error": bool, "error_message": str | None, "resultset": ...}
    result = {"error": False, "error_message": None, "resultset": {}}
    return return_resultset_jsonified_or_exception(result)
```

For DB access inside the business logic, use GenericDbHelper with the
entity's backend JSON config name (see
`references/models/food_moments_model.py` for the working idiom):

```python
from genericsuite.util.generic_db_middleware import (
    fetch_all_from_db,
)
result = fetch_all_from_db(
    app_context=app_context,
    json_file='<entity_backend_config_name>',
    like_query_params={'name': '<search_value>'},
    combinator='$or',
)
```

## Step 3 — Generate the router layer

File: `lib/routers/<feature>.py`.

Template (adapt from `references/routers/fda_food_endpoint.py`):

```python
"""
<Feature> FastAPI endpoint
"""
from typing import Any
import json

from fastapi import Depends, Request as FaRequest
from fastapi.security import HTTPBasic

from genericsuite.fastapilib.framework_abstraction import BlueprintOne
from genericsuite.fastapilib.util.dependencies import (
    get_current_user,
    get_default_fa_request,
)

from lib.models.<domain>.<feature> import <feature> as <feature>_model

router = BlueprintOne()
security = HTTPBasic()


@router.post('', tags='<feature_tag>')
async def <feature>_endpoint(
    request: FaRequest,
    current_user: str = Depends(get_current_user),
) -> Any:
    """
    <Docstring>
    """
    try:
        params = await request.json()
    except json.JSONDecodeError:
        params = {}
    gs_request, other_params = get_default_fa_request(
        current_user=current_user,
        json_body=params,
    )
    router.set_current_request(request, gs_request)
    return <feature>_model(
        request=gs_request,
        blueprint=router,
        other_params=other_params,
    )
```

Validate required parameters in the router before calling the model, and
return the standard error shape directly on bad input:

```python
    if params.get('<required_param>', '') == '':
        return {
            'error': True,
            'error_message': '<required_param> is required',
            'status_code': 400,
            'resultset': {}
        }
```

## Step 4 — Wiring snippet for lib/main.py

Do NOT rewrite main.py. Output this snippet for the user to add (or apply it
if the user confirms):

```python
from lib.routers import <feature>

app.include_router(
    <feature>.router,
    prefix=f'/{settings.API_VERSION}/<feature_url>')
```

Note: custom FastAPI routers do NOT go into `config_dbdef/backend/endpoints.json`
(that file is for GenericEndpointHelper CRUD entities — see the
`endpoints-builder` skill).

## Step 5 — Verify and summarize

1. Syntax-check every generated file:
   `python3 -m py_compile <each generated .py file>` — must exit 0.
2. Lint if available: `flake8 <files>` (fall back to
   `python3 -m flake8`); fix any findings.
3. Confirm the model layer imports nothing from `fastapi` (layer
   separation): `grep -n "fastapi" lib/models/<domain>/<feature>.py`
   must return nothing.
4. Summarize files created, the main.py wiring snippet, and remind the user
   to add tests and run the dev server (`make dev`).
````

- [ ] **Step 2: Write `skills/python-fastapi-code-builder/evals/evals.json`**

```json
{
    "skill_name": "python-fastapi-code-builder",
    "evals": [
        {
            "id": 1,
            "prompt": "Generate a GenericSuite FastAPI backend feature called currency_rates: a POST endpoint that receives {\"base\": str, \"symbols\": str} and returns exchange rates fetched from an external API (use requests.get against https://api.frankfurter.dev/v1/latest with params, api key not required). Domain folder: external_apis. JWT-protected. Project root: playground/python-fastapi-code-builder-test/eval-1/",
            "expected_output": "lib/models/external_apis/currency_rates.py (model layer) and lib/routers/currency_rates.py (router) plus a main.py wiring snippet",
            "files": [],
            "expectations": [
                "Creates lib/models/external_apis/currency_rates.py and lib/routers/currency_rates.py under the output root",
                "Both files pass python3 -m py_compile (runtime validity)",
                "The model file does NOT import fastapi (layer separation)",
                "The model function signature is (request: AuthorizedRequest, blueprint: BlueprintOne, other_params: Optional[dict] = None) and it calls app_context_and_set_env",
                "The model returns via return_resultset_jsonified_or_exception with the standard {error, error_message, resultset} shape",
                "The router uses BlueprintOne, Depends(get_current_user), get_default_fa_request and router.set_current_request",
                "The router validates the required 'base' parameter and returns the standard error shape with status_code 400 when missing",
                "Outputs a main.py snippet using app.include_router with prefix f'/{settings.API_VERSION}/currency_rates'",
                "Does NOT add anything to endpoints.json and explains why (custom routers are registered in main.py)"
            ]
        },
        {
            "id": 2,
            "prompt": "Generate a GenericSuite FastAPI backend feature called invoice_totals: a POST endpoint that receives {\"customer_id\": str} and returns the number of invoices and the sum of their 'total' field for that customer, reading the invoices table through the GenericSuite DB middleware (backend config json_file 'invoices'). Domain folder: billing. Project root: playground/python-fastapi-code-builder-test/eval-2/",
            "expected_output": "lib/models/billing/invoice_totals.py using fetch_all_from_db with MongoDB-style filtering, lib/routers/invoice_totals.py, and a main.py wiring snippet",
            "files": [],
            "expectations": [
                "Creates lib/models/billing/invoice_totals.py, lib/models/billing/__init__.py and lib/routers/invoice_totals.py",
                "All generated .py files pass python3 -m py_compile (runtime validity)",
                "The model uses the GenericSuite DB middleware (e.g. fetch_all_from_db from genericsuite.util.generic_db_middleware) with json_file 'invoices' — no raw pymongo/SQL and no string-built queries",
                "The model does NOT import fastapi",
                "The result is returned in the standard {error, error_message, resultset} shape via return_resultset_jsonified_or_exception",
                "The router validates customer_id and returns the standard error shape with status_code 400 when missing"
            ]
        }
    ]
}
```

- [ ] **Step 3: Validate skill structure and JSON**

Run:
```bash
(cd skills/skill-creator && python3 -m scripts.quick_validate ../../skills/python-fastapi-code-builder)
python3 -c "import json; json.load(open('skills/python-fastapi-code-builder/evals/evals.json')); print('OK')"
```
Expected: skill valid; `OK`.

- [ ] **Step 4: Register the skill**

`.claude-plugin/marketplace.json` — add to `code-generation-skills` skills array:
```json
        "./skills/python-fastapi-code-builder"
```

`CLAUDE.md` table row:
```markdown
| `skills/python-fastapi-code-builder/` | Generates custom GenericSuite FastAPI routers + abstraction-layer model modules |
```

Run: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('OK')"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add skills/python-fastapi-code-builder .claude-plugin/marketplace.json CLAUDE.md
git commit -m "Add: python-fastapi-code-builder skill — custom FastAPI endpoints on the genericsuite-be abstraction layer, with evals [GS-254]"
```

---

### Task 5: Point existing skills at the new ones (Phase 1 close-out)

**Files:**
- Modify: `skills/config-builder/SKILL.md` (Step 3 section)
- Modify: `skills/jsx-code-builder/SKILL.md` (Step 4 intro + Step 5 summary)

**Interfaces:**
- Consumes: skill names `menu-builder`, `endpoints-builder` (Tasks 2–3).
- Produces: cross-skill handoff text; no code interfaces.

- [ ] **Step 1: Update `skills/config-builder/SKILL.md` Step 3**

Replace items 2 and 3 of the "Step 3 — Show what to do next" numbered list (menu entry + endpoint instructions, including the endpoint JSON code block) with:

```markdown
2. Add the menu entry to `backend/app_main_menu.json` — use the
   `menu-builder` skill (`/menu-builder <ComponentName>`) to apply it
   idempotently instead of editing by hand.
3. Add the API endpoint to `backend/endpoints.json` — use the
   `endpoints-builder` skill (`/endpoints-builder <entity>`); it skips
   `subType: "array"` children automatically.
```

- [ ] **Step 2: Update `skills/jsx-code-builder/SKILL.md` Step 4 intro**

Replace the sentence "After generating the JSX files, output these code snippets for the user to integrate into their existing files. Do NOT rewrite the full files — only show what needs to be added." with:

```markdown
After generating the JSX files, output these code snippets for the user to
integrate into their existing files. Do NOT rewrite the full files — only
show what needs to be added. For sections 4b (menu) and 4c (endpoints),
prefer invoking the `menu-builder` and `endpoints-builder` skills to apply
the changes idempotently; keep the snippets below as the fallback when those
skills are not available.
```

- [ ] **Step 3: Verify the skills still parse and reference real skill names**

Run:
```bash
grep -n "menu-builder\|endpoints-builder" skills/config-builder/SKILL.md skills/jsx-code-builder/SKILL.md
ls skills/menu-builder/SKILL.md skills/endpoints-builder/SKILL.md
```
Expected: grep shows the new references; both SKILL.md files exist.

- [ ] **Step 4: Commit**

```bash
git add skills/config-builder/SKILL.md skills/jsx-code-builder/SKILL.md
git commit -m "Change: config-builder and jsx-code-builder hand off menu/endpoint wiring to menu-builder and endpoints-builder skills [GS-254]"
```

---

### Task 6: Eval smoke run for the three new skills

**Files:**
- Create: `playground/menu-builder-test/`, `playground/endpoints-builder-test/`, `playground/python-fastapi-code-builder-test/` outputs (git-ignored or committed per playground convention — check `.gitignore`; commit only if playground outputs are already tracked).

**Interfaces:**
- Consumes: evals.json of Tasks 2–4.
- Produces: pass/fail evidence per eval; feeds the accept/iterate decision.

- [ ] **Step 1: Execute each eval prompt with the skill loaded**

For each of the 6 evals (2 per skill), dispatch a subagent whose prompt is the eval's `prompt` field verbatim, with the corresponding SKILL.md content prepended as its instructions (this mirrors how skill-creator's `with_skill` configuration runs). Collect outputs under the paths named in each prompt.

- [ ] **Step 2: Grade the expectations**

For each eval, check every `expectations` entry against the outputs. Mechanical ones are commands:

```bash
# runtime-validity examples
python3 -c "import json; json.load(open('playground/menu-builder-test/eval-1/app_main_menu.json')); print('OK')"
python3 -m py_compile playground/python-fastapi-code-builder-test/eval-1/lib/models/external_apis/currency_rates.py
grep -L fastapi playground/python-fastapi-code-builder-test/eval-1/lib/models/external_apis/currency_rates.py
```

Record pass/fail per expectation.

- [ ] **Step 3: Report and decide**

Present a per-skill pass-rate table to the user. 100% → accept. Any failure → fix the SKILL.md (not the expectation, unless the expectation is wrong), re-run that eval, and repeat once; if still failing, stop and discuss.

- [ ] **Step 4: Commit (fixtures/adjustments only, not transient outputs)**

```bash
git status --short  # review what changed
git add skills/ playground/
git commit -m "Change: adjustments from Phase-1 eval smoke run [GS-254]"
```
(Skip the commit if nothing changed.)

---

## Follow-up plans (not in this document)

Each later phase gets its own plan once this one ships, in dependency order:

1. **Phase 2 plan** — `python-ai-code-builder`, `python-ai-tools-code-builder`, `mcp-builder` (reference-map additions: `ai_assistant.py`, `ai_gpt_fn_*.py`, `mcp_server.py`, client configs).
2. **Phase 3 plan** — `jsx-ai-code-builder`.
3. **Phase 4 plan** — `app-starter` (wraps basecamp's `new-project-from-template.sh`).
4. **Phase 5 plan** — `gs-app-builder` orchestrator + end-to-end playground app build.
5. **Phase 6 plan** — README/CHANGELOG, basecamp docs page, `gs-app-builder-suite` plugin group finalization, publish to Claude Skills marketplace and skills.sh (GS-254 close-out).
