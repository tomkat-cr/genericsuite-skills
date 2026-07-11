# GenericSuite App-Builder Skill Suite — Phase 3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `jsx-ai-code-builder` — the skill that adds GenericSuite AI features to a React frontend (chatbot page wiring, per-field ChatBotButton popups, GsAiApp shell migration) — per `docs/design/2026-07-09-app-builder-skill-suite-design.md`.

**Architecture:** Same shape as Phases 1–2: one skill directory with SKILL.md + synced `references/` exemplars + `evals/evals.json` + playground fixtures + registration. The skill has three operations: (A) add an AI chat button to a CRUD field (JSON config attrs + JSX registry entry), (B) wire the chatbot page (App.jsx uses the `genericsuite-ai` App shell; menu gets the `/chatbot` nav_link), (C) verify constraints (no `dangerouslySetInnerHTML`, `renderMarkdownContent()` reuse).

**Tech Stack:** Markdown SKILL.md, JSX/JSON exemplars from exampleapp, Python 3 stdlib for JSON validation.

**Working directory for ALL tasks:** `/Users/carlosramirez/desarrollo/genericsuite/packages/genericsuite-skills`.

## Global Constraints

- **Commits:** per-task commits on branch `feature/GS-254-phase3` (established user preference from Phase 2); the user merges/pushes manually afterward. Never commit `__pycache__`/`.pyc` or transient `playground/*-test/` outputs.
- New skill: `SKILL.md` frontmatter with `name`, `description` (~100 words max), `argument-hint`; registered in `.claude-plugin/marketplace.json` (`code-generation-skills`, alphabetical); row in `CLAUDE.md` "Skills in this Repository" table (alphabetical); `evals/evals.json` with ≥2 cases.
- Eval expectations must include at least one runtime-validity assertion (JSON parse at minimum; JSX has no compile check available — use structural assertions).
- Frontend AI constraints (from the design doc): `genericsuite-fe-ai` reuses `renderMarkdownContent()`; **never** `dangerouslySetInnerHTML` — the skill must both obey and check this.
- Commit message style: `Add:`/`Change:`/`Fix:` prefix + `[GS-254]`.
- `quick_validate` must exit 0 for the new skill.
- Reference files are created by `make sync-references` / the map — never hand-authored.

---

### Task 1: Phase-3 reference seeding

**Files:**
- Modify: `skills/update-gs-docs/reference_map.txt` (append Phase-3 block)
- Created by sync: `skills/jsx-ai-code-builder/references/**`

**Interfaces:**
- Consumes: `BASECAMP_DIR=../genericsuite-basecamp bash skills/update-gs-docs/scripts/update-gs-docs.sh` (Phase 1).
- Produces: the three reference files below at exactly these paths — Task 2's SKILL.md cites them verbatim.

- [ ] **Step 1: Append to `skills/update-gs-docs/reference_map.txt`**

```
# jsx-ai-code-builder
mkdocs_root/code/exampleapp/apps/ui/src/components/UsersMenu/UserIngredients.jsx|skills/jsx-ai-code-builder/references/UserIngredients.example.jsx
mkdocs_root/code/exampleapp/apps/ui/src/components/App/App.jsx|skills/jsx-ai-code-builder/references/App.example.jsx
mkdocs_root/code/exampleapp/apps/config_dbdef/frontend/user_ingredients.json|skills/jsx-ai-code-builder/references/user_ingredients.example.json
```

- [ ] **Step 2: Run the sync**

Run: `BASECAMP_DIR=../genericsuite-basecamp bash skills/update-gs-docs/scripts/update-gs-docs.sh`
Expected: `CHANGED:` for the 3 new destinations; `0 failed`; everything else unchanged.

- [ ] **Step 3: Verify byte-identity**

Run:
```bash
while IFS='|' read -r src dest; do
    case "${src}" in \#*|"") continue ;; esac
    cmp "../genericsuite-basecamp/${src}" "${dest}" || echo "MISMATCH: ${dest}"
done < skills/update-gs-docs/reference_map.txt; echo "verify done"
python3 -c "import json; json.load(open('skills/jsx-ai-code-builder/references/user_ingredients.example.json')); print('OK')"
```
Expected: `verify done` with no MISMATCH lines; `OK`.

- [ ] **Step 4: Commit**

```bash
git add skills/update-gs-docs/reference_map.txt skills/jsx-ai-code-builder
git commit -m "Add: Phase-3 reference seeding for jsx-ai-code-builder [GS-254]"
```

---

