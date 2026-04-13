---
name: config-builder
description: Build GenericSuite JSON configuration files (frontend + backend) for a new CRUD editor, table, form, or child listing. Use when the user wants to create or scaffold new config_dbdef JSON files following the GenericSuite configuration guide.
argument-hint: [entity-name]
---

Build GenericSuite `config_dbdef` JSON configuration files following the guidelines in:
- `gs_docs/en/Configuration-Guide/index.md`
- `gs_docs/en/Configuration-Guide/Generic-CRUD-Editor-Configuration.md`
- `gs_docs/code/configuration-guide/crud_editor_config_classes.py` (Pydantic validation schema for frontend/backend JSON configs)

## Step 1 — Gather requirements

Ask the user the following questions (can be answered all at once):

1. **Entity name**: What is the entity? (e.g. "Invoice", "Product", "Order Line")
2. **Table name**: What is the physical database table name? (e.g. `invoices`)
3. **Endpoint URL**: What API endpoint URL? (defaults to table name)
4. **React component name**: PascalCase component name (e.g. `Invoices`)
5. **Relationship type**: Is this a **master** (top-level) editor or a **child** (1-to-many) listing?
   - If child: what is the parent table/URL? Is the relationship `array` (same table) or `table` (separate table)?
6. **Fields**: List each field with:
   - `name` (snake_case)
   - `label` (display name)
   - `type` (see types below)
   - `required` (yes/no)
   - `listing` (show in list page? yes/no)
   - `readonly` (yes/no)
   - Any default value?
7. **Child components**: Does this master editor have child listings? (list component names)
8. **Mandatory filters**: Should results be filtered (e.g. by `user_id`)?
9. **Default sort order**: Which field and direction? (e.g. `name|asc`, `update_date|desc`)
10. **Backend extras**: primary key for creation duplicate check (`creation_pk_name`), fields to exclude from results (`projection_exclusion`), password fields, email fields, mandatory DB fields?
11. **Specific function**: Any backend-specific function? (e.g. `delete_params_file`)

## Field types reference

| Type | Description |
|---|---|
| `text` | Single-line text input |
| `textarea` | Multi-line text input |
| `number` | Float number |
| `integer` | Integer number |
| `date` | Date only |
| `datetime-local` | Date + time |
| `email` | Email with validation |
| `select` | Dropdown from a constant list (`select_elements` required) |
| `select_table` | Dropdown from related table |
| `select_component` | Dropdown from React component |
| `suggestion_dropdown` | Autocomplete from API call |
| `_id` | Hidden primary key field |
| `array` | Multi-dimensional array / JSON object |
| `component` | Value rendered by a React component |
| `label` | Display-only label |
| `h1`–`h6` | Heading |
| `hr` | Horizontal rule |

Special field attributes:
- `chatbot_popup: true` + `chatbot_prompt` — adds AI assistant button
- `google_popup: true` + `google_prompt` — adds Google search button
- `formula` — JS function name to compute value from other fields
- `uuid_generator: true` — auto-generate UUID on creation
- `default_value: "current_timestamp"` — auto-fill current date/time

## Step 2 — Generate the files

Before generating, read `gs_docs/code/configuration-guide/crud_editor_config_classes.py` to understand the valid field types, attributes, and config structure. Validate your generated JSON against the `FrontendCrudEditorConfig` and `BackendCrudEditorConfig` Pydantic models defined there.

Based on the answers, generate these files under `docs/code/exampleapp/apps/config_dbdef/` (or the path the user specifies):

### `frontend/<entity>.json`

```json
{
    "baseUrl": "<endpoint_url>",
    "title": "<Entity plural display name>",
    "name": "<Entity singular display name>",
    "component": "<ComponentName>",
    "dbApiUrl": "<endpoint_url>",
    // if mandatory filters:
    "mandatoryFilters": { "user_id": "{CurrentUserId}" },
    // if default order:
    "defaultOrder": "<field>|<asc|desc>",
    // if child listing:
    "type": "child_listing",
    "subType": "<array|table>",
    "array_name": "<array_attribute>",
    "parentUrl": "<parent_endpoint>",
    "endpointKeyNames": [
        { "parameterName": "<fk_param>", "parentElementName": "<parent_pk>" }
    ],
    "primaryKeyName": "id",
    // if has child components:
    "childComponents": ["<ChildComponent>"],
    "fieldElements": [ /* generated from field list */ ]
}
```

Standard fields to always include at top of `fieldElements`:
```json
{ "name": "id", "required": true, "label": "ID", "type": "_id", "readonly": true, "hidden": true },
{ "name": "user_id", "required": true, "label": "User ID", "type": "text", "readonly": true, "hidden": true }
```

Standard timestamp fields to include at the bottom:
```json
{ "name": "creation_date", "required": true, "label": "Created", "type": "datetime-local", "readonly": true, "hidden": false, "default_value": "current_timestamp", "listing": true },
{ "name": "update_date", "required": true, "label": "Last update", "type": "datetime-local", "readonly": true, "hidden": false, "default_value": "current_timestamp", "listing": false }
```

### `backend/<entity>.json`

```json
{
    "table_name": "<physical_table_name>",
    // optional:
    "notes": "<description>",
    "creation_pk_name": "<unique_field>",
    "projection_exclusion": ["<field_to_hide>"],
    "email_verification": ["email"],
    "passwords": ["passcode"],
    "mandatory_fields": ["field1", "field2"],
    "additional_query_params": ["<searchable_field>"],
    "specific_function": "<function_name>"
}
```

## Step 3 — Show what to do next

After generating the files, remind the user to:

1. Add the React component to `App.jsx`'s `componentMap`
2. Add the menu entry to `backend/app_main_menu.json`
3. Add the API endpoint to `backend/endpoints.json` using this pattern:
   ```json
   {
       "name": "<endpoint_url>",
       "url_prefix": "<endpoint_url>",
       "routes": [{
           "endpoint": "/",
           "methods": ["GET", "POST", "PUT", "DELETE"],
           "handler_type": "GenericEndpointHelper",
           "view_func": "lib.util.generic_endpoint_builder.generic_route_handler",
           "params": { "json_file": "<entity>" }
       }]
   }
   ```
4. Create the React component file `src/components/<ComponentName>/<ComponentName>.jsx`
5. Run `make exampleapp-run` to test

> **Tip:** Use the `jsx-code-builder` skill to automatically generate the React component files (step 4) from the JSON configs you just created. Just say `/jsx-code-builder` and point it at the generated frontend JSON file.
