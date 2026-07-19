# Handoff prompt: finish app-builder skill suite Phases 4–6 [GS-254]

Copy everything below the line into a fresh Claude Code session started in
`packages/genericsuite-skills` (superproject: `~/desarrollo/genericsuite`).

---

Finish the GenericSuite app-builder Claude Skills suite (ticket GS-254) in this
repo (`packages/genericsuite-skills`). Phases 0–3 are DONE and merged into
`develop` (latest merge: Phase 3, commit 3f68c99). Remaining work: Phases 4, 5,
and 6.

## Read first (in this order)

1. `docs/design/2026-07-09-app-builder-skill-suite-design.md` — the master
   design. Sections "#### 8. app-starter", "#### 9. gs-app-builder
   (orchestrator)", "Repository Conventions", and "Build Order (phases)" define
   the remaining scope.
2. `.superpowers/sdd/progress.md` — durable ledger of Phases 0–3 execution.
   Everything listed there is done; do not redo it.
3. One executed plan as the structural template for new plans:
   `docs/plans/2026-07-11-app-builder-suite-phase3.md` (also
   `...phase2.md` and `...phase0-1.md` exist).
4. This repo's `CLAUDE.md` (skill table, marketplace registration steps,
   playground convention) and the superproject `CLAUDE.md`.

## Current state (verified 2026-07-11)

- 9 suite skills exist and are merged: config-builder, jsx-code-builder,
  menu-builder, endpoints-builder, python-fastapi-code-builder,
  python-ai-code-builder, python-ai-tools-code-builder, mcp-builder,
  jsx-ai-code-builder. All registered in `.claude-plugin/marketplace.json`
  under the `code-generation-skills` group (alphabetical) and in the CLAUDE.md
  skill table.
- Reference sync is map-driven: `skills/update-gs-docs/reference_map.txt`
  (`src|dest` lines) + `scripts/update-gs-docs.sh` (BASECAMP_DIR local mode or
  GitHub raw), `make sync-references`. Add new exemplar files by extending the
  map, never by hand-copying.
- Eval fixture app lives at `playground/gs-billing-app/` (config_dbdef
  frontend+backend JSONs, ai-fixtures/, ui-fixtures/). `playground/.gitignore`
  ignores everything except `gs-billing-app/`.
- Basecamp checkout is the sibling package
  `../genericsuite-basecamp` (i.e. `packages/genericsuite-basecamp`); its
  `new-project-from-template.sh` and the fastapitemplate/exampleapp templates
  are the app-starter's substrate. Scout them before planning Phase 4.

## Workflow — follow exactly (established over Phases 0–3)

- Per phase: **scout canonical exemplars → write the plan with verbatim
  file content (superpowers:writing-plans) → execute with
  superpowers:subagent-driven-development → eval smoke run with mechanical
  grading → ONE fix wave from the final review → hand the branch to the user.**
- Branch per phase off `develop`: `feature/GS-254-phase4`, then `-phase5`,
  `-phase6`. ALWAYS verify `pwd` is this repo before any git command (a
  previous session created a branch in the wrong submodule).
- Per-task commits by subagents on the feature branch are approved. **The user
  personally does all merges and pushes** — when a phase branch is ready,
  report the commit list and stop; never merge, push, or commit ad-hoc changes
  outside SDD task execution.
- Model tiering: haiku implementers for transcription tasks (plan contains the
  full content), sonnet reviewers, most-capable model for the final
  whole-branch review. One fix subagent per findings wave, not one per finding.
- Tell implementers explicitly: never commit `__pycache__`/`.pyc` files (this
  bit us twice).
- Append to `.superpowers/sdd/progress.md` after every completed task and
  review, same format as the existing entries.
- Skill conventions: `skills/<name>/SKILL.md` with `name`, `description`,
  `argument-hint` frontmatter; `evals/evals.json` with ≥2 runtime-validity
  test cases (assert on behavior/output validity, not just structure — a
  structural-only eval once passed a broken fixture at 100%); `references/`
  seeded via reference_map.txt; register in marketplace.json + CLAUDE.md
  table; validate with
  `python -m scripts.quick_validate skills/<name>` (run from
  `skills/skill-creator/`).

## Phase 4 — `app-starter` skill

One skill covering backend+frontend bootstrap (the fastapitemplate monorepo
contains `ui/`, `server/`, and MCP server — no separate frontend starter).

- Behavior per design doc: gather target dir, app name, domain, template;
  run basecamp's `new-project-from-template.sh` (curl or local clone); then
  guide through `make init-app-environment`, `.env` editing with an
  interactive checklist of required vars, `make install-all`, `make dev`.
- Greenfield only. Reserve a "template" question in the flow for GS-306
  (exampleapp template with backend framework selection) without building it.
- Evals: exercise in `playground/` (a scaffold-into-playground run); keep
  fixtures small and gitignore-aware.

## Phase 5 — `gs-app-builder` orchestrator

SKILL.md instruction flow that invokes the other 9 skills by name, holding a
shared "app brief" (entities, fields, relationships, AI features, deployment
intent) so later skills don't re-ask questions.

- Flow steps 0–9 are fully specified in the design doc — implement verbatim,
  including **step 0 mode detection** (greenfield vs. brownfield: probe for
  `config_dbdef/`, genericsuite Python deps, `componentMap` in App.jsx; if the
  dir exists but is NOT a GenericSuite project, stop and point at the
  `gs-adopt` gap — never scaffold on foreign code).
- Checkpoints after each phase of the flow: show generated files, get user
  confirmation before continuing.
- Exercise end-to-end in `playground/` building a small sample app
  (design suggests an "invoices" domain — reuse/extend gs-billing-app or a
  fresh sibling, your call at planning time).

## Phase 6 — Docs & publishing (GS-254 close-out)

- README + CHANGELOG updates in this repo covering the whole suite.
- Basecamp docs page listing the suite (basecamp is a separate submodule —
  prepare the change, let the user commit there).
- Marketplace grouping decision: design proposes a `gs-app-builder-suite`
  plugin group in `.claude-plugin/marketplace.json`; skills currently sit in
  `code-generation-skills`. **Ask the user** whether to move/duplicate before
  editing.
- Publish to the Claude Skills marketplace and skills.sh — prepare packaging
  (`package_skill` per skill or plugin-level, whichever those channels need)
  and give the user the exact publish steps/commands; the user executes
  anything requiring their accounts.
- Deferred minors to sweep here: unused `log_debug` import in the
  python-ai-tools-code-builder tools template; basecamp docstring typo
  "a the" → "of the" (user's call, flag it).

## Start

Begin with Phase 4: scout basecamp's `new-project-from-template.sh` and the
fastapitemplate structure, then write
`docs/plans/<today>-app-builder-suite-phase4.md` and execute it
subagent-driven. Ask 1–3 key questions before planning only if something
above is genuinely ambiguous.