### Task 2: `jsx-ai-code-builder` skill + fixtures

**Files:**
- Create: `skills/jsx-ai-code-builder/SKILL.md`
- Create: `skills/jsx-ai-code-builder/evals/evals.json`
- Create: `playground/gs-billing-app/ui-fixtures/src/components/BillingMenu/Invoices.jsx` (eval-1 fixture)
- Create: `playground/gs-billing-app/ui-fixtures/src/components/App/App.jsx` (eval-2 fixture)
- Modify: `.claude-plugin/marketplace.json`, `CLAUDE.md`

**Interfaces:**
- Consumes: `skills/jsx-ai-code-builder/references/**` (Task 1); Phase-1 skills `menu-builder` (chatbot nav_link) and `config-builder` conventions; the existing fixture `playground/gs-billing-app/config_dbdef/frontend/invoices.json`.
- Produces: the skill, invoked as `/jsx-ai-code-builder [component-or-config ...]`.

- [ ] **Step 1: Write `skills/jsx-ai-code-builder/SKILL.md`**

````markdown
---
name: jsx-ai-code-builder
description: Add GenericSuite AI features to a React frontend — per-field AI chat buttons (chatbot_popup + ChatBotButton from genericsuite-ai), the AI assistant chatbot page and menu entry, and migration of App.jsx to the genericsuite-ai App shell. Use when the user wants AI/chatbot capabilities in a GenericSuite UI, or right after jsx-code-builder when configs carry chatbot_popup fields. Requires the backend assistant from python-ai-code-builder to be useful at runtime.
argument-hint: [component-or-config ...]
---

Add AI features to a GenericSuite React frontend, following the canonical
patterns bundled under `references/`:

- `references/UserIngredients.example.jsx` — component with
  `ChatBotButton` (the `import * as gsAi from "genericsuite-ai"` +
  registry idiom)
- `references/App.example.jsx` — App.jsx built on the genericsuite-ai
  App shell (`import { App as GsAiApp } from "genericsuite-ai"`)
- `references/user_ingredients.example.json` — frontend config with a
  `chatbot_popup` field (all popup attributes in real use)

READ the reference files before editing. Hard constraints:

1. **Never** use `dangerouslySetInnerHTML` — genericsuite-fe-ai renders
   markdown via its `renderMarkdownContent()` helper. If you find
   `dangerouslySetInnerHTML` in code you're editing, warn the user.
2. The chatbot page component (`Chatbot`, path `/chatbot`) is BUILT INTO
   the genericsuite-ai App shell — it needs a menu entry but NO
   componentMap entry and NO new component file.
3. All JSON edits are idempotent: never duplicate attributes or menu
   entries; preserve unrelated content byte-for-byte.

## Step 1 — Gather inputs

1. **Operation(s)** wanted (any combination):
   - **A. Field chat button**: which frontend config JSON + which field
     gets the AI popup, and the chatbot prompt text (use `%s` where the
     field value goes). Optionally a Google-search popup too.
   - **B. Chatbot page**: wire the AI assistant page into the app
     (App shell migration if needed + menu entry).
2. **Paths**: UI source root (default `ui/src/` for fastapitemplate,
   `apps/ui/src/` for exampleapp), frontend configs directory, and
   `backend/app_main_menu.json` location. Output to `playground/` when
   testing this skill.
3. **Backend check** (advisory): the AI features call the backend
   assistant endpoints (`/ai/chatbot` etc.). If the project lacks
   `lib/routers/ai_assistant.py`, remind the user to run
   `/python-ai-code-builder` — do not block.

## Step 2 — Operation A: add a field chat button

### 2a. Frontend config JSON

Add to the chosen field element (keep existing attributes untouched):

```json
{
    "...existing field attributes...": "...",
    "chatbot_popup": true,
    "aux_component": "ChatBotButton",
    "chatbot_prompt": "<prompt text with %s for the field value>"
}
```

Optional Google popup (only if the user asked):

```json
    "google_popup": true,
    "google_prompt": "<query with %s>"
```

Validate the result parses as JSON and the field still has its original
`name`/`label`/`type`.

### 2b. Component JSX

Edit the component that consumes this config (find it by the config's
`component` attribute under `src/components/**`):

1. Add the import if missing:
```jsx
import * as gsAi from "genericsuite-ai";
```
2. Add the alias after the other `const ... = gs....` lines:
```jsx
const ChatBotButton = gsAi.ChatBotButton;
```
3. Add to the `registry` object in `<Component>_EditorData()`:
```jsx
        "ChatBotButton": ChatBotButton,
```

