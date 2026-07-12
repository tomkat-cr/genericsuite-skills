# GenericSuite App-Builder Skill Suite — Phase 4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `app-starter` — the skill that bootstraps a new GenericSuite application from the basecamp `fastapitemplate` monorepo (React `ui/`, FastAPI `server/`, MCP server) and guides the user through environment init, the required-`.env`-vars checklist, dependency install, and first run — per `docs/design/2026-07-09-app-builder-skill-suite-design.md` §"#### 8. app-starter".

**Architecture:** Same shape as Phases 1–3: one skill directory with SKILL.md + synced `references/` exemplars + `evals/evals.json` + registration. The skill wraps basecamp's `scripts/new-project-from-template.sh` (network path) and documents an equivalent offline path from a local basecamp checkout (used by the evals). Greenfield only; a "template" question is reserved in the flow for GS-306 (exampleapp with framework selection) without building it.

**Tech Stack:** Markdown SKILL.md, bash exemplars from basecamp (`new-project-from-template.sh`, `rename-app.sh`, `init_app_environment.sh`), Python 3 stdlib for grading.

**Working directory for ALL tasks:** `/Users/carlosramirez/desarrollo/genericsuite/packages/genericsuite-skills`.

## Global Constraints

- **Commits:** per-task commits on branch `feature/GS-254-phase4`; the user merges/pushes manually afterward. Never commit `__pycache__`/`.pyc` or transient `playground/app-starter-test/` outputs (`playground/.gitignore` already ignores everything except `gs-billing-app/`).
- New skill: `SKILL.md` frontmatter with `name`, `description` (~100 words max), `argument-hint`; registered in `.claude-plugin/marketplace.json` (`code-generation-skills`, alphabetical); row in `CLAUDE.md` "Skills in this Repository" table (alphabetical); `evals/evals.json` with ≥2 cases.
- Eval expectations must include at least one runtime-validity assertion (here: the rename actually completed in the files the app boots from, and `make init-app-environment` actually produced a usable `.env`), not just structure checks.
- **Skills never write secrets** — env-var placeholders only; the skill may write values the user explicitly supplied in chat that are not secrets (e.g. their admin email), never keys or passwords.
- **Evals run offline**: no GitHub clone, no `make install-all`, no `make dev`/`make run`. Scaffolding uses the local basecamp checkout at `../genericsuite-basecamp` (relative to this repo root).
- Commit message style: `Add:`/`Change:`/`Fix:` prefix + `[GS-254]`.
- `quick_validate` must exit 0 for the new skill.
- Reference files are created by `make sync-references` / the map — never hand-authored.

---

### Task 1: Phase-4 reference seeding

**Files:**
- Modify: `skills/update-gs-docs/reference_map.txt` (append Phase-4 block)
- Created by sync: `skills/app-starter/references/**`

**Interfaces:**
- Consumes: `BASECAMP_DIR=../genericsuite-basecamp bash skills/update-gs-docs/scripts/update-gs-docs.sh` (Phase 1 mechanism).
- Produces: the five reference files below at exactly these paths — Task 2's SKILL.md cites them verbatim.

- [ ] **Step 1: Append to `skills/update-gs-docs/reference_map.txt`**

```
# app-starter
scripts/new-project-from-template.sh|skills/app-starter/references/new-project-from-template.sh
scripts/rename-app.sh|skills/app-starter/references/rename-app.sh
mkdocs_root/code/fastapitemplate/scripts/init_app_environment.sh|skills/app-starter/references/init_app_environment.sh
mkdocs_root/code/fastapitemplate/README.md|skills/app-starter/references/fastapitemplate-README.md
mkdocs_root/code/fastapitemplate/.env.example|skills/app-starter/references/fastapitemplate.env.example
```

(Append at the end of the file, after the `# jsx-ai-code-builder` block, preserving the existing blocks byte-for-byte.)

- [ ] **Step 2: Run the sync**

Run: `BASECAMP_DIR=../genericsuite-basecamp bash skills/update-gs-docs/scripts/update-gs-docs.sh`
Expected: `CHANGED:` for the 5 new destinations; `0 failed`; everything else unchanged.

- [ ] **Step 3: Verify byte-identity**

