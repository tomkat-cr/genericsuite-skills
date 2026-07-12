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
