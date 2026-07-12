# GenericSuite App-Builder Skill Suite — Phase 6 Implementation Plan (GS-254 close-out)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close out GS-254: rename the marketplace plugin group to `gs-app-builder-suite` (user decision 2026-07-12), rewrite README + CHANGELOG for the suite, prepare the basecamp change (rename-app.sh filename pass + AI-skills docs page — user commits basecamp-side), resync app-starter references, sweep the deferred minors, and verify packaging/validation for publishing (user executes account-bound publish steps).

**Architecture:** Three tasks: (1) skills-repo docs & regroup, (2) prepared basecamp change + reference resync, (3) whole-suite validation & packaging verification. No new skills; no evals.json changes.

**Tech Stack:** Markdown, JSON, bash, Python 3 stdlib (`quick_validate`, `package_skill`).

**Working directory for ALL tasks:** `/Users/carlosramirez/desarrollo/genericsuite/packages/genericsuite-skills`.

## Global Constraints

- **Commits:** per-task commits on branch `feature/GS-254-phase6`; the user merges/pushes manually. Never commit `__pycache__`/`.pyc`, `dist/` (gitignored), or playground outputs.
- **Basecamp is the user's to commit:** Task 2 edits files in `../genericsuite-basecamp` but runs NO git commands there — changes stay uncommitted in its working tree. Never touch its untracked `.env*` files.
- User decisions honored verbatim: plugin group `code-generation-skills` → **`gs-app-builder-suite`** (rename in place, same 11 skills); basecamp change includes rename-app.sh filename pass + docs page (the "a the" docstring typo was searched for and no longer exists in basecamp — already fixed at source; nothing to do).
- Reference files under `skills/*/references/` are only ever produced by the sync mechanism (`skills/update-gs-docs/scripts/update-gs-docs.sh`), never hand-edited.
- Commit message style: `Add:`/`Change:`/`Fix:` prefix + `[GS-254]`.
- `quick_validate` must exit 0 for every skill under `skills/` at the end of the phase.

---

### Task 1: Marketplace regroup + README + CHANGELOG + log_debug sweep

**Files:**
- Modify: `.claude-plugin/marketplace.json`
- Modify: `README.md` (full replacement)
- Modify: `CHANGELOG.md` (insert release section under the `[Unreleased]` template)
- Modify: `skills/python-ai-tools-code-builder/SKILL.md` (remove one unused import line from the tools template)

**Interfaces:**
- Consumes: current marketplace.json (plugin `code-generation-skills` with 11 skills).
- Produces: plugin group named `gs-app-builder-suite` (Task 3 validates against it; the basecamp docs page in Task 2 names it).

- [ ] **Step 1: Rename the plugin group in `.claude-plugin/marketplace.json`**

Change ONLY these two fields of the first plugin (the `skills` array of 11 entries stays byte-identical):

```json
      "name": "gs-app-builder-suite",
      "description": "GenericSuite app-builder suite — bootstrap a full-stack GenericSuite app and generate its JSON configs, CRUD code, AI assistant wiring and MCP server",
```

Also bump `metadata.version` from `"1.0.0"` to `"1.1.0"`.

- [ ] **Step 2: Replace `README.md` with exactly this content**

````markdown
# GenericSuite Skills

