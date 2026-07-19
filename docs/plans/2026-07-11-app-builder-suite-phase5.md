# GenericSuite App-Builder Skill Suite — Phase 5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `gs-app-builder` — the "build me an app" orchestrator that detects greenfield vs. brownfield, interviews the user into a shared app brief, and drives the nine specialized suite skills in the design's flow order (steps 0–9) with a checkpoint after each phase — per `docs/design/2026-07-09-app-builder-skill-suite-design.md` §"#### 9. gs-app-builder (orchestrator)".

**Architecture:** The orchestrator is a pure SKILL.md instruction flow: it never generates project files itself — every artifact comes from invoking a sibling skill by name (the invoked skill's SKILL.md is read and followed exactly). It holds the app brief so later skills never re-ask questions. No `references/` sync this phase: the orchestrator's grounding IS the sibling skills.

**Tech Stack:** Markdown SKILL.md, evals.json, Python 3 stdlib + bash for grading.

**Working directory for ALL tasks:** `/Users/carlosramirez/desarrollo/genericsuite/packages/genericsuite-skills`.

## Global Constraints

- **Commits:** per-task commits on branch `feature/GS-254-phase5`; the user merges/pushes manually afterward. Never commit `__pycache__`/`.pyc` or transient `playground/gs-app-builder-test/` outputs (`playground/.gitignore` ignores everything except `gs-billing-app/`).
- New skill: `SKILL.md` frontmatter with `name`, `description` (~100 words max), `argument-hint` (quoted — bracketed hints are invalid YAML unquoted); registered in `.claude-plugin/marketplace.json` (`code-generation-skills`, alphabetical); row in `CLAUDE.md` "Skills in this Repository" table (alphabetical); `evals/evals.json` with ≥2 cases including at least one runtime-validity assertion.
- **Flow steps 0–9 verbatim from the design doc**, including step 0's three probes (`config_dbdef/` present; `genericsuite`/`genericsuite-ai` in the Python deps; `componentMap` in the frontend App.jsx) and the foreign-code STOP (point at the `gs-adopt` gap — never scaffold on top of non-GenericSuite code).
- **Skills never write secrets** — env-var placeholders only.
- **Evals run offline**: no GitHub clone, no `make install-all`, no dev servers. Scaffolding uses the local basecamp checkout at `../genericsuite-basecamp`. Eval runs skip checkpoint pauses (act autonomously).
- Tracked `playground/gs-billing-app/` must never be modified by eval runs — brownfield eval works on a copy under `playground/gs-app-builder-test/`.
- Commit message style: `Add:`/`Change:`/`Fix:` prefix + `[GS-254]`.
- `quick_validate` must exit 0 for the new skill.

---

### Task 1: `gs-app-builder` skill + evals + registration

**Files:**
- Create: `skills/gs-app-builder/SKILL.md`
- Create: `skills/gs-app-builder/evals/evals.json`
- Modify: `.claude-plugin/marketplace.json`, `CLAUDE.md`

**Interfaces:**
- Consumes: the nine sibling skills by name (`app-starter`, `config-builder`, `menu-builder`, `endpoints-builder`, `jsx-code-builder`, `python-fastapi-code-builder`, `python-ai-code-builder`, `python-ai-tools-code-builder`, `jsx-ai-code-builder`, `mcp-builder`) — invoked, not duplicated.
- Produces: the skill, invoked as `/gs-app-builder [target-dir] [app-description]`. Task 2's evals execute it.

- [ ] **Step 1: Write `skills/gs-app-builder/SKILL.md`**

````markdown
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
````

- [ ] **Step 2: Write `skills/gs-app-builder/evals/evals.json`**

```json
{
  "skill_name": "gs-app-builder",
  "evals": [
    {
      "id": 1,
      "prompt": "Build me a small GenericSuite invoicing app named 'invoicehub' with domain 'invoicehub.io' in playground/gs-app-builder-test/eval-1/invoicehub. App brief (answer the interview from this, do not ask me): entities are customers (name:text, email:email, active:boolean — master) and invoices (invoice_number:text, customer_id:select from customers, total:number — master, with child invoice_lines: description:text, quantity:number, unit_price:number). No custom endpoints, no AI features, no MCP. Deployment: make run. This is a test run: use the OFFLINE scaffold path from the local basecamp checkout at ../genericsuite-basecamp, do not pause at checkpoints, and do NOT run make install-all or any dev server.",
      "expected_output": "A scaffolded invoicehub app (fresh git repo, renamed from fastapitemplate) whose config_dbdef holds customers/invoices/invoice_lines configs, whose menu and endpoints register the two masters, and whose ui/src/components holds the generated Customers and Invoices JSX registered in componentMap — produced by driving app-starter, config-builder, menu-builder, endpoints-builder and jsx-code-builder in order, with a printed checkpoint after each phase",
      "files": [],
      "expectations": [
        "Mode detection reported greenfield and an App brief block was shown before any files were generated",
        "The scaffold at playground/gs-app-builder-test/eval-1/invoicehub is a fresh git repo with the fastapitemplate layout fully renamed to invoicehub/invoicehub.io (no occurrence of 'fastapitemplate' in package.json, server/pyproject.toml or .env.example)",
        "config_dbdef/frontend and config_dbdef/backend each contain customers.json, invoices.json and invoice_lines.json, and every one of them parses as valid JSON (runtime validity)",
        "config_dbdef/backend/app_main_menu.json contains menu entries whose element values are Customers_EditorData and Invoices_EditorData, and config_dbdef/backend/endpoints.json registers url_prefix 'customers' and 'invoices' but has NO endpoint entry for invoice_lines (children live inside the parent document)",
        "Customers.jsx and Invoices.jsx exist under ui/src/components/<MenuGroup>/ (jsx-code-builder's menu-group folder convention) and App.jsx's componentMap references Customers_EditorData and Invoices_EditorData (runtime validity: the menu elements resolve to real components)",
        "No secrets were written: .env (if created by init-app-environment) still has APP_SECRET_KEY=xxxx, and make install-all / dev servers were never run",
        "A checkpoint summary (files created/changed) was printed after each phase"
      ]
    },
    {
      "id": 2,
      "prompt": "First copy playground/gs-billing-app to playground/gs-app-builder-test/eval-2/gs-billing-app (do not touch the original). Then run the gs-app-builder flow against playground/gs-app-builder-test/eval-2/gs-billing-app: I want to add a payment_methods entity (name:text, type:select with options card/transfer/cash, active:boolean — master, no children). Backend registration only — skip frontend JSX, AI and MCP phases. This is a test run: do not pause at checkpoints, no network, no installs.",
      "expected_output": "Brownfield mode detected on the copy (config_dbdef/ probe), existing entities/menu/endpoints inventoried, NO scaffolding, then payment_methods configs generated and merged idempotently into app_main_menu.json and endpoints.json with every pre-existing entry preserved",
      "files": [],
      "expectations": [
        "Mode detection reported brownfield (existing GenericSuite project) and an inventory of existing entities, menu entries and endpoints was shown; the interview was framed additively",
        "app-starter was NOT invoked: no ui/, Makefile or scaffold files were created in the copy",
        "config_dbdef/frontend/payment_methods.json and config_dbdef/backend/payment_methods.json exist and parse as valid JSON (runtime validity)",
        "config_dbdef/backend/app_main_menu.json gained a PaymentMethods_EditorData entry AND still contains every pre-existing entry (e.g. Invoices_EditorData); config_dbdef/backend/endpoints.json gained url_prefix 'payment_methods' AND still contains 'invoices' (idempotent merge, nothing rewritten)",
        "The tracked playground/gs-billing-app original was not modified (git status clean for that path)"
      ]
    },
    {
      "id": 3,
      "prompt": "Set up a fixture first: create playground/gs-app-builder-test/eval-3/legacyshop containing EXACTLY two files — package.json ({\"name\": \"legacyshop\", \"version\": \"1.0.0\", \"main\": \"src/index.js\"}) and src/index.js (a minimal plain Express hello-world). Then run the gs-app-builder flow against playground/gs-app-builder-test/eval-3/legacyshop asking to 'build an orders management app here'. This is a test run: no network, no installs.",
      "expected_output": "The orchestrator detects an existing NON-GenericSuite codebase, STOPS without scaffolding or modifying anything, explains that retrofitting GenericSuite into foreign code (gs-adopt) is a known gap rather than a shipped skill, and offers to build in a fresh directory instead",
      "files": [],
      "expectations": [
        "Mode detection ran the three probes (config_dbdef/, genericsuite Python deps, componentMap) and reported none matched",
        "The flow STOPPED before any interview/scaffold phase: legacyshop still contains exactly the two fixture files, no config_dbdef/, server/ or ui/ was created, and neither fixture file was modified",
        "The response mentions the gs-adopt gap (adopting GenericSuite into existing non-GenericSuite code is not yet supported) and offers a fresh-directory alternative"
      ]
    }
  ]
}
```

- [ ] **Step 3: Register in `.claude-plugin/marketplace.json`**

In the `code-generation-skills` plugin's `skills` array, insert
`"./skills/gs-app-builder",` immediately after
`"./skills/endpoints-builder",` (alphabetical order). No other changes.

- [ ] **Step 4: Add the `CLAUDE.md` table row**

In the "Skills in this Repository" table, insert this row immediately
after the `skills/endpoints-builder/` row (alphabetical order):

```markdown
| `skills/gs-app-builder/` | Orchestrates the whole app-builder suite: mode detection (greenfield/brownfield), app-brief interview, then drives app-starter → config-builder → menu/endpoints-builder → jsx-code-builder → custom/AI/MCP builders with checkpoints |
```

- [ ] **Step 5: Validate**

Run:
```bash
(cd skills/skill-creator && python3 -m scripts.quick_validate ../../skills/gs-app-builder)
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); json.load(open('skills/gs-app-builder/evals/evals.json')); print('JSON OK')"
python3 -c "import yaml,pathlib; t=pathlib.Path('skills/gs-app-builder/SKILL.md').read_text().split('---')[1]; d=yaml.safe_load(t); assert set(d)=={'name','description','argument-hint'}, d.keys(); print('frontmatter OK')" 2>/dev/null || python3 - <<'EOF'
# fallback if PyYAML missing: check the three keys exist as lines
import pathlib
fm = pathlib.Path('skills/gs-app-builder/SKILL.md').read_text().split('---')[1]
for k in ('name:', 'description:', 'argument-hint:'):
    assert any(l.startswith(k) for l in fm.splitlines()), k
print('frontmatter OK')
EOF
```
Expected: quick_validate exit 0; `JSON OK`; `frontmatter OK`.

- [ ] **Step 6: Commit**

```bash
git add skills/gs-app-builder .claude-plugin/marketplace.json CLAUDE.md
git commit -m "Add: gs-app-builder orchestrator skill — mode detection, app brief, suite flow with checkpoints, evals [GS-254]"
```

---

### Task 2: Eval smoke run + mechanical grading

**Files:**
- Create (transient, NOT committed — `playground/.gitignore` covers it): `playground/gs-app-builder-test/`

**Interfaces:**
- Consumes: Task 1's skill and evals; the sibling skills' SKILL.md files; the local basecamp checkout `../genericsuite-basecamp`; tracked `playground/gs-billing-app/` (read/copy only).
- Produces: pass/fail evidence appended to `.superpowers/sdd/progress.md`; fixes (if any) committed.

- [ ] **Step 1: Execute the three eval prompts with the skill loaded**

Dispatch one subagent per eval: prompt = the eval's `prompt` verbatim, prefixed with "Read and follow skills/gs-app-builder/SKILL.md exactly (it will direct you to read other skills/*/SKILL.md files — do so). Work from /Users/carlosramirez/desarrollo/genericsuite/packages/genericsuite-skills.". Rules for the subagents: act autonomously; NO git commands in the skills repo itself (git inside the scaffolded playground app is required and expected); no network (offline scaffold path only); never commit `__pycache__`/`.pyc`; never modify tracked `playground/gs-billing-app/`. The three evals are independent (separate output dirs) and may run in parallel. Eval 1 is the long one (full greenfield chain) — expect it to take the longest.

- [ ] **Step 2: Grade mechanically**

```bash
set -u
E1=playground/gs-app-builder-test/eval-1/invoicehub
E2=playground/gs-app-builder-test/eval-2/gs-billing-app
E3=playground/gs-app-builder-test/eval-3/legacyshop
fail=0
check() { if eval "$2"; then echo "PASS: $1"; else echo "FAIL: $1"; fail=1; fi; }

# eval 1 — greenfield end-to-end
check "e1 scaffold layout"     "[ -d $E1/ui ] && [ -d $E1/server ] && [ -d $E1/config_dbdef ] && [ -f $E1/Makefile ]"
check "e1 fresh repo"          "git -C $E1 rev-list --count HEAD >/dev/null 2>&1"
check "e1 renamed"             "! grep -qi fastapitemplate $E1/package.json $E1/server/pyproject.toml $E1/.env.example"
check "e1 entity configs"      "python3 -c \"import json;[json.load(open(f'$E1/config_dbdef/{s}/{e}.json')) for s in ('frontend','backend') for e in ('customers','invoices','invoice_lines')]\""
check "e1 menu entries"        "grep -q Customers_EditorData $E1/config_dbdef/backend/app_main_menu.json && grep -q Invoices_EditorData $E1/config_dbdef/backend/app_main_menu.json"
check "e1 endpoints"           "python3 -c \"import json;p=[e['url_prefix'] for e in json.load(open('$E1/config_dbdef/backend/endpoints.json'))];assert 'customers' in p and 'invoices' in p and 'invoice_lines' not in p,p\""
check "e1 jsx components"      "[ -n \"\$(find $E1/ui/src/components -name Customers.jsx)\" ] && [ -n \"\$(find $E1/ui/src/components -name Invoices.jsx)\" ]"
check "e1 componentMap wired"  "grep -q Customers_EditorData $E1/ui/src/components/App/App.jsx && grep -q Invoices_EditorData $E1/ui/src/components/App/App.jsx"
check "e1 no secrets written"  "[ ! -f $E1/.env ] || grep -q '^APP_SECRET_KEY=xxxx$' $E1/.env"
check "e1 no installs"         "[ ! -d $E1/node_modules ] && [ ! -d $E1/ui/node_modules ] && [ ! -d $E1/server/.venv ]"

# eval 2 — brownfield additive
check "e2 no scaffold"         "[ ! -d $E2/ui ] && [ ! -f $E2/Makefile ]"
check "e2 new configs"         "python3 -c \"import json;[json.load(open(f'$E2/config_dbdef/{s}/payment_methods.json')) for s in ('frontend','backend')]\""
check "e2 menu merged"         "grep -q PaymentMethods_EditorData $E2/config_dbdef/backend/app_main_menu.json && grep -q Invoices_EditorData $E2/config_dbdef/backend/app_main_menu.json"
check "e2 endpoints merged"    "python3 -c \"import json;p=[e['url_prefix'] for e in json.load(open('$E2/config_dbdef/backend/endpoints.json'))];assert 'payment_methods' in p and 'invoices' in p,p\""
check "e2 original untouched"  "[ -z \"\$(git status --porcelain playground/gs-billing-app)\" ]"

# eval 3 — foreign-code STOP
check "e3 fixture intact"      "[ \"\$(find $E3 -type f | wc -l | tr -d ' ')\" = 2 ] && [ -f $E3/package.json ] && [ -f $E3/src/index.js ]"
check "e3 nothing scaffolded"  "[ ! -d $E3/config_dbdef ] && [ ! -d $E3/server ] && [ ! -d $E3/ui ]"

# hygiene
check "no pycache"             "! find playground/gs-app-builder-test -name __pycache__ -o -name '*.pyc' 2>/dev/null | grep -q ."
check "nothing staged"         "git status --porcelain | grep -v '^??' | wc -l | grep -qx ' *0'"
exit $fail
```

Expected: all `PASS`, exit 0. The subjective expectations (brief shown before generation, checkpoint summaries printed, brownfield inventory shown, gs-adopt wording) are graded by reading each subagent's final report against the eval's `expectations` list.

- [ ] **Step 3: One fix wave if needed, then record**

If any check fails or a subjective expectation is unmet: ONE fix commit to the skill (`Fix: gs-app-builder <what> [GS-254]`), purge and re-run only the failed eval(s), re-grade. Then append the task results to `.superpowers/sdd/progress.md` (same format as Phases 0–4).

---

## Self-Review Notes

- Design-doc coverage (§9): flow steps 0–9 all present in the SKILL.md (Step 0 mode detection with the three probes, brownfield additive framing + skill-support note, foreign-code STOP → gs-adopt ✔; Step 1 interview items purpose/entities/relationships/AI/deployment plus custom endpoints from flow step 6 ✔; Steps 2–8 invoke the named skills in the design's order ✔; Step 9 checklist env vars / make dev / smoke test ✔); checkpoints after each phase ✔; shared app brief so skills don't re-ask ✔; orchestrator invokes skills by name, generates nothing itself ✔; exercised end-to-end in playground on an invoices domain ✔ (eval 1).
- `endpoints.json` in both the template and gs-billing-app is a top-level JSON array — the grading's `json.load(...)` list comprehension matches that shape.
- Eval 2 works on a COPY of gs-billing-app because the original is tracked; the "original untouched" check enforces it.
- Eval 1's componentMap check targets `ui/src/components/App/App.jsx` — verified as the App.jsx location in the fastapitemplate scaffold.
- `Customers_EditorData` naming verified against menu-builder's SKILL.md (element convention) and jsx-code-builder's generated exports.
- Eval-1 grading avoids asserting an exact commit count in the scaffolded repo: app-starter makes 2 commits, but later phases legitimately leave uncommitted changes or extra commits — only repo validity is asserted; rename completeness is the runtime-validity anchor.
