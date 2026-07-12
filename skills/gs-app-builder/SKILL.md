---
name: gs-app-builder
description: End-to-end "build me a GenericSuite app" orchestrator. Detects greenfield vs. brownfield, interviews the user into an app brief (purpose, entities and fields, relationships, custom endpoints, AI features, MCP, deployment intent), then drives the specialized suite skills in order — app-starter, config-builder, menu-builder, endpoints-builder, jsx-code-builder, python-fastapi-code-builder, python-ai-code-builder, python-ai-tools-code-builder, jsx-ai-code-builder, mcp-builder — with a checkpoint after each phase. Use when the user wants to build a whole GenericSuite application from a description, or add a batch of entities/features to an existing one, and be driven through the full flow.
argument-hint: "[target-dir] [app-description]"
---

You are the ORCHESTRATOR for the GenericSuite app-builder suite. Rules
that govern the entire flow:

1. **You never generate project files yourself.** Every artifact comes
   from invoking one of the sibling skills by name: READ that skill's
   `skills/<name>/SKILL.md` and follow it exactly, handing it the
   relevant slice of the app brief so it never re-asks a question the
   user already answered.
2. **The app brief is the single source of truth.** Build it in Step 1,
   show it for confirmation, and re-display the (updated) brief at every
   checkpoint.
3. **Checkpoint after each phase:** list the files created or changed in
   that phase and get the user's confirmation before continuing.
   Exception — eval/test runs (output under `playground/`): do not pause
   for confirmation; still print each checkpoint summary.
4. **Inherit every sibling skill's hard constraints**: greenfield-only
   for app-starter, never write secrets (env placeholders only),
   idempotent JSON merges, standard backend result shape. In eval/test
   runs also inherit the suite eval conventions: offline scaffold from
   the local basecamp checkout, no `make install-all`, no dev servers,
   no network.

## Step 0 — Mode detection

Resolve the target directory (ask if not given). Three cases:

- **Greenfield** — the directory does not exist (or is empty): the full
  flow applies, including Step 2.
- **Brownfield GenericSuite** — the directory has content AND any of
  these probes hits:
  1. a `config_dbdef/` directory (project root or `server/`);
  2. `genericsuite` or `genericsuite-ai` in the Python deps
     (`pyproject.toml` or `requirements.txt`, root or `server/`);
  3. a `componentMap` in the frontend's App.jsx (search `ui/src/` or
     `src/`).
  Then SKIP Step 2 (never scaffold), inventory what exists — entities
  (`config_dbdef/frontend/*.json` + `backend/*.json`), menu
  (`app_main_menu.json`), endpoints (`endpoints.json`), AI wiring
  (`ai_gpt_fn_index.py`, ai_assistant router), MCP server (`mcp-server/`
  or `mcplib` usage) — show the inventory, and frame the Step 1
  interview additively: "what do you want to add?" instead of "what app
  do you want to build?". The sibling skills already support this mode:
  menu-builder and endpoints-builder merge idempotently,
  python-ai-code-builder preserves a populated index,
  python-ai-tools-code-builder skips existing registrations, and
  mcp-builder has EXTEND mode.
- **Foreign code** — the directory has content and NO probe hits: STOP.
  Tell the user this looks like an existing non-GenericSuite codebase;
  retrofitting GenericSuite into foreign code (`gs-adopt`) is a known
  gap, not a shipped skill. Do NOT scaffold on top of it and do NOT
  modify anything in it. Offer to build in a fresh directory instead.

## Step 1 — Interview → app brief

Ask (greenfield framing, or additive framing in brownfield mode — only
what the arguments and conversation haven't already answered):

1. App purpose (one sentence), app name, domain (greenfield only —
   these feed app-starter).
2. Entities: names, fields with types, which are master editors and
   which are children of a master (child = `subType: "array"` inside
   the parent document).
3. Custom non-CRUD endpoints (wrapping an external API, computed or
   aggregate results, custom actions)? For each: name and behavior.
4. AI features: chatbot/assistant? App-specific AI tools — which
   actions should the assistant perform?
5. MCP server exposing those tools (and which CRUD entities, if any)?
6. Deployment intent: local Docker MongoDB (`make run`) vs. remote DB
   (`make dev`) — this shapes the final checklist only.

Record the answers in a fenced **App brief** block:

```
App brief
- mode: greenfield | brownfield
- target dir / app name / domain: ...
- entities: <name> (field:type, ...) [master | child of <parent>]
- custom endpoints: <name> — <behavior> | none
- AI: chatbot yes/no; tools: <name> — <action>, ... | none
- MCP: yes/no (+ which CRUD entities to expose)
- deployment: make run (local Docker) | make dev (remote DB)
```

Show it and get confirmation before Phase 2.

## Step 2 — Scaffold (greenfield only)

Invoke **app-starter** with the target dir, app name, and domain from
the brief. Run it through scaffold, `make init-app-environment`, and its
`.env` checklist; DEFER its `make install-all` and first-run steps to
Step 9 (mention that to the user). Checkpoint.

## Step 3 — Entity configs

For each entity in the brief — masters first, then their children —
invoke **config-builder**. Checkpoint: list the generated
`config_dbdef/frontend/*.json` and `config_dbdef/backend/*.json` files.

## Step 4 — Register menus and endpoints

Invoke **menu-builder** for each new master component, then
**endpoints-builder** for each master entity (it skips
`subType: "array"` children automatically — children live inside the
parent document). Checkpoint.

## Step 5 — Frontend components

Invoke **jsx-code-builder** once per master frontend config (it batch-
generates the master and all its children, and registers the
`<ComponentName>_EditorData` entries in App.jsx's `componentMap`).
Checkpoint.

## Step 6 — Custom endpoints (only if the brief lists any)

For each custom endpoint: invoke **python-fastapi-code-builder**, then
**endpoints-builder** (and **menu-builder** if it has a UI page) for its
wiring. Checkpoint.

## Step 7 — AI (only if the brief says yes)

In this order — each depends on the previous one's output:

1. **python-ai-code-builder** — assistant router + skeleton
   GPT-functions index + env checklist.
2. **python-ai-tools-code-builder** — one pass listing every tool from
   the brief (generates the `@tool`/`*_func` pairs and registers them
   in `ai_gpt_fn_index.py`).
3. **jsx-ai-code-builder** — chatbot page + menu entry, per-field chat
   buttons where configs carry `chatbot_popup`, genericsuite-ai App
   shell migration.

Checkpoint.

## Step 8 — MCP (only if the brief says yes)

Invoke **mcp-builder** — it wraps the `*_func` companions from Step 7
and the CRUD entities the brief selected. Checkpoint.

## Step 9 — Final checklist

Close with a numbered handoff (do not run installs or servers in
eval/test runs):

1. `.env` recap: the required vars from app-starter's checklist, plus
   the AI vars (e.g. `OPENAI_API_KEY`) if Step 7 ran, plus any vars the
   custom endpoints or MCP server introduced. Placeholders still in
   place — the user fills real values themselves.
2. `make install-all`, then `make dev` (remote DB) or `make run` (local
   Docker MongoDB) per the brief's deployment intent.
3. Smoke test: log in as the superadmin, open each new menu entry, CRUD
   one record per entity, and — if AI — ask the chatbot to use one of
   the new tools.
4. Greenfield: push to their own remote
   (`git remote add origin <url> && git push -u origin main`).
