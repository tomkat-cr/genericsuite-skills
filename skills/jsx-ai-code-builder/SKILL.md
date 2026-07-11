---
name: jsx-ai-code-builder
description: "Add GenericSuite AI features to a React frontend — per-field AI chat buttons (chatbot_popup + ChatBotButton from genericsuite-ai), the AI assistant chatbot page and menu entry, and migration of App.jsx to the genericsuite-ai App shell. Use when the user wants AI/chatbot capabilities in a GenericSuite UI, or right after jsx-code-builder when configs carry chatbot_popup fields. Requires the backend assistant from python-ai-code-builder to be useful at runtime."
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
  When the old shell was used via `import * as gs from "genericsuite"` +
  `gs.App`, add the new `genericsuite-ai` import and keep the `import *
  as gs` line only if other `gs.*` references remain in the file.

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

When delegating to `menu-builder`, two of its defaults do NOT apply here:
its "element must be registered in componentMap" reminder is wrong for
`Chatbot` (the genericsuite-ai App shell provides it — never add it to
componentMap), and instead of appending at the end of the array, place
this entry before the hamburger/User Menu group when one exists.

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