Run:
```bash
while IFS='|' read -r src dest; do
    case "${src}" in \#*|"") continue ;; esac
    cmp "../genericsuite-basecamp/${src}" "${dest}" || echo "MISMATCH: ${dest}"
done < skills/update-gs-docs/reference_map.txt; echo "verify done"
bash -n skills/app-starter/references/new-project-from-template.sh && bash -n skills/app-starter/references/rename-app.sh && bash -n skills/app-starter/references/init_app_environment.sh && echo "syntax OK"
```
Expected: `verify done` with no MISMATCH lines; `syntax OK`.

- [ ] **Step 4: Commit**

```bash
git add skills/update-gs-docs/reference_map.txt skills/app-starter
git commit -m "Add: Phase-4 reference seeding for app-starter [GS-254]"
```

---

### Task 2: `app-starter` skill + evals + registration

**Files:**
- Create: `skills/app-starter/SKILL.md`
- Create: `skills/app-starter/evals/evals.json`
- Modify: `.claude-plugin/marketplace.json`, `CLAUDE.md`

**Interfaces:**
- Consumes: `skills/app-starter/references/**` (Task 1).
- Produces: the skill, invoked as `/app-starter [target-dir] [app-name] [domain]`. Phase 5's orchestrator will invoke it by name at flow step 2 (greenfield only).

- [ ] **Step 1: Write `skills/app-starter/SKILL.md`**

````markdown
---
name: app-starter
description: Bootstrap a brand-new GenericSuite application from the basecamp fastapitemplate — a full-stack monorepo with React frontend (ui/), FastAPI backend (server/), MCP server, and JSON-driven config_dbdef. Scaffolds via basecamp's new-project-from-template.sh (or a local basecamp checkout), renames the app, then guides through make init-app-environment, the required .env variables checklist, make install-all, and the first make dev / make run. Use when the user wants to start, create, scaffold, or bootstrap a new GenericSuite project. Greenfield only — never run it on an existing directory.
argument-hint: [target-dir] [app-name] [domain]
---

Bootstrap a new GenericSuite app, following the canonical machinery
bundled under `references/`:

- `references/new-project-from-template.sh` — basecamp's scaffold script
  (clone → copy template → git init → rename)
- `references/rename-app.sh` — the rename engine it delegates to
- `references/init_app_environment.sh` — what `make init-app-environment`
  runs (copies `.env.example` → `.env`)
- `references/fastapitemplate-README.md` — the template's own setup guide
- `references/fastapitemplate.env.example` — the unified root env file
  (single `.env` feeds both `ui/` and `server/` via `make dev`'s
  copy-env-files step)

READ the reference files before acting. Hard constraints:

1. **Greenfield only.** If the target directory already exists, STOP and
   tell the user — never scaffold over existing code. (For adding to an
   existing GenericSuite app, point them at the other suite skills or
   `gs-app-builder`.)
2. **Never write secrets.** The `.env` keeps its placeholders; you may
   write values the user explicitly typed in chat that are not secrets
   (e.g. `APP_SUPERADMIN_EMAIL`), never API keys, passwords, or
   generated secret values.
3. **Never run network or install commands without telling the user
   first** — scaffolding clones GitHub, `make install-all` downloads
   dependencies. In eval/test runs (output under `playground/`), use the
   offline path and skip install/run entirely.

## Step 1 — Gather inputs

1. **Target directory** — must NOT exist yet (constraint 1). Expand `~`.
2. **App name** — must match `^[a-z0-9][a-z0-9-]*[a-z0-9]$` (lowercase
   letters, digits, hyphens; at least 2 chars). Refuse anything else —
   the rename script enforces the same rule.
3. **Domain** — default `<app-name>.com`.
4. **Template** — today the only option is `fastapitemplate` (React ui/ +
   FastAPI server/ + MCP server in one monorepo). ASK anyway and say:
   "an exampleapp-based template with backend framework selection
   (FastAPI/Flask/Chalice) is planned (GS-306)". If the user asks for
   exampleapp or a specific framework, tell them it isn't available yet
   and proceed with fastapitemplate only if they agree.
5. **Basecamp source** — ask whether to scaffold from GitHub (default,
   needs network) or from a local `genericsuite-basecamp` checkout (offer
   this when one is present nearby, e.g. `../genericsuite-basecamp`).

## Step 2 — Scaffold

### Path A — GitHub (default)

Run basecamp's script with all five args (never rely on its interactive
`/dev/tty` prompts):

```bash
curl -fsSL https://raw.githubusercontent.com/tomkat-cr/genericsuite-basecamp/main/scripts/new-project-from-template.sh -o /tmp/new-project-from-template.sh
bash /tmp/new-project-from-template.sh "<target-dir>" "<app-name>" "<domain>" fastapitemplate main
```