AI agent skills for the [GenericSuite](https://genericsuite.carlosjramirez.com) ecosystem — a **Claude Skills plugin repository**. Skills are self-contained directories under `skills/`, each with a `SKILL.md` and optional bundled resources (references, scripts, evals), organized into plugin groups in [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json).

## The App-Builder Suite (`gs-app-builder-suite`)

Build a complete GenericSuite application — React frontend, FastAPI backend, JSON-driven CRUD, AI assistant, MCP server — from a conversation. The entry point is `/gs-app-builder`, which detects greenfield vs. brownfield, interviews you into an app brief, and drives the specialized skills below with a checkpoint after each phase:

| Skill | Purpose |
|---|---|
| `gs-app-builder` | **Orchestrator** — mode detection, app-brief interview, drives the whole flow |
| `app-starter` | Bootstraps a new app from basecamp's `fastapitemplate` (scaffold + rename, env init, `.env` checklist, install, first run) |
| `config-builder` | Generates the frontend/backend `config_dbdef` JSON files for a CRUD entity |
| `menu-builder` | Adds menu entries to `backend/app_main_menu.json` (idempotent merge) |
| `endpoints-builder` | Registers entities in `backend/endpoints.json` (idempotent merge; skips array children) |
| `jsx-code-builder` | Generates the React CRUD editor components from the frontend JSON configs |
| `python-fastapi-code-builder` | Custom FastAPI routers + abstraction-layer model modules for non-CRUD endpoints |
| `python-ai-code-builder` | Wires the GenericSuite AI assistant into the backend (router, GPT-functions index, env checklist) |
| `python-ai-tools-code-builder` | Generates LangChain `@tool`/`*_func` pairs and registers them in the GPT-functions index |
| `jsx-ai-code-builder` | Adds AI features to the frontend (field chat buttons, chatbot page, genericsuite-ai App shell) |
| `mcp-builder` | Builds/extends the MCP server exposing the app's AI tools and CRUD endpoints |

> The orchestrator invokes the other skills by name, so install the whole `gs-app-builder-suite` plugin — a standalone install of `gs-app-builder` alone cannot drive the flow.

Existing GenericSuite apps are supported too: the suite detects them and works additively (idempotent JSON merges, index preservation, MCP EXTEND mode). Directories with non-GenericSuite code are refused — retrofitting (`gs-adopt`) is future scope.

## Other plugin groups

| Plugin | Skills |
|---|---|
| `agents-skills` | `build-agents-md` (AGENTS.md generator), `skill-creator` (meta-skill: create/test/evaluate/package skills) |
| `release-prep-skills` | `release-notes` (bilingual EN/ES changelog entries) |

## Installation

**Claude Code (plugin marketplace):**

```
/plugin marketplace add tomkat-cr/genericsuite-skills
/plugin install gs-app-builder-suite@genericsuite-skills
```

**skills CLI ([skills.sh](https://skills.sh)):**

```bash
npx skills add tomkat-cr/genericsuite-skills
```

## Quick start

```
/gs-app-builder ./my-app "an inventory app with products and warehouses, with an AI chatbot"
```

Or run the pieces yourself: `/app-starter` to scaffold, then `/config-builder`, `/menu-builder`, `/endpoints-builder`, `/jsx-code-builder` per entity, and the AI/MCP builders when you want them.

## Development

- Each skill ships `evals/evals.json`; generated-output tests run in `playground/` (gitignored except the `gs-billing-app` fixture).
- Validate a skill: `(cd skills/skill-creator && python3 -m scripts.quick_validate ../../skills/<name>)`
- Package a skill: `(cd skills/skill-creator && python3 -m scripts.package_skill ../../skills/<name> ../../dist)`
- Reference exemplars under `skills/*/references/` are synced from a basecamp checkout — never hand-edited: `BASECAMP_DIR=../genericsuite-basecamp make sync-references`

## Documentation

* [https://genericsuite.carlosjramirez.com](https://genericsuite.carlosjramirez.com)
* Mirror: [https://genericsuite.readthedocs.io](https://genericsuite.readthedocs.io)

## License

[GenericSuite](https://genericsuite.carlosjramirez.com) is open-sourced software licensed under the MIT license.

## Credits

This project is developed and maintained by [Carlos J. Ramirez](https://carlosjramirez.com). For more information or to contribute to the GenericSuite project, visit [GenericSuite on GitHub](https://github.com/tomkat-cr/genericsuite-skills).

Happy Coding!
````

- [ ] **Step 3: Insert a release section in `CHANGELOG.md`**

Keep the `## [Unreleased] - Date` template block at the top exactly as it is. Immediately AFTER it (before `## [Unreleased] - 2026-04-12`), insert:

```markdown
## 1.1.0 (2026-07-12)

### Added
- App-builder skill suite (`gs-app-builder-suite` plugin group) [GS-254]:
  `gs-app-builder` orchestrator (greenfield/brownfield mode detection, app-brief
  interview, checkpointed flow), `app-starter`, `config-builder` (updated),
  `jsx-code-builder` (updated), `menu-builder`, `endpoints-builder`,
  `python-fastapi-code-builder`, `python-ai-code-builder`,
  `python-ai-tools-code-builder`, `jsx-ai-code-builder`, `mcp-builder`.
- Per-skill `evals/evals.json` with runtime-validity assertions, exercised in
  `playground/` [GS-254].
- Reference-sync mechanism: `skills/update-gs-docs` map + script,
  `make sync-references` [GS-254].

### Changed
- Marketplace plugin group `code-generation-skills` renamed to
  `gs-app-builder-suite`; metadata version 1.1.0 [GS-254].
- README rewritten around the app-builder suite, installation and
  publishing [GS-254].
```

- [ ] **Step 4: Remove the unused import from the tools template**

In `skills/python-ai-tools-code-builder/SKILL.md`, in the Python template code block, delete this single line (flagged by review in Phase 2 — the template never calls it, so generated files fail flake8 F401):

```python
from genericsuite.util.app_logger import log_debug
```

Leave the adjacent `from genericsuite.util.app_context import CommonAppContext` line and everything else untouched.

- [ ] **Step 5: Validate**

```bash
python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); assert d['plugins'][0]['name']=='gs-app-builder-suite'; assert len(d['plugins'][0]['skills'])==11; assert d['metadata']['version']=='1.1.0'; print('marketplace OK')"
! grep -q "log_debug" skills/python-ai-tools-code-builder/SKILL.md && echo "log_debug gone"
grep -q "gs-app-builder-suite" README.md && grep -q "1.1.0 (2026-07-12)" CHANGELOG.md && echo "docs OK"
```
Expected: `marketplace OK`, `log_debug gone`, `docs OK`.

- [ ] **Step 6: Commit**

```bash
git add .claude-plugin/marketplace.json README.md CHANGELOG.md skills/python-ai-tools-code-builder/SKILL.md
git commit -m "Change: rename plugin group to gs-app-builder-suite, rewrite README/CHANGELOG for the suite, drop unused log_debug from tools template [GS-254]"
```

---

### Task 2: Prepared basecamp change + reference resync

**Files:**
- Modify (basecamp working tree, NOT committed): `../genericsuite-basecamp/scripts/rename-app.sh`
- Create (basecamp working tree, NOT committed): `../genericsuite-basecamp/mkdocs_root/en/ai-skills.md`
- Modify (basecamp working tree, NOT committed): `../genericsuite-basecamp/mkdocs.yml` (one nav line)
- Modified by sync (skills repo, committed): `skills/app-starter/references/rename-app.sh`

**Interfaces:**
- Consumes: Task 1's plugin-group name (`gs-app-builder-suite`) — the docs page references it.
- Produces: the basecamp diff the user reviews and commits themselves; the resynced app-starter reference.

- [ ] **Step 1: Add the filename-rename pass to `../genericsuite-basecamp/scripts/rename-app.sh`**

Insert this block AFTER the existing content-rewrite `done < <( find ... )` loop and BEFORE the `echo ""` / `echo "Done. $FILE_COUNT file(s) updated."` lines:

```bash
# ── Rename files whose names contain the old name ───────────────────────────
# (contents were rewritten above; filenames like
#  server/fastapitemplate-backend_openapi.json need renaming too)
while IFS= read -r -d '' file; do
    base="$(basename "$file")"
    newbase="$(echo "$base" | perl -pe "s/\Q${OLD_NAME}\E/${NEW_NAME}/gi")"
    if [ "$base" != "$newbase" ]; then
        mv "$file" "$(dirname "$file")/${newbase}"
        echo "  renamed: ${file#$BASE_DIR/} -> ${newbase}"
        FILE_COUNT=$((FILE_COUNT + 1))
    fi
done < <(
    find "$BASE_DIR" \
        \( "${PRUNE_ARGS[@]}" \) -prune \
        -o -type f -iname "*${OLD_NAME}*" -print0
)
```

(Files only, deliberately: the template has no directories named after the app. `-iname` mirrors the content pass's case-insensitive `/gi`.)

- [ ] **Step 2: Test the modified script in a throwaway dir**

```bash
T=$(mktemp -d)
mkdir -p "$T/app/scripts" "$T/app/server"
cp ../genericsuite-basecamp/scripts/rename-app.sh "$T/app/scripts/"
printf '{"info": {"title": "fastapitemplate backend"}}\n' > "$T/app/server/fastapitemplate-backend_openapi.json"
printf 'APP_NAME=fastapitemplate\nAPP_DOMAIN_NAME=fastapitemplate.com\n' > "$T/app/.env.example"
bash -n "$T/app/scripts/rename-app.sh" && echo "syntax OK"
(cd "$T/app" && bash scripts/rename-app.sh zetaapp zeta.io)
[ -f "$T/app/server/zetaapp-backend_openapi.json" ] && echo "filename renamed"
grep -q '"title": "zetaapp backend"' "$T/app/server/zetaapp-backend_openapi.json" && echo "content renamed"
grep -q '^APP_NAME=zetaapp$' "$T/app/.env.example" && grep -q '^APP_DOMAIN_NAME=zeta.io$' "$T/app/.env.example" && echo "env renamed"
[ -z "$(find "$T/app" -iname '*fastapitemplate*')" ] && echo "no old-name files remain"
rm -rf "$T"
```
Expected: `syntax OK`, `filename renamed`, `content renamed`, `env renamed`, `no old-name files remain`.

- [ ] **Step 3: Create `../genericsuite-basecamp/mkdocs_root/en/ai-skills.md` with exactly this content**

````markdown
# AI Skills

The [genericsuite-skills](https://github.com/tomkat-cr/genericsuite-skills) repository is a Claude Skills plugin collection for the GenericSuite ecosystem. Its centerpiece is the **app-builder suite** (`gs-app-builder-suite`): a set of AI agent skills that build a complete GenericSuite application — React frontend, FastAPI backend, JSON-driven CRUD, AI assistant and MCP server — from a conversation.

## The app-builder suite

The entry point is `/gs-app-builder`. It detects whether the target directory is a brand-new app (greenfield) or an existing GenericSuite project (brownfield, handled additively), interviews you into an *app brief*, and then drives the specialized skills with a checkpoint after each phase:

| Skill | Purpose |
|---|---|
| `gs-app-builder` | Orchestrator: mode detection, app-brief interview, drives the flow end to end |
| `app-starter` | Bootstraps a new app from the basecamp `fastapitemplate` monorepo |
| `config-builder` | Generates the `config_dbdef` frontend/backend JSON files per CRUD entity |
| `menu-builder` | Adds entries to `backend/app_main_menu.json` idempotently |
| `endpoints-builder` | Registers entities in `backend/endpoints.json` idempotently |
| `jsx-code-builder` | Generates the React CRUD editor components from the JSON configs |
| `python-fastapi-code-builder` | Custom FastAPI endpoints + business-logic modules on the genericsuite-be abstraction layer |
| `python-ai-code-builder` | Wires the GenericSuite AI assistant (router, GPT-functions index, env checklist) |
| `python-ai-tools-code-builder` | App-specific LangChain tools for the assistant, registered in the index |
| `jsx-ai-code-builder` | Frontend AI features: field chat buttons, chatbot page, genericsuite-ai App shell |
| `mcp-builder` | MCP server exposing the app's AI tools and CRUD endpoints |

## Installation

**Claude Code:**

```
/plugin marketplace add tomkat-cr/genericsuite-skills
/plugin install gs-app-builder-suite@genericsuite-skills
```

**skills CLI ([skills.sh](https://skills.sh)):**

```bash
npx skills add tomkat-cr/genericsuite-skills
```

## Quick start

```
/gs-app-builder ./my-app "an inventory app with products and warehouses, with an AI chatbot"
```

The repository also ships `agents-skills` (AGENTS.md generation, skill-creator meta-skill) and `release-prep-skills` (bilingual release notes). See the [genericsuite-skills README](https://github.com/tomkat-cr/genericsuite-skills#readme) for development and evaluation workflows.
````

- [ ] **Step 4: Add the nav entry to `../genericsuite-basecamp/mkdocs.yml`**

Insert after the `  - 'Sample Code': './Sample-Code/index.md'` line:

```yaml
  - 'AI Skills': './ai-skills.md'
```

- [ ] **Step 5: Resync app-starter references in the skills repo**

```bash
BASECAMP_DIR=../genericsuite-basecamp bash skills/update-gs-docs/scripts/update-gs-docs.sh
git status --porcelain
```
Expected: `CHANGED: skills/app-starter/references/rename-app.sh`, `0 failed`; git status shows ONLY that file modified.

- [ ] **Step 6: Verify byte-identity and commit (skills repo only)**

```bash
cmp ../genericsuite-basecamp/scripts/rename-app.sh skills/app-starter/references/rename-app.sh && echo "identical"
bash -n skills/app-starter/references/rename-app.sh && echo "syntax OK"
git add skills/app-starter/references/rename-app.sh
git commit -m "Change: resync rename-app.sh reference — basecamp adds filename-rename pass for old-name files [GS-254]"
```

NO git commands in `../genericsuite-basecamp` — its three changed/new files stay in the working tree for the user to review and commit.

---

### Task 3: Whole-suite validation + packaging verification

**Files:**
- Create (transient, gitignored): `dist/*.skill`

**Interfaces:**
- Consumes: Tasks 1–2 committed state.
- Produces: pass/fail evidence in `.superpowers/sdd/progress.md`; the publish-steps summary handed to the user at phase end.

- [ ] **Step 1: quick_validate every skill**

```bash
fail=0
for s in skills/*/; do
  n=$(basename "$s")
  [ -f "$s/SKILL.md" ] || continue
  if (cd skills/skill-creator && python3 -m scripts.quick_validate "../../skills/$n" >/dev/null 2>&1); then
    echo "PASS: $n"
  else
    echo "FAIL: $n"; fail=1
  fi
done
exit $fail
```
Expected: PASS for every skill directory that has a SKILL.md.

- [ ] **Step 2: Package the 11 suite skills into `dist/`**

```bash
mkdir -p dist
for n in gs-app-builder app-starter config-builder menu-builder endpoints-builder jsx-code-builder python-fastapi-code-builder python-ai-code-builder python-ai-tools-code-builder jsx-ai-code-builder mcp-builder; do
  (cd skills/skill-creator && python3 -m scripts.package_skill "../../skills/$n" ../../dist) || echo "PACKAGE FAIL: $n"
done
ls -la dist/
git check-ignore dist && echo "dist ignored (not committable)"
```
Expected: 11 `.skill` files; `dist ignored`.

- [ ] **Step 3: Consistency checks**

```bash
python3 - <<'EOF'
import json, pathlib, re
mp = json.load(open('.claude-plugin/marketplace.json'))
mp_skills = {p.split('/')[-1] for pl in mp['plugins'] for p in pl['skills']}
fs_skills = {d.name for d in pathlib.Path('skills').iterdir() if (d/'SKILL.md').exists()}
claude_rows = set(re.findall(r'\| `skills/([a-z-]+)/`', pathlib.Path('CLAUDE.md').read_text()))
print('in marketplace but not on disk:', sorted(mp_skills - fs_skills))
print('on disk but unregistered:', sorted(fs_skills - mp_skills))
print('on disk but not in CLAUDE.md table:', sorted(fs_skills - claude_rows))
EOF
```
Expected: first two lines empty lists; third line may legitimately list `update-gs-docs` (internal maintenance skill, unregistered by design) — anything else is a finding.

- [ ] **Step 4: Record and clean**

Append results to `.superpowers/sdd/progress.md`. `rm -rf dist` is NOT needed (gitignored) but confirm `git status --porcelain` shows nothing staged. No commit unless a fix was required.

---

## Publish steps for the user (deliverable of the phase, executed by the user)

1. Merge `feature/GS-254-phase6` into `develop` (and onward to `main` when releasing), push, and tag `v1.1.0`.
2. In `../genericsuite-basecamp`: review the three working-tree changes (`scripts/rename-app.sh`, `mkdocs_root/en/ai-skills.md`, `mkdocs.yml`), commit and push them; the docs site picks up the AI Skills page on next deploy.
3. Basecamp hygiene (yours): delete/rotate the untracked `.env` files with real-looking secrets under `mkdocs_root/code/fastapitemplate/` (root, `server/`, `ui/`, `mcp-server/`, `ui/.env.*.bak`).
4. Claude Skills marketplace: with the repo public on GitHub, users install via `/plugin marketplace add tomkat-cr/genericsuite-skills` — verify once from a clean Claude Code session, then announce.
5. skills.sh: the repo layout (`skills/<name>/SKILL.md`) is already compatible; submit/verify the listing at skills.sh under your account (`npx skills add tomkat-cr/genericsuite-skills` is the user-side install to smoke-test).
6. Optional: attach the `dist/*.skill` files to the GitHub release for manual installs.

## Self-Review Notes

- Handoff coverage: README + CHANGELOG ✔ (Task 1); basecamp docs page prepared, user commits ✔ (Task 2); marketplace grouping decided BY USER (gs-app-builder-suite) and applied ✔ (Task 1); publishing prep with user-executed steps ✔ (Task 3 + publish list); deferred minors: unused `log_debug` ✔ (Task 1 Step 4), basecamp "a the" typo — searched, no longer exists, closed as already-fixed ✔; rename-app.sh filename pass + reference resync ✔ (Task 2, per user decision 2026-07-11); basecamp `.env` secrets reminder ✔ (publish step 3).
- Phase-5 minor (sibling-path validity under per-skill installs) addressed by the README/docs blockquote telling users to install the whole suite plugin.
- The plugin-group rename changes the name existing installs reference — the user chose this knowingly; CHANGELOG documents it.
- CLAUDE.md needs no edit: it never names plugin groups (verified by grep), and the skills table already includes all 13 documented skills.