All three edits are idempotent — skip any already present. Check
`package.json` in the UI root lists `genericsuite-ai`; if missing, output
the install reminder (`npm install genericsuite-ai`) — do not run it.

## Step 3 — Operation B: wire the chatbot page

### 3a. App shell

Read `src/components/App/App.jsx`:

- Already `import { App as GsAiApp } from "genericsuite-ai"` → nothing to
  do.
- Uses the plain `genericsuite` App (e.g. `import { App as GsApp } from
  "genericsuite"` or `gs.App`) → migrate: replace the import with
  `import { App as GsAiApp } from "genericsuite-ai";` and the JSX element
  with `<GsAiApp ...same props...>`. Preserve `appLogo`,
  `appLogoHeader`, `componentMap` and every componentMap entry
  byte-for-byte.

### 3b. Menu entry

Add to `backend/app_main_menu.json` (top-level array, before the
hamburger/User Menu group if present) — prefer invoking the
`menu-builder` skill; the entry shape:

```json
{
    "title": "<App name> Assistant",
    "location": "top_menu",
    "type": "nav_link",
    "sec_group": "users",
    "path": "/chatbot",
    "element": "Chatbot"
}
```

`Chatbot` is provided by the genericsuite-ai App shell — do NOT add it to
componentMap and do NOT create a component file. Skip if an entry with
`"path": "/chatbot"` already exists.

## Step 4 — Verify and summarize

1. Every edited JSON file parses:
   `python3 -c "import json; json.load(open('<path>'))"`.
2. `grep -n "dangerouslySetInnerHTML" <edited .jsx files>` → must return
   nothing.
3. For Operation A: the config field has `chatbot_popup`,
   `aux_component`, `chatbot_prompt`; the JSX has the import, alias and
   registry entry exactly once each.
4. For Operation B: App.jsx imports the genericsuite-ai App; the menu has
   exactly one `/chatbot` entry; componentMap unchanged (Operation B
   alone must not modify it).
5. Summarize edits applied/skipped, the backend-assistant advisory if it
   fired, and remind: run the dev server (`make dev` /
   `make exampleapp-run`) to test the chat button and /chatbot page.
````

- [ ] **Step 2: Create the eval-1 fixture `playground/gs-billing-app/ui-fixtures/src/components/ContactsMenu/Customers.jsx`**

(The Phase-1 jsx-code-builder output shape for the customers standalone master — no AI yet. The customers config has a `name` text field, mirroring the canonical exampleapp chat-button-on-name example:)

```jsx
import React from 'react';

import * as gs from "genericsuite";
import customersConfig from "../../configs/frontend/customers.json";

const GenericCrudEditor = gs.genericEditorRfcService.GenericCrudEditor;
const GetFormData = gs.genericEditorRfcService.GetFormData;

const console_debug_log = gs.loggingService.console_debug_log;

export function Customers_EditorData() {
    console_debug_log("Customers_EditorData");
    const registry = {
        "Customers": Customers,
    }
    return GetFormData(customersConfig, registry, 'Customers_EditorData');
}

export const Customers = () => (
    <GenericCrudEditor editorConfig={Customers_EditorData()} />
)
```

- [ ] **Step 3: Create the eval-2 fixture `playground/gs-billing-app/ui-fixtures/src/components/App/App.jsx`**

(A plain-genericsuite App shell — the migration target:)

```jsx
import React from 'react';

import { App as GsApp } from "genericsuite";

import { Invoices } from '../BillingMenu/Invoices.jsx';
import { Customers } from '../ContactsMenu/Customers.jsx';
import { HomePage } from '../HomePage/HomePage.jsx';

const AppLogo = 'app_logo_circle.svg';
const AppLogoHeader = 'app_logo_horizontal.svg';

const componentMap = {
    "Invoices": Invoices,
    "Customers": Customers,
    "HomePage": HomePage,
};

export const App = () => {
    return (
        <GsApp
            appLogo={AppLogo}
            appLogoHeader={AppLogoHeader}
            componentMap={componentMap}
        />
    );
}
```

- [ ] **Step 4: Write `skills/jsx-ai-code-builder/evals/evals.json`**