Or, if a local basecamp checkout exists, run the same script from it
(it still shallow-clones GitHub internally):

```bash
bash <basecamp-dir>/scripts/new-project-from-template.sh "<target-dir>" "<app-name>" "<domain>" fastapitemplate main
```

### Path B — offline, from a local basecamp checkout

Replicates exactly what the script does, without the network clone:

```bash
cp -r "<basecamp-dir>/mkdocs_root/code/fastapitemplate" "<target-dir>"
mkdir -p "<target-dir>/scripts"
cp "<basecamp-dir>/scripts/rename-app.sh" "<target-dir>/scripts/rename-app.sh"
cd "<target-dir>"
rm -rf .git
git init --quiet
git add .
git commit --quiet -m "Initial commit from fastapitemplate"
bash scripts/rename-app.sh "<app-name>" "<domain>"
git add .
git commit --quiet -m "Rename: fastapitemplate → <app-name>"
```

### Verify the scaffold (both paths)

```bash
cd "<target-dir>"
ls ui server mcp-server config_dbdef deploy Makefile scripts/rename-app.sh
git log --oneline   # expect exactly 2 commits (initial + rename)
grep -c "APP_NAME=<app-name>" .env.example   # expect 1
! grep -qi fastapitemplate package.json server/pyproject.toml .env.example && echo "rename OK"
```

If any check fails, show the failure and stop — do not continue to a
broken environment.

## Step 3 — Initialize the environment

```bash
cd "<target-dir>"
make init-app-environment
```

This copies `.env.example` → `.env` (and other `*.example` files; it
skips files that already exist). Verify `.env` now exists at the repo
root.

## Step 4 — `.env` checklist (interactive)

Read the generated `.env` and walk the user through the required
variables, grouped by what they want to run. Report which ones still
hold placeholder values (`xxxx`, `openai_api_key`, ...):

**Always required:**

| Var | What it is | How to fill |
|---|---|---|
| `APP_SECRET_KEY` | JWT signing key | user runs `python3 -c "import secrets; print(secrets.token_hex(32))"` and pastes the value in themselves |
| `APP_SUPERADMIN_EMAIL` | first admin login | user's email — you may write it if they told you |

**For `make run` (Docker, DEV stage, local MongoDB):** the defaults
already work — `USE_LOCAL_MONGODB=1` and the prefilled
`APP_DB_*_DEV` values target the docker-compose local MongoDB. Nothing
extra needed.

**For `make dev` (no Docker, QA stage, remote DB):**

| Var | Example |
|---|---|
| `APP_DB_ENGINE_QA` | `MONGODB` (or `DYNAMODB`, `POSTGRES`, `MYSQL`, `SUPABASE`) |
| `APP_DB_NAME_QA` | the database name |
| `APP_DB_URI_QA` | e.g. `mongodb+srv://USER:PASS@CLUSTER.mongodb.net` — user pastes it themselves (contains credentials) |

**For AI features (chatbot/assistant):** `OPENAI_API_KEY` — user pastes
it themselves.

**Defer until deployment** (fine as placeholders for local dev):
`AWS_*`, `APP_CORS_ORIGIN_*` (non-DEV), `APP_FE_URL_*` /
`APP_API_URL_*` (non-DEV), `FLASK_SECRET_KEY` (FastAPI template doesn't
use Flask).

Remind: `make dev` re-copies the root `.env` into `ui/` and `server/`
each run, so the root file is the single source of truth — edit it, not
the copies.

## Step 5 — Install dependencies

Check prerequisites first and report what's missing (do not install
system tools yourself): git, Node.js 18+ with npm, Python 3.12+, `uv`,
Docker (only for `make run`). Then:

```bash
make install-all
```

## Step 6 — First run and handoff

- Remote DB configured → `make dev`
- Docker local DB → `make run` (later: `make down` to stop,
  `make logs-f` to tail)

Then summarize next steps for the user:

1. Frontend at `http://localhost:3000` (`FRONTEND_LOCAL_PORT`), API at
   port `BACKEND_LOCAL_PORT` from `.env`.
2. Push to their own remote: `git remote add origin <url> && git push -u
   origin main`.
3. Add entities with `/config-builder` (then `/menu-builder`,
   `/endpoints-builder`, `/jsx-code-builder`) — or run `/gs-app-builder`
   to be driven through the whole flow.
````

