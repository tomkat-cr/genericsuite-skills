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
