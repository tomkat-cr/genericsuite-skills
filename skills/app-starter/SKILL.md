---
name: app-starter
description: Bootstrap a brand-new GenericSuite application from the basecamp fastapitemplate — a full-stack monorepo with React frontend (ui/), FastAPI backend (server/), MCP server, and JSON-driven config_dbdef. Scaffolds via basecamp's new-project-from-template.sh (or a local basecamp checkout), renames the app, then guides through make init-app-environment, the required .env variables checklist, make install-all, and the first make dev / make run. Use when the user wants to start, create, scaffold, or bootstrap a new GenericSuite project. Greenfield only — never run it on an existing directory.
argument-hint: "[target-dir] [app-name] [domain]"
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

Replicates what the script does, without the network clone — extracting only git-tracked template content:

```bash
[ -e "<target-dir>" ] && { echo "target exists — refusing to scaffold"; exit 1; }
mkdir -p "<target-dir>"
# extract TRACKED content only — a local checkout's working tree may hold
# untracked artifacts (stale .env files with secrets, node_modules) that a
# fresh clone never has; git archive makes inheriting them impossible
git -C "<basecamp-dir>" archive HEAD:mkdocs_root/code/fastapitemplate | tar -x -C "<target-dir>"
git -C "<basecamp-dir>" archive HEAD scripts/rename-app.sh | tar -x -C "<target-dir>"
cd "<target-dir>"
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
[ -z "$(find . -name '.env*' ! -name '*.example' -not -path './.git/*')" ] && echo "no stray env files"
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
system tools yourself): git, Node.js 26+ with npm, Python 3.12+, `uv`,
Make, Docker/Podman (only for `make run`). Then:

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