- [ ] **Step 2: Write `skills/app-starter/evals/evals.json`**

```json
{
    "skill_name": "app-starter",
    "evals": [
        {
            "id": 1,
            "prompt": "Scaffold a new GenericSuite app named 'trackerapp' with domain 'trackerapp.io' into playground/app-starter-test/eval-1/trackerapp. This is a test run: use the OFFLINE path from the local basecamp checkout at ../genericsuite-basecamp (do NOT clone from GitHub), and STOP after the scaffold verification step — do not run make init-app-environment, make install-all, or any dev server.",
            "expected_output": "A fresh git repo at playground/app-starter-test/eval-1/trackerapp with the fastapitemplate layout, fully renamed to trackerapp/trackerapp.io, with exactly two commits (initial + rename)",
            "files": [],
            "expectations": [
                "The scaffold directory contains ui/, server/, mcp-server/, config_dbdef/, deploy/, Makefile and scripts/rename-app.sh",
                "It is a fresh git repository with exactly 2 commits and no basecamp history (runtime validity: the repo the user would push is self-contained)",
                "package.json 'name' is 'trackerapp' and contains no occurrence of 'fastapitemplate' (runtime validity: npm workspace boots under the new name)",
                ".env.example contains APP_NAME=trackerapp and APP_DOMAIN_NAME=trackerapp.io and no occurrence of 'fastapitemplate'",
                "server/pyproject.toml contains no occurrence of 'fastapitemplate'",
                "No .env file was created (init-app-environment was not run, as instructed)",
                "The response reports the scaffold verification results and stops without installing dependencies or starting servers"
            ]
        },
        {
            "id": 2,
            "prompt": "I already scaffolded a GenericSuite app at playground/app-starter-test/eval-2/billingstar (if it does not exist, first scaffold it offline from ../genericsuite-basecamp with app name 'billingstar', domain 'billingstar.com'). Now initialize its environment and give me the required .env variables checklist. My admin email is admin@billingstar.com — you can set that one. This is a test run: do NOT run make install-all or any dev server, and do not write any secret values.",
            "expected_output": "make init-app-environment run (root .env created from .env.example), APP_SUPERADMIN_EMAIL set to admin@billingstar.com, and a checklist of remaining required vars grouped by make run vs make dev vs AI, with all secrets left as placeholders",
            "files": [],
            "expectations": [
                "A .env file exists at the app root (runtime validity: make dev's copy-env-files step has a source file to propagate)",
                "APP_SUPERADMIN_EMAIL in .env is admin@billingstar.com (explicit non-secret user-provided value was applied)",
                "APP_SECRET_KEY in .env is still the 'xxxx' placeholder and OPENAI_API_KEY is still the 'openai_api_key' placeholder (no secrets written)",
                "The checklist names APP_SECRET_KEY and suggests the user generate it with a python3 secrets command they run themselves",
                "The checklist explains make run works with the local-MongoDB DEV defaults, while make dev needs APP_DB_ENGINE_QA, APP_DB_NAME_QA and APP_DB_URI_QA",
                "The checklist lists OPENAI_API_KEY as required only for AI features",
                "No dependencies were installed and no server was started"
            ]
        }
    ]
}
```

- [ ] **Step 3: Validate**

Run:
```bash
(cd skills/skill-creator && python3 -m scripts.quick_validate ../../skills/app-starter)
python3 -c "import json; json.load(open('skills/app-starter/evals/evals.json')); print('OK')"
```
Expected: skill valid (exit 0); `OK`.

- [ ] **Step 4: Register the skill**

`.claude-plugin/marketplace.json` — add `"./skills/app-starter"` to the `code-generation-skills` plugin's `skills` array, alphabetical (FIRST entry, before `./skills/config-builder`).

`CLAUDE.md` "Skills in this Repository" table — add in alphabetical position (first row, before `skills/build-agents-md/`):

```markdown
| `skills/app-starter/` | Bootstraps a new GenericSuite app from the basecamp fastapitemplate (scaffold + rename, env init, .env checklist, install, first run) |
```

Run: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('OK')"` → `OK`.

- [ ] **Step 5: Commit**

```bash
git add skills/app-starter .claude-plugin/marketplace.json CLAUDE.md
git commit -m "Add: app-starter skill — new-app bootstrap from fastapitemplate with env checklist, evals [GS-254]"
```

---

### Task 3: Eval smoke run + mechanical grading