```json
{
    "skill_name": "jsx-ai-code-builder",
    "evals": [
        {
            "id": 1,
            "prompt": "Add an AI chat button to the 'name' field of the customers editor. Chatbot prompt: 'Give me a company profile summary for the customer named %s, including industry and typical billing terms.'. No Google popup. The frontend config is playground/gs-billing-app/config_dbdef/frontend/customers.json and the component is playground/gs-billing-app/ui-fixtures/src/components/ContactsMenu/Customers.jsx. Copy both into playground/jsx-ai-code-builder-test/eval-1/ (preserving the relative layout: config_dbdef/frontend/customers.json and src/components/ContactsMenu/Customers.jsx) and edit the copies only.",
            "expected_output": "customers.json gains chatbot_popup/aux_component/chatbot_prompt on the name field; Customers.jsx gains the gsAi import, ChatBotButton alias and registry entry",
            "files": [
                "playground/gs-billing-app/config_dbdef/frontend/customers.json",
                "playground/gs-billing-app/ui-fixtures/src/components/ContactsMenu/Customers.jsx"
            ],
            "expectations": [
                "The edited customers.json parses as valid JSON (runtime validity)",
                "The 'name' field element has chatbot_popup true, aux_component 'ChatBotButton' and the exact chatbot_prompt text with %s; its original name/label/type attributes are unchanged",
                "No google_popup/google_prompt attributes were added (not requested)",
                "Customers.jsx contains exactly one `import * as gsAi from \"genericsuite-ai\"`, one `const ChatBotButton = gsAi.ChatBotButton;` and one `\"ChatBotButton\": ChatBotButton,` registry entry",
                "Customers.jsx contains no dangerouslySetInnerHTML",
                "All other fields in customers.json and all other registry entries in Customers.jsx are unchanged",
                "The original files under playground/gs-billing-app/ are untouched"
            ]
        },
        {
            "id": 2,
            "prompt": "Wire the AI chatbot page into the gs-billing-app frontend: migrate the App shell to genericsuite-ai and add the assistant menu entry titled 'Billing Assistant'. The App component is playground/gs-billing-app/ui-fixtures/src/components/App/App.jsx and the menu file is playground/gs-billing-app/config_dbdef/backend/app_main_menu.json. Copy both into playground/jsx-ai-code-builder-test/eval-2/ (layout: src/components/App/App.jsx and config_dbdef/backend/app_main_menu.json) and edit the copies only.",
            "expected_output": "App.jsx imports the genericsuite-ai App shell with componentMap preserved; menu gains one /chatbot nav_link with element 'Chatbot'",
            "files": [
                "playground/gs-billing-app/ui-fixtures/src/components/App/App.jsx",
                "playground/gs-billing-app/config_dbdef/backend/app_main_menu.json"
            ],
            "expectations": [
                "The edited app_main_menu.json parses as valid JSON (runtime validity)",
                "App.jsx imports `{ App as GsAiApp } from \"genericsuite-ai\"` and renders <GsAiApp with the same appLogo, appLogoHeader and componentMap props; no `from \"genericsuite\"` App import remains",
                "The componentMap object still contains exactly Invoices, Customers and HomePage — no 'Chatbot' entry was added to it",
                "The menu contains exactly one entry with path '/chatbot': type nav_link, location top_menu, sec_group users, title 'Billing Assistant', element 'Chatbot'",
                "All pre-existing menu entries (Home nav_link, Billing group) are unchanged",
                "No component file was created for the Chatbot element",
                "The original files under playground/gs-billing-app/ are untouched"
            ]
        }
    ]
}
```

- [ ] **Step 5: Validate**

Run:
```bash
(cd skills/skill-creator && python3 -m scripts.quick_validate ../../skills/jsx-ai-code-builder)
python3 -c "import json; json.load(open('skills/jsx-ai-code-builder/evals/evals.json')); print('OK')"
```
Expected: skill valid (exit 0); `OK`.

- [ ] **Step 6: Register the skill**

`.claude-plugin/marketplace.json` — add `"./skills/jsx-ai-code-builder"` to `code-generation-skills` (alphabetical: after `endpoints-builder`, before `jsx-code-builder`). `CLAUDE.md` table row in the same slot:

```markdown
| `skills/jsx-ai-code-builder/` | Adds AI features to the React frontend (field chat buttons, chatbot page, genericsuite-ai App shell) |
```

Run: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('OK')"` → `OK`.

- [ ] **Step 7: Commit**

```bash
git add skills/jsx-ai-code-builder playground/gs-billing-app/ui-fixtures .claude-plugin/marketplace.json CLAUDE.md
git commit -m "Add: jsx-ai-code-builder skill — frontend AI wiring (chat buttons, chatbot page, GsAiApp shell) with evals and fixtures [GS-254]"
```

---

