# CLAUDE.md

This file provides guidance to AI Coding Assistants (Claude Code, Gemini CLI, Cursor, Antigravity, etc.) when working with code in this repository.

## Project Overview

This is a **Claude Skills Plugin Repository** for GenericSuite — a collection of AI agent skills that extend Claude's capabilities. Skills are self-contained directories under `skills/`, each containing a `SKILL.md` file and optional bundled resources (scripts, references, assets).

The plugin registry is in [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json), which organizes skills into named plugin groups.

## Skill Structure

Each skill directory contains:
- `SKILL.md` — Required. Frontmatter with `name` and `description` (~100 words, used for skill triggering/discovery), followed by full instructions.
- `evals/evals.json` — Test cases (prompts, expected outputs, expectations/assertions)
- `agents/` — Subagent instruction sets (for skills that spawn subagents)
- `references/` — Schema definitions and reference docs bundled with the skill
- `scripts/` — Python utilities for evaluation, packaging, benchmarking
- `assets/` — Static files (HTML viewers, templates)
- `LICENSE.txt` — Skill-level license (may differ from root MIT license)

## Skills in this Repository

| Skill | Purpose |
|---|---|
| `skills/app-starter/` | Bootstraps a new GenericSuite app from the basecamp fastapitemplate (scaffold + rename, env init, .env checklist, install, first run) |
| `skills/build-agents-md/` | Generates AGENTS.md documentation for any project |
| `skills/config-builder/` | Generates GenericSuite frontend/backend JSON config files for CRUD editors |
| `skills/endpoints-builder/` | Adds/updates API endpoint registrations in backend/endpoints.json (idempotent JSON merge) |
| `skills/jsx-ai-code-builder/` | Adds AI features to the React frontend (field chat buttons, chatbot page, genericsuite-ai App shell) |
| `skills/jsx-code-builder/` | Generates React JSX component files from GenericSuite frontend JSON configs |
| `skills/mcp-builder/` | Builds/extends the MCP server exposing the app's AI tools (*_func wrappers, auth, prompts, client configs) |
| `skills/menu-builder/` | Adds/updates menu entries in backend/app_main_menu.json (idempotent JSON merge) |
| `skills/python-ai-code-builder/` | Wires the GenericSuite AI assistant into a backend (router, skeleton GPT-functions index, env checklist) |
| `skills/python-ai-tools-code-builder/` | Generates LangChain @tool/_func pairs for the AI assistant and registers them in ai_gpt_fn_index.py |
| `skills/python-fastapi-code-builder/` | Generates custom GenericSuite FastAPI routers + abstraction-layer model modules |
| `skills/release-notes/` | Drafts bilingual (EN/ES) changelog entries |
| `skills/skill-creator/` | Meta-skill for creating, testing, evaluating, and improving other skills |

## Development Workflow

The `skill-creator` skill defines a complete lifecycle for skill development:

1. **Draft** — Write `SKILL.md` with name, description, and instructions
2. **Test** — Create `evals/evals.json`; execute test cases with subagents
3. **Review** — Generate HTML viewer to inspect results and collect feedback
4. **Improve** — Refactor skill based on feedback; store iterations in `iteration-N/` subdirectories
5. **Optimize** — Run description optimizer to improve Claude's triggering accuracy
6. **Package** — Create distributable `.skill` file (zipfile)

## Python Utility Scripts (skill-creator)

These scripts are in `skills/skill-creator/scripts/` and run with no external dependencies (Python stdlib only, Python 3.6+):

```bash
# Validate a skill's folder structure
python -m scripts.quick_validate <skill-path>

# Package a skill into a distributable .skill file
python -m scripts.package_skill <skill-path> [output-dir]

# Run trigger evaluation on skill descriptions (train/test split)
python -m scripts.run_eval --eval-set <eval-set.json> --skill-path <skill-path>

# Full optimization loop: eval → improve → eval
python -m scripts.run_loop \
  --eval-set <trigger-eval.json> \
  --skill-path <skill-path> \
  --model <model-id> \
  --max-iterations 5 \
  --verbose

# Generate interactive HTML benchmark viewer
python skills/skill-creator/eval-viewer/generate_review.py <workspace> \
  --skill-name "my-skill" \
  --benchmark <workspace>/benchmark.json

# Consolidate benchmark data across iterations
python -m scripts.aggregate_benchmark <workspace>

# Generate HTML benchmark report
python -m scripts.generate_report <workspace>
```

## Evaluation Framework

The `skill-creator` skill uses a quantitative evaluation framework:

- **evals.json** — Test cases with prompts, expected outputs, and typed assertions
- **grading.json** — Grader results (pass/fail per assertion, pass rates, timing)
- **history.json** — Iteration tracking across improvement cycles
- **benchmark.json** — Comparative benchmark data across iterations/versions

Iteration artifacts are stored in `<workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/`.

Subagent roles:
- `agents/grader.md` — Evaluates assertions against execution outputs
- `agents/comparator.md` — Blind A/B comparison of two skill versions
- `agents/analyzer.md` — Post-hoc analysis of why one skill outperformed another

## Adding a New Skill

1. Create a directory under `skills/<skill-name>/`
2. Write `SKILL.md` with YAML frontmatter (`name`, `description`) and instructions
3. Register the skill in `.claude-plugin/marketplace.json` under the appropriate plugin group
4. Use the `skill-creator` skill to test, evaluate, and iterate on the new skill

## Testing Skill run

For those skills that generate files or folders, use the `./playground/` folder to store the generated files or folders.

## Key Schema References

Full JSON schema definitions for evals.json, grading.json, and history.json are in [skills/skill-creator/references/schemas.md](skills/skill-creator/references/schemas.md).

## Important Notes

- The files `AGENTS.md`, `GEMINI.md`, etc. (if present) have only a referece to `@CLAUDE.md` — edit only `CLAUDE.md`.
- Skills live in `.ai/skills/` (source of truth); symlinked under `.agents/skills/`, `.claude/skills/`, `.codex/skills/`, `.gemini/skills/`, and `.devin/skills/`.