**Files:**
- Create (transient, NOT committed — `playground/.gitignore` covers it): `playground/app-starter-test/`

**Interfaces:**
- Consumes: Task 2's skill and evals; the local basecamp checkout `../genericsuite-basecamp`.
- Produces: pass/fail evidence appended to `.superpowers/sdd/progress.md`; fixes (if any) committed.

- [ ] **Step 1: Execute both eval prompts with the skill loaded**

Dispatch one subagent per eval: prompt = the eval's `prompt` verbatim, prefixed with "Read and follow skills/app-starter/SKILL.md exactly. Work from /Users/carlosramirez/desarrollo/genericsuite/packages/genericsuite-skills.". Rules for the subagents: act autonomously; NO git commands in the skills repo itself (git inside the scaffolded playground app is required and expected); no network (offline path only); never commit `__pycache__`/`.pyc`. Eval 2 depends on nothing from eval 1 (it scaffolds its own app), so they may run in parallel.

- [ ] **Step 2: Grade mechanically**

```bash
set -u
E1=playground/app-starter-test/eval-1/trackerapp
E2=playground/app-starter-test/eval-2/billingstar
fail=0
check() { if eval "$2"; then echo "PASS: $1"; else echo "FAIL: $1"; fail=1; fi; }

# eval 1
check "e1 layout"            "[ -d $E1/ui ] && [ -d $E1/server ] && [ -d $E1/mcp-server ] && [ -d $E1/config_dbdef ] && [ -d $E1/deploy ] && [ -f $E1/Makefile ] && [ -f $E1/scripts/rename-app.sh ]"
check "e1 two commits"       "[ \"\$(git -C $E1 rev-list --count HEAD)\" = 2 ]"
check "e1 pkg name renamed"  "python3 -c \"import json;d=json.load(open('$E1/package.json'));assert d['name']=='trackerapp'\" && ! grep -qi fastapitemplate $E1/package.json"
check "e1 env renamed"       "grep -q '^APP_NAME=trackerapp$' $E1/.env.example && grep -q '^APP_DOMAIN_NAME=trackerapp.io$' $E1/.env.example && ! grep -qi fastapitemplate $E1/.env.example"
check "e1 pyproject renamed" "! grep -qi fastapitemplate $E1/server/pyproject.toml"
check "e1 no .env yet"       "[ ! -f $E1/.env ]"

# eval 2
check "e2 .env exists"       "[ -f $E2/.env ]"
check "e2 admin email set"   "grep -q '^APP_SUPERADMIN_EMAIL=admin@billingstar.com$' $E2/.env"
check "e2 secret untouched"  "grep -q '^APP_SECRET_KEY=xxxx$' $E2/.env"
check "e2 openai untouched"  "grep -q '^OPENAI_API_KEY=openai_api_key$' $E2/.env"

# hygiene
check "no pycache"           "! find playground/app-starter-test -name __pycache__ -o -name '*.pyc' | grep -q ."
check "nothing staged"       "git status --porcelain | grep -v '^??' | wc -l | grep -qx ' *0'"
exit $fail
```

Expected: all `PASS`, exit 0. The subjective expectations (checklist wording, stop-before-install behavior) are graded by reading each subagent's final report against the eval's `expectations` list.

- [ ] **Step 3: One fix wave if needed, then record**

If any check fails or a subjective expectation is unmet: ONE fix commit to the skill (`Fix: app-starter <what> [GS-254]`), re-run only the failed eval, re-grade. Then append the task results to `.superpowers/sdd/progress.md` (same format as Phases 0–3).

---

## Self-Review Notes

- Design-doc coverage: gather target dir/app name/domain/template ✔ (Task 2 Step 1, skill Step 1); run new-project-from-template.sh via curl or local clone ✔ (skill Step 2 Path A/B); guide through init-app-environment / .env checklist / install-all / dev-run ✔ (skill Steps 3–6); GS-306 template question reserved ✔ (skill Step 1 item 4); greenfield only ✔ (constraint 1); evals in playground, gitignore-aware, ≥2 cases with runtime-validity assertions ✔ (Task 2 Step 2, Task 3).
- The rename check deliberately targets the three files the rename script's own README table names (package.json, server/pyproject.toml, .env.example) instead of a whole-tree grep: asset filenames like `fastapitemplate_banner_01.png` are not renamed by design and would false-positive a `find`-based check.
- `make init-app-environment` requires `deploy/` to exist (its script checks); the template ships it, and eval 1's layout check covers it.