### Task 3: Update jsx-code-builder handoff + eval smoke run

**Files:**
- Modify: `skills/jsx-code-builder/SKILL.md` (Step 2e)
- Create (transient, not committed): `playground/jsx-ai-code-builder-test/`

**Interfaces:**
- Consumes: Task 2's skill and evals.
- Produces: handoff pointer; pass/fail evidence.

- [ ] **Step 1: Point jsx-code-builder at the new skill**

In `skills/jsx-code-builder/SKILL.md`, section "### 2e. Classify auxiliary components", replace the line:

```markdown
- `ChatBotButton` → requires `import * as gsAi from "genericsuite-ai"` and `const ChatBotButton = gsAi.ChatBotButton;`
```

with:

```markdown
- `ChatBotButton` → requires `import * as gsAi from "genericsuite-ai"` and `const ChatBotButton = gsAi.ChatBotButton;` (to ADD AI buttons to fields that don't have them yet — or to wire the chatbot page — use the `jsx-ai-code-builder` skill)
```

- [ ] **Step 2: Execute both eval prompts with the skill loaded**

Dispatch one subagent per eval: prompt = the eval's `prompt` verbatim, prefixed with "read and follow skills/jsx-ai-code-builder/SKILL.md exactly"; act autonomously; no git commands; no network; clean up any `__pycache__`. The two evals are independent — they may run in parallel.

- [ ] **Step 3: Grade mechanically**

```bash
python3 - <<'EOF'
import json
# eval 1
cfg = json.load(open('playground/jsx-ai-code-builder-test/eval-1/config_dbdef/frontend/customers.json'))
fld = [f for f in cfg['fieldElements'] if f['name']=='name'][0]
assert fld.get('chatbot_popup') is True and fld.get('aux_component')=='ChatBotButton' and '%s' in fld.get('chatbot_prompt','')
assert 'google_popup' not in fld
jsx = open('playground/jsx-ai-code-builder-test/eval-1/src/components/ContactsMenu/Customers.jsx').read()
assert jsx.count('import * as gsAi from "genericsuite-ai"')==1
assert jsx.count('const ChatBotButton = gsAi.ChatBotButton;')==1
assert jsx.count('"ChatBotButton": ChatBotButton,')==1
assert 'dangerouslySetInnerHTML' not in jsx
# eval 2
app = open('playground/jsx-ai-code-builder-test/eval-2/src/components/App/App.jsx').read()
assert 'App as GsAiApp } from "genericsuite-ai"' in app and '<GsAiApp' in app
assert 'from "genericsuite"' not in app.split('genericsuite-ai')[0] or 'App as GsApp' not in app
assert '"Chatbot"' not in app  # componentMap must NOT gain a Chatbot entry
menu = json.load(open('playground/jsx-ai-code-builder-test/eval-2/config_dbdef/backend/app_main_menu.json'))
cb = [e for e in menu if e.get('path')=='/chatbot']
assert len(cb)==1 and cb[0]['element']=='Chatbot' and cb[0]['type']=='nav_link' and cb[0]['title']=='Billing Assistant'
# originals untouched
orig = json.load(open('playground/gs-billing-app/config_dbdef/frontend/customers.json'))
assert not any('chatbot_popup' in f for f in orig['fieldElements'])
print("ALL PASS")
EOF
```
Expected: `ALL PASS`. Non-mechanical expectations (reports, advisories) are graded from the eval subagents' final messages.

- [ ] **Step 4: Report and decide**

100% → accept. Any failure → fix the SKILL.md (not the expectation, unless the expectation is wrong per canonical evidence), re-run that eval once; still failing → stop and discuss.

- [ ] **Step 5: Commit (handoff edit + any smoke-run adjustments; skip transient outputs)**

```bash
git add skills/jsx-code-builder/SKILL.md skills/jsx-ai-code-builder
git commit -m "Change: jsx-code-builder hands off AI wiring to jsx-ai-code-builder; Phase-3 eval smoke-run adjustments [GS-254]"
```

---

## Follow-up plans (not in this document)

1. **Phase 4** — `app-starter` (wraps basecamp's `new-project-from-template.sh`; greenfield only, per the design's brownfield mode-detection note).
2. **Phase 5** — `gs-app-builder` orchestrator (with greenfield/brownfield mode detection, step 0 of the design's flow) + end-to-end playground app.
3. **Phase 6** — docs, CHANGELOG, plugin-group decision, publish to Claude Skills marketplace and skills.sh; deferred minors (unused `log_debug` in the tools template) (GS-254 close-out).
