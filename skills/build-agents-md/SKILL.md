---
name: build-agents-md
description: Generate or update an AGENTS.md file for any project repository by analyzing the codebase. Use when the user asks to "build AGENTS.md", "create AGENTS.md", "generate AGENTS.md", or "scaffold agent instructions" for a project.
argument-hint: [path/to/project] (optional; defaults to current working directory)
---

Generate a well-filled `AGENTS.md` for the target project by exploring its codebase and filling in the template.

## Steps

### 1. Determine the target directory

If `$ARGUMENTS` is provided, treat it as the project root. Otherwise use the current working directory.

### 2. Read the template

Read the template from this skill's own directory:
`.claude/skills/build-agents-md/AGENTS-template.md`

This is the canonical template. It can be edited there to change the structure for all future runs.

### 3. Explore the project

Gather information for each template section. Read whichever of these exist (skip silently if absent):

**Project overview**
- `README.md` or `README.rst` — name, purpose, high-level description
- `pyproject.toml` / `setup.cfg` / `setup.py` — Python project metadata
- `package.json` (root) — JS/TS project name, description, workspaces

**Build and test commands**
- `Makefile` — all targets (focus on install, run, build, test, deploy, clean)
- `package.json` scripts block
- `pyproject.toml` `[tool.taskipy]` or `[tool.poe]` sections
- `.github/workflows/*.yml` — CI commands reveal canonical build/test invocations
- `docker-compose.yml` / `Dockerfile` — containerised run commands

**Code style guidelines**
- `.eslintrc*`, `eslint.config.*` — JS/TS linter
- `.prettierrc*` — JS/TS formatter
- `pyproject.toml` `[tool.black]`, `[tool.ruff]`, `[tool.flake8]` — Python formatter/linter
- `.editorconfig` — editor-level conventions (indent, line endings)
- `tsconfig.json` — TypeScript strictness settings
- `package.json` `engines` field — Node.js version requirements
- `.python-version` / `Pipfile` / `uv.lock` — Python version

**Testing instructions**
- `pytest.ini` / `pyproject.toml [tool.pytest]` — pytest config
- `package.json` `test` script — JS test runner and flags
- `jest.config.*` — Jest setup
- Any `tests/` or `__tests__/` directories — presence confirms test suite exists

**Security considerations**
- `.env.example` — lists expected env vars (never commit real `.env`)
- `SECURITY.md` — explicit security policy
- `package.json` — check for `npm audit` mentions in scripts
- `requirements*.txt` / `pyproject.toml` — check for `pip-audit` or `safety`
- `Dockerfile` — note if secrets are handled via build args vs runtime env

### 4. Write the AGENTS.md

Using the template structure and everything discovered above, produce a complete `AGENTS.md` at the project root (`{target-dir}/AGENTS.md`).

Rules:
- Keep each section concise and actionable — these are instructions for an AI agent, not prose documentation
- Use fenced code blocks for all commands
- If a section has nothing to fill in (truly empty), write `_Nothing specific found — follow general best practices._`
- Do NOT invent commands or settings that were not found in the codebase
- If the project already has an `AGENTS.md`, show a diff of proposed changes and ask the user to confirm before overwriting

### 5. Confirm and remind

After writing the file, tell the user:
- The path where `AGENTS.md` was written
- Which sections were filled from discovered files vs left as stubs
- That the template lives at `.claude/skills/build-agents-md/AGENTS-template.md` and can be edited to customize future runs
