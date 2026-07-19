---
name: jsx-code-builder
description: Generate ReactJS component JSX files from GenericSuite frontend JSON configuration files (config_dbdef/frontend). Use when the user wants to create or scaffold React CRUD editor components (.jsx files) from existing frontend JSON configs, or right after running the config-builder skill. Handles batch generation of master + all child components in one go.
argument-hint: [path/to/frontend-config.json]
---

Generate GenericSuite React component `.jsx` files from frontend JSON configuration files.

This skill reads a `config_dbdef/frontend` JSON file (or a set of master + child JSON configs) and produces ready-to-use React component files that follow the GenericSuite `GenericCrudEditor` pattern.

For additional context on field types and configuration options, see:
- `skills/config-builder/gs_docs/en/Configuration-Guide/index.md`
- `skills/config-builder/gs_docs/en/Configuration-Guide/Generic-CRUD-Editor-Configuration.md`
- `skills/config-builder/gs_docs/code/configuration-guide/crud_editor_config_classes.py` (Pydantic validation schema)

## Step 1 — Gather inputs

Ask the user the following (many can be inferred from context if this skill runs right after `config-builder`):

1. **Frontend JSON config path**: Path to the master frontend JSON config file, or paste the JSON inline. Example: `src/configs/frontend/invoices.json`
2. **Menu group folder**: The subdirectory name under `src/components/` where the JSX files will live (e.g. `SalesMenu`, `BillingMenu`). This becomes the component folder name.
3. **Output path**: Where to write the generated files. Defaults to `playground/` per project conventions. The user can specify their actual project path (e.g. `~/projects/myapp/ui/src/`).
4. **App constants file** (optional): Path to the project's `app_constants.jsx` if it exists, to check which constants are already exported. Defaults to `src/constants/app_constants.jsx`.

## Step 2 — Parse JSON and analyze dependencies

Read the master JSON config and perform the following analysis:

### 2a. Extract metadata

From the JSON config, extract:
- `component` — the React component name (e.g. `Invoices`)
- `type` — if `"child_listing"`, this is a child component; otherwise it's a master
- `childComponents` — array of child component names (e.g. `["InvoiceLines"]`)
- `baseUrl` — used for deriving the config file name
- `dbApiUrl` — the API endpoint URL

### 2b. Batch discovery (find child configs)

If `childComponents` exists in the master config:
1. Look in the **same directory** as the master config for each child's JSON file
2. Match by scanning JSON files for `"component": "ChildComponentName"` or by converting the child component name to snake_case (e.g. `InvoiceLines` → `invoice_lines.json`)
3. Read and parse each child config

### 2c. Scan field dependencies

For **each** config (master + all children), scan `fieldElements` and collect:

| What to find | Where | Collect |
|---|---|---|
| `"type": "select"` with `"select_elements"` | fieldElements | Constant name (e.g. `GENDERS`) — see validation below |
| `"formula"` attribute | fieldElements | Formula function name |
| `"aux_component"` attribute | fieldElements | Auxiliary component name (e.g. `ChatBotButton`) |
| `"type": "component"` | fieldElements | Custom component name |

### 2c-bis. Validate `select_elements` shape

`GetFormData` only resolves `select_elements` through the registry when it is a
**string** (constant name). Arrays pass through untouched, and the renderer
(`putSelectOptionsFromArray` / `getSelectDescription`) reads `option.title` and
`option.value` on each element. Therefore, for every `"type": "select"` field:

- **String** (e.g. `"GENDERS"`) — valid; collect as a constant (step 2d).
- **Array of `{title, value}` objects** — valid inline form; no constant import
  or registry entry needed.
- **Array of bare strings** (e.g. `["Asset", "Liability"]`) — **INVALID**: it
  compiles but renders empty/broken select options at runtime. Do NOT generate
  silently. Stop and tell the user, offering to fix the JSON config by either
  (a) converting to `[{"title": "Asset", "value": "asset"}, ...]`, or
  (b) extracting a named constant into `app_constants`.

### 2d. Classify constants

Separate constants into two categories:

**GenericSuite built-in constants** (import from `gs.generalConstants`):
- `TRUE_FALSE`
- `YES_NO`
- `LANGUAGES`

**App-specific constants** (import from `app_constants.jsx`):
- Everything else (e.g. `GENDERS`, `BILLING_PLANS`, `CALORIE_UNITS`)

