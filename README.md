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

## The App-Delivery Suite (`gs-app-delivery-suite`)

Release-readiness checks for an app that is about to ship.

| Skill | Purpose |
|---|---|
| `privacy-policy-checker` | Compares the privacy policy against what the code actually does — data inventory sweep, AI/third-party providers, Play Data Safety + Apple Nutrition Labels + ATT, GDPR/CCPA/COPPA — and reports gaps with ready-to-paste clause text |

Works on any stack (Flutter, Kotlin, Swift, React Native, web, backend), with fast paths for GenericSuite apps. It produces an alignment matrix with one row per data item — including the aligned ones — so "checked and fine" is distinguishable from "not checked".

```
/privacy-policy-checker ./my-app https://example.com/privacy
```

> Output is an engineering artifact for counsel to review, not legal advice.

## Other plugin groups

| Plugin | Skills |
|---|---|
| `agents-skills` | `build-agents-md` (AGENTS.md generator), `skill-creator` (meta-skill: create/test/evaluate/package skills) |

## Installation

### Claude Code

Using the Claude Code **plugin marketplace**:

```bash
claude

/plugin marketplace add tomkat-cr/genericsuite-skills

/plugin install gs-app-builder-suite@genericsuite-skills
```

### Skills CLI

Using the **Vercel Skills CLI ([skills.sh](https://skills.sh))**:

```bash
npx skills add tomkat-cr/genericsuite-skills
```

## Quick start

### 1. Build a Complete App (Orchestrator)

Run the full interactive flow to build a greenfield app or extend an existing GenericSuite project:

```
# Greenfield: Bootstrap and build a complete full-stack app
/gs-app-builder ./my-app "an inventory management system with products and warehouses, plus an AI chatbot"

# Brownfield: Add a new entity and features to an existing GenericSuite codebase
/gs-app-builder ./ "add a suppliers entity with contact details and a custom metrics endpoint"
```

### 2. Step-by-Step App Builder Skills

Run specific skills directly for modular or incremental updates:

#### Project Scaffolding
```
# Bootstrap a new full-stack GenericSuite application
/app-starter ./my-app
```

#### CRUD Entity Creation
```
# Generate frontend and backend config_dbdef JSON files
/config-builder "create config_dbdef JSON files for a products entity with name, SKU, price, and stock_quantity"

# Add navigation menu entry
/menu-builder "add Products under the Inventory menu in app_main_menu.json"

# Register backend API endpoints
/endpoints-builder "register the products entity endpoints in backend/endpoints.json"

# Generate React CRUD editor components
/jsx-code-builder "generate React CRUD components for products from the frontend JSON config"
```

#### Custom Routers & AI / MCP Integration
```
# Generate custom FastAPI router and model abstractions
/python-fastapi-code-builder "create a custom router for bulk stock adjustments with validation model"

# Wire the AI assistant and tools into backend & frontend
/python-ai-code-builder "wire the GenericSuite AI assistant router into the backend"
/python-ai-tools-code-builder "generate a LangChain @tool calculate_reorder_point and register in ai_gpt_fn_index.py"
/jsx-ai-code-builder "add the AI chatbot assistant shell and field-level AI buttons to the React UI"

# Build or extend the Model Context Protocol (MCP) server
/mcp-builder "expose the app's AI tools and CRUD endpoints via an MCP server"
```

### 3. Repository Utilities & Meta-Skills

```
# Generate or update AGENTS.md documentation for any project
/build-agents-md ./

# Create, evaluate, benchmark, or optimize a skill
/skill-creator "create a new skill for database schema migrations"
```

## Development

- Most skills ship `evals/evals.json`; generated-output tests run in `playground/` (gitignored except the `gs-billing-app` fixture).
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