### 2e. Classify auxiliary components

- `ChatBotButton` → requires `import * as gsAi from "genericsuite-ai"` and `const ChatBotButton = gsAi.ChatBotButton;` (to ADD AI buttons to fields that don't have them yet — or to wire the chatbot page — use the `jsx-ai-code-builder` skill)
- Any other auxiliary component → ask the user for the import source

## Step 3 — Generate JSX files

Generate all JSX files in a single pass: the master component and every child detected in `childComponents`.

### Config variable naming convention

Convert the JSON filename from snake_case to camelCase and append `Config`:
- `example_main_element.json` → `exampleMainElementConfig`
- `invoices.json` → `invoicesConfig`
- `invoice_lines.json` → `invoiceLinesConfig`

### 3a. Master (top-level) component template

File path: `src/components/{MenuGroup}/{ComponentName}.jsx`

```jsx
import React from 'react';

import * as gs from "genericsuite";
// IF ChatBotButton is needed:
// import * as gsAi from "genericsuite-ai";
import {configVarName} from "../../configs/frontend/{entity_name}.json";
// IF app-specific constants exist:
import {
    CONSTANT_1,
    CONSTANT_2,
} from '../../constants/app_constants.jsx';
// FOR EACH child component:
import {
    ChildComponent,
} from './{ChildComponent}.jsx';

const GenericCrudEditor = gs.genericEditorRfcService.GenericCrudEditor;
const GetFormData = gs.genericEditorRfcService.GetFormData;
// IF GS built-in constants are needed:
// const TRUE_FALSE = gs.generalConstants.TRUE_FALSE;
// IF ChatBotButton:
// const ChatBotButton = gsAi.ChatBotButton;

// To show debug data in the Browser's developer tools console
const console_debug_log = gs.loggingService.console_debug_log;

export function {ComponentName}_EditorData() {
    console_debug_log("{ComponentName}_EditorData");
    const registry = {
        "{ComponentName}": {ComponentName},
        // Each child component:
        "{ChildComponent}": {ChildComponent},
        // Each constant (both GS built-in and app-specific):
        "{CONSTANT}": {CONSTANT},
        // Each formula function:
        // "{formulaFunc}": {formulaFunc},
        // Each aux component:
        // "{AuxComponent}": {AuxComponent},
    }
    return GetFormData({configVarName}, registry, '{ComponentName}_EditorData');
}

export const {ComponentName} = () => (
    <GenericCrudEditor editorConfig={{ComponentName}_EditorData()} />
)
```

**Concrete example** — given `invoices.json` with component `Invoices` and child `InvoiceLines`:

```jsx
import React from 'react';

import * as gs from "genericsuite";
import invoicesConfig from "../../configs/frontend/invoices.json";

import {
    InvoiceLines,
} from './InvoiceLines.jsx';

const GenericCrudEditor = gs.genericEditorRfcService.GenericCrudEditor;
const GetFormData = gs.genericEditorRfcService.GetFormData;

const console_debug_log = gs.loggingService.console_debug_log;

export function Invoices_EditorData() {
    console_debug_log("Invoices_EditorData");
    const registry = {
        "Invoices": Invoices,
        "InvoiceLines": InvoiceLines,
    }
    return GetFormData(invoicesConfig, registry, 'Invoices_EditorData');
}

export const Invoices = () => (
    <GenericCrudEditor editorConfig={Invoices_EditorData()} />
)
```

### 3b. Child component template

File path: `src/components/{MenuGroup}/{ChildComponentName}.jsx`

Key differences from the master template:
- The component receives `{parentData, handleFormPageActions}` as props
- The third argument to `GetFormData` is `false` (not the EditorData name string)
- No `console_debug_log` import needed

```jsx
import React from 'react';

import * as gs from "genericsuite";
import {configVarName} from "../../configs/frontend/{child_entity_name}.json";

// IF GS built-in constants:
const TRUE_FALSE = gs.generalConstants.TRUE_FALSE;

const GenericCrudEditor = gs.genericEditorRfcService.GenericCrudEditor;
const GetFormData = gs.genericEditorRfcService.GetFormData;

export function {ChildComponent}_EditorData() {
    const registry = {
        "{ChildComponent}": {ChildComponent},
        // Each constant:
        "{CONSTANT}": {CONSTANT},
    }
    return GetFormData({configVarName}, registry, false);
}

export const {ChildComponent} = ({parentData, handleFormPageActions}) => (
    <GenericCrudEditor
        editorConfig={{ChildComponent}_EditorData()}
        parentData={parentData}
        handleFormPageActions={handleFormPageActions}
    />
)
```

**Concrete example** — given `invoice_lines.json` with component `InvoiceLines`:

```jsx
import React from 'react';

import * as gs from "genericsuite";
import invoiceLinesConfig from "../../configs/frontend/invoice_lines.json";

const GenericCrudEditor = gs.genericEditorRfcService.GenericCrudEditor;
const GetFormData = gs.genericEditorRfcService.GetFormData;

export function InvoiceLines_EditorData() {
    const registry = {
        "InvoiceLines": InvoiceLines,
    }
    return GetFormData(invoiceLinesConfig, registry, false);
}

export const InvoiceLines = ({parentData, handleFormPageActions}) => (
    <GenericCrudEditor
        editorConfig={InvoiceLines_EditorData()}
        parentData={parentData}
        handleFormPageActions={handleFormPageActions}
    />
)
```

## Step 4 — Generate integration snippets

After generating the JSX files, output these code snippets for the user to
integrate into their existing files. Do NOT rewrite the full files — only
show what needs to be added. For sections 4b (menu) and 4c (endpoints),
prefer invoking the `menu-builder` and `endpoints-builder` skills to apply
the changes idempotently; keep the snippets below as the fallback when those
skills are not available.

### 4a. App.jsx — imports and componentMap

```jsx
// Add these imports at the top of App.jsx:
import { ComponentName } from '../MenuGroup/ComponentName.jsx';
import { ChildComponent } from '../MenuGroup/ChildComponent.jsx';

// Add these entries to the componentMap object:
"ComponentName": ComponentName,
"ChildComponent": ChildComponent,
// If formula functions exist, add them too:
// "formulaFuncName": () => ( /* formula logic */ ),
```

### 4b. app_main_menu.json — menu entry (master components only)

Only master components get menu entries. Child components are accessed through their parent's form.

```json
{
    "type": "editor",
    "sec_group": "users",
    "title": "Display Title",
    "element": "ComponentName_EditorData"
}
```

This entry goes inside the `sub_menu_options` array of an existing `nav_dropdown` menu group, or create a new menu group:

```json
{
    "title": "Menu Group Title",
    "location": "top_menu",
    "type": "nav_dropdown",
    "sec_group": "users",
    "sub_menu_options": [
        {
            "type": "editor",
            "sec_group": "users",
            "title": "Display Title",
            "element": "ComponentName_EditorData"
        }
    ]
}
```

### 4c. endpoints.json — API endpoints

Add an endpoint entry for the master component. For child components, only add an endpoint if `subType` is `"table"` (separate table storage). When `subType` is `"array"`, the child data lives inside the parent document and no separate endpoint is needed.

```json
{
    "name": "<dbApiUrl>",
    "url_prefix": "<dbApiUrl>",
    "routes": [
        {
            "endpoint": "/",
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "handler_type": "GenericEndpointHelper",
            "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
            "params": {
                "json_file": "<entity_config_name>"
            }
        }
    ]
}
```

### 4d. app_constants.jsx — new constants (if any)

If the JSON config references constants not yet in `app_constants.jsx`, provide the code to add them:

```json
// Add to src/configs/frontend/app_constants.json:
"NEW_CONSTANT": {
    "value1": "Label 1",
    "value2": "Label 2"
}
```

```jsx
// Add to src/constants/app_constants.jsx:
export const NEW_CONSTANT = buildConstant(constants.NEW_CONSTANT);
```

## Step 5 — Summary

After generating everything, present a summary:

1. **Files created** — list every JSX file with its full path
2. **Integration snippets** — recap what needs to be added to App.jsx, menu, endpoints, and constants
3. **Formula functions** — if any `formula` fields were found, remind the user they need to implement the formula functions and register them in `componentMap`
4. **Lifecycle hooks** — if the JSON config has `dbListPreRead`, `dbPreWrite`, `validations`, or similar hook arrays, remind the user they need to implement those functions and register them in `componentMap`
5. **Test** — remind to run the dev server to verify the new components work
