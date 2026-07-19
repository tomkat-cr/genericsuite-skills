# GenericSuite App-Builder Skill Suite — Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the AI-backend skills of the app-builder suite — `python-ai-code-builder` (assistant endpoint wiring), `python-ai-tools-code-builder` (LangChain tools / GPT functions), and `mcp-builder` (MCP server from the generated tools) — per `docs/design/2026-07-09-app-builder-skill-suite-design.md`.

**Architecture:** Same shape as Phase 1: each skill is a `skills/<name>/SKILL.md` instruction document with `references/` exemplars (synced from basecamp via `reference_map.txt` + `make sync-references`), `evals/evals.json` (≥2 cases with runtime-validity assertions), playground fixtures, and registration in `.claude-plugin/marketplace.json` + `CLAUDE.md`. The three skills chain: ai-code-builder creates the assistant router + a skeleton `ai_gpt_fn_index.py`; tools-code-builder fills the index with `@tool`/`_func` pairs; mcp-builder wraps the `_func` variants as `@mcp.tool()`.

**Tech Stack:** Markdown SKILL.md files, Python 3 stdlib validation, skill-creator eval framework, bash reference sync.

**Working directory for ALL tasks:** `/Users/carlosramirez/desarrollo/genericsuite/packages/genericsuite-skills`.

## Global Constraints

- **Commits:** the user prefers to commit manually. At execution time, ask once whether per-task commits on a feature branch are acceptable (recommended — reviews need per-task diffs) or whether to leave all changes uncommitted in the working tree. Every "Commit" step below is conditional on that answer; when commits are off, end the task by listing the changed files instead.
- Every new skill: `SKILL.md` frontmatter with `name`, `description` (~100 words max), `argument-hint`; registered in `.claude-plugin/marketplace.json` (group `code-generation-skills`, alphabetical); row in `CLAUDE.md` "Skills in this Repository" table (alphabetical); `evals/evals.json` with ≥2 cases.
- Eval expectations must include at least one runtime-validity assertion (py_compile / JSON parse), not only structure checks.
- Backend result shape non-negotiable: `{"error": bool, "error_message": str | None, "resultset": Any}`.
- Security: AI tool templates must wrap AI/user-provided URLs with `is_safe_url()` and local paths with `is_safe_local_path()` (from `genericsuite_ai.lib.ai_utilities` / `genericsuite.util.utilities` — check the synced references for the exact import at generation time); never log raw user input.
- Commit message style (when committing): `Add:`/`Change:`/`Fix:` prefix + `[GS-254]`.
- `quick_validate` now accepts `argument-hint` (fixed in Phase 1) — validation steps must exit 0.
- Skill-generated test outputs go under `playground/`.
- Known upstream quirk: fastapitemplate's `mcp-server/*_config.json` files carry stale `genericsuite-codegen` names/paths — they are STRUCTURAL references only; generated client configs must use the target app's own name and paths.

---

### Task 1: Phase-2 reference seeding

**Files:**
- Modify: `skills/update-gs-docs/reference_map.txt` (append Phase-2 block)
- Created by sync (do not hand-author): `skills/python-ai-code-builder/references/**`, `skills/python-ai-tools-code-builder/references/**`, `skills/mcp-builder/references/**`

**Interfaces:**
- Consumes: `make sync-references` / `BASECAMP_DIR=../genericsuite-basecamp bash skills/update-gs-docs/scripts/update-gs-docs.sh` (Phase 1).
- Produces: the reference files listed below, at exactly these paths — Tasks 2–4 SKILL.md documents cite them verbatim.

- [ ] **Step 1: Append the Phase-2 block to `skills/update-gs-docs/reference_map.txt`**

```
# python-ai-code-builder
mkdocs_root/code/fastapitemplate/server/lib/routers/ai_assistant.py|skills/python-ai-code-builder/references/routers/ai_assistant.py
mkdocs_root/code/exampleapp/apps/api-fastapi/lib/models/ai_chatbot/ai_gpt_fn_index.py|skills/python-ai-code-builder/references/models/ai_gpt_fn_index.py
mkdocs_root/code/fastapitemplate/server/lib/main.py|skills/python-ai-code-builder/references/main.py

# python-ai-tools-code-builder
mkdocs_root/code/exampleapp/apps/api-fastapi/lib/models/ai_chatbot/ai_gpt_fn_fda.py|skills/python-ai-tools-code-builder/references/ai_gpt_fn_fda.py
mkdocs_root/code/exampleapp/apps/api-fastapi/lib/models/ai_chatbot/ai_gpt_fn_app.py|skills/python-ai-tools-code-builder/references/ai_gpt_fn_app.py
mkdocs_root/code/exampleapp/apps/api-fastapi/lib/models/ai_chatbot/ai_gpt_fn_index.py|skills/python-ai-tools-code-builder/references/ai_gpt_fn_index.py

# mcp-builder
mkdocs_root/code/exampleapp/apps/mcp-server/mcp_server.py|skills/mcp-builder/references/mcp_server_full_example.py
mkdocs_root/code/fastapitemplate/server/lib/mcp_server.py|skills/mcp-builder/references/mcp_server_minimal.py
mkdocs_root/code/fastapitemplate/mcp-server/package.json|skills/mcp-builder/references/mcp-server-package.json
mkdocs_root/code/fastapitemplate/mcp-server/claude_desktop_stdio_config.json|skills/mcp-builder/references/claude_desktop_stdio_config.json
mkdocs_root/code/fastapitemplate/mcp-server/claude_desktop_http_config.json|skills/mcp-builder/references/claude_desktop_http_config.json
mkdocs_root/code/fastapitemplate/mcp-server/vscode_mcp_stdio_config.json|skills/mcp-builder/references/vscode_mcp_stdio_config.json
mkdocs_root/code/fastapitemplate/mcp-server/vscode_mcp_http_config.json|skills/mcp-builder/references/vscode_mcp_http_config.json
mkdocs_root/code/fastapitemplate/mcp-server/README.md|skills/mcp-builder/references/mcp-server-README.md
```

- [ ] **Step 2: Run the sync**

Run: `BASECAMP_DIR=../genericsuite-basecamp bash skills/update-gs-docs/scripts/update-gs-docs.sh`
Expected: `CHANGED:` line for each of the 14 new destinations; `0 failed`; existing entries unchanged.

- [ ] **Step 3: Verify byte-identity and Python validity**

Run:
```bash
while IFS='|' read -r src dest; do
    case "${src}" in \#*|"") continue ;; esac
    cmp "../genericsuite-basecamp/${src}" "${dest}" || echo "MISMATCH: ${dest}"
done < skills/update-gs-docs/reference_map.txt; echo "verify done"
python3 -m py_compile skills/python-ai-code-builder/references/routers/ai_assistant.py skills/python-ai-tools-code-builder/references/ai_gpt_fn_fda.py skills/mcp-builder/references/mcp_server_full_example.py && echo "compile OK"
```
Expected: `verify done` with no MISMATCH lines; `compile OK`.

- [ ] **Step 4: Commit (if commits enabled)**

```bash
git add skills/update-gs-docs/reference_map.txt skills/python-ai-code-builder skills/python-ai-tools-code-builder skills/mcp-builder
git commit -m "Add: Phase-2 reference seeding for python-ai-code-builder, python-ai-tools-code-builder and mcp-builder [GS-254]"
```

---

### Task 2: `python-ai-code-builder` skill

**Files:**
- Create: `skills/python-ai-code-builder/SKILL.md`
- Create: `skills/python-ai-code-builder/evals/evals.json`
- Create: `playground/gs-billing-app/ai-fixtures/lib/models/ai_chatbot/ai_gpt_fn_index.py` (eval-2 fixture; content in Step 3)
- Modify: `.claude-plugin/marketplace.json`, `CLAUDE.md`

**Interfaces:**
- Consumes: `skills/python-ai-code-builder/references/**` (Task 1).
- Produces: the skill; its skeleton `ai_gpt_fn_index.py` defines `assign_app_specific_gpt_functions(app_context)` — the exact hook name Task 3's registration edits extend and the assistant router imports.

- [ ] **Step 1: Write `skills/python-ai-code-builder/SKILL.md`**

````markdown
---
name: python-ai-code-builder
description: Wire the GenericSuite AI assistant into a Python backend — generates the FastAPI ai_assistant router (chatbot, image-to-text, voice-to-text endpoints backed by genericsuite-be-ai), a skeleton GPT-functions index, main.py wiring and the AI env-var checklist. Use when the user wants to add the AI chatbot/assistant to a GenericSuite backend. For the assistant's app-specific tools, use python-ai-tools-code-builder afterwards.
argument-hint: [project-root]
---

Wire the GenericSuite AI assistant into a backend, following the canonical
patterns bundled under `references/`:

- `references/routers/ai_assistant.py` — the full assistant router
  (chatbot, image_to_text, voice_to_text) from fastapitemplate
- `references/models/ai_gpt_fn_index.py` — a POPULATED GPT-functions index
  (exampleapp); this skill generates the skeleton version below
- `references/main.py` — router registration idiom

READ the reference files before generating. Architecture rules:

1. The heavy lifting lives in `genericsuite_ai` (`ai_chatbot_endpoint`,
   `vision_image_analyzer_endpoint`, `transcribe_audio_endpoint` model
   functions) — the generated router only adapts FastAPI requests and
   passes the app-specific hook `assign_app_specific_gpt_functions`.
2. The index module is the single registration point for app tools; this
   skill creates it EMPTY (skeleton) so the assistant works with the
   built-in GenericSuite functions; `python-ai-tools-code-builder` fills it.
3. Standard result shape everywhere:
   `{"error": bool, "error_message": str | None, "resultset": Any}`.

## Step 1 — Gather inputs

1. **Project root**: where `lib/` lives (default `server/` for
   fastapitemplate-style, `apps/api-fastapi/` for exampleapp-style).
   Output to `playground/` when testing this skill.
2. **Existing state**: check whether `lib/routers/ai_assistant.py` and
   `lib/models/ai_chatbot/ai_gpt_fn_index.py` already exist. Never
   overwrite an existing index (it may hold registered tools) — report
   and leave it; the router may be regenerated if the user confirms.
3. **AI features wanted**: chatbot only, or also image-to-text (vision)
   and voice-to-text (transcription)? Default: all three.

## Step 2 — Generate the assistant router

File: `lib/routers/ai_assistant.py`. Copy the structure of
`references/routers/ai_assistant.py` VERBATIM, adjusting only:

- Omit the endpoint functions for features the user declined (keep
  `/chatbot` always).
- Keep these exact idioms: `router = BlueprintOne()`; each endpoint builds
  `gs_request, other_params = get_default_fa_request(...)`, calls
  `router.set_current_request(request, gs_request)`, then delegates to the
  `genericsuite_ai` model function with
  `additional_callable=assign_app_gpt_functions` (imported from
  `lib.models.ai_chatbot.ai_gpt_fn_index` as
  `assign_app_specific_gpt_functions`).
- The chatbot endpoint passes `sendfile_callable=send_file_fa` and
  `background_tasks=background_tasks`.

## Step 3 — Generate the skeleton GPT-functions index

File: `lib/models/ai_chatbot/ai_gpt_fn_index.py` (plus
`lib/models/ai_chatbot/__init__.py` if the folder is new). Skip if it
already exists.

```python
"""
AI Langchain Tools and GPT functions management
"""
from genericsuite.util.app_logger import log_debug
from genericsuite.util.app_context import AppContext

from genericsuite_ai.lib.ai_gpt_functions import (
    get_functions_dict,
)

from lib.config.config import Config

DEBUG = False


def assign_app_specific_gpt_functions(
    app_context: AppContext,
) -> None:
    """
    Assign app-specific GPT functions to the assistant.
    """
    app_context.set_other_data(
        'additional_function_dict',
        get_additional_functions_dict)
    app_context.set_other_data(
        'additional_func_context',
        additional_gpt_func_appcontexts)
    app_context.set_other_data(
        'additional_run_one_function',
        additional_run_one_function)
    app_context.set_other_data(
        'additional_function_specs',
        get_additional_function_specs)


def get_additional_functions_dict(
    app_context: AppContext,
) -> dict:
    """
    App-specific tools/GPT-functions registry.
    Filled by the python-ai-tools-code-builder skill.
    """
    settings = Config(app_context)
    is_lc = settings.AI_TECHNOLOGY == 'langchain'
    if is_lc:
        # Langchain Tools (the @tool-decorated callables)
        result = {}
    else:
        # GPT Functions (the plain *_func callables)
        result = {}
    return result


def additional_gpt_func_appcontexts(
    app_context: AppContext,
) -> list:
    """
    CommonAppContext (cac) objects of every app tool module.
    Filled by the python-ai-tools-code-builder skill.
    """
    return []


def additional_run_one_function(
    app_context: AppContext,
    function_name: str,
    function_args: dict,
) -> dict:
    """
    Dispatch one GPT function call by name (non-LangChain mode).
    Filled by the python-ai-tools-code-builder skill.
    """
    available_functions = get_functions_dict(app_context)
    _ = DEBUG and log_debug(
        f'RUN_ONE_FUNCTION | function_name: {function_name}'
        f' | function_args: {function_args}')
    function_response = None
    # <python-ai-tools-code-builder: add one elif per tool here>
    return function_response


def get_additional_function_specs(
    app_context: AppContext,
) -> list:
    """
    OpenAI function-calling specs for the app tools (non-LangChain mode).
    Filled by the python-ai-tools-code-builder skill.
    """
    return []
```

## Step 4 — Wiring snippet and env checklist

Output (or apply on confirmation) the `lib/main.py` addition:

```python
from lib.routers import ai_assistant as ai_chatbot_endpoint

app.include_router(
    ai_chatbot_endpoint.router,
    prefix=f'/{settings.API_VERSION}/ai')
```

Env-var checklist for the project `.env` (values are placeholders — never
write real secrets):

```bash
OPENAI_API_KEY=<your key>
AI_TECHNOLOGY=langchain            # or 'openai' for raw function calling
AWS_S3_CHATBOT_ATTACHMENTS_BUCKET_QA=<bucket for chat attachments>
```

Point the user to the GenericSuite AI backend docs
(Backend-Development/GenericSuite-AI, Configuration section) for provider
and model selection variables.

## Step 5 — Verify and summarize

1. `python3 -m py_compile` every generated file — exit 0.
2. `grep -n "^from fastapi\|^import fastapi" lib/models/ai_chatbot/ai_gpt_fn_index.py`
   must return nothing (the index is framework-agnostic).
3. Summarize files created/skipped, the main.py snippet, the env checklist.
4. Next steps: `/python-ai-tools-code-builder` to add app-specific tools;
   `/mcp-builder` to expose them over MCP.
````

- [ ] **Step 2: Write `skills/python-ai-code-builder/evals/evals.json`**

```json
{
    "skill_name": "python-ai-code-builder",
    "evals": [
        {
            "id": 1,
            "prompt": "Wire the GenericSuite AI assistant into a fresh backend: all three features (chatbot, image-to-text, voice-to-text). Project root: playground/python-ai-code-builder-test/eval-1/",
            "expected_output": "lib/routers/ai_assistant.py, skeleton lib/models/ai_chatbot/ai_gpt_fn_index.py (+__init__.py), main.py wiring snippet and env checklist",
            "files": [],
            "expectations": [
                "Creates lib/routers/ai_assistant.py and lib/models/ai_chatbot/ai_gpt_fn_index.py under the output root",
                "All generated .py files pass python3 -m py_compile (runtime validity)",
                "The router imports assign_app_specific_gpt_functions from lib.models.ai_chatbot.ai_gpt_fn_index and passes it as additional_callable",
                "The router has /chatbot, /image_to_text and /voice_to_text POST endpoints using BlueprintOne, get_default_fa_request and set_current_request",
                "The index defines assign_app_specific_gpt_functions, get_additional_functions_dict (both is_lc branches returning empty dicts), additional_gpt_func_appcontexts returning [], additional_run_one_function and get_additional_function_specs",
                "The index does NOT import fastapi",
                "Outputs a main.py snippet with app.include_router and prefix f'/{settings.API_VERSION}/ai'",
                "Outputs an env checklist naming OPENAI_API_KEY with placeholder values only (no real-looking secrets)"
            ]
        },
        {
            "id": 2,
            "prompt": "Wire the GenericSuite AI assistant (chatbot only) into a backend that ALREADY has a populated GPT-functions index at playground/gs-billing-app/ai-fixtures/lib/models/ai_chatbot/ai_gpt_fn_index.py. Copy that fixture tree to playground/python-ai-code-builder-test/eval-2/lib/models/ai_chatbot/ first, then run against project root playground/python-ai-code-builder-test/eval-2/",
            "expected_output": "Only the router is generated; the existing index is detected and left byte-for-byte untouched",
            "files": [
                "playground/gs-billing-app/ai-fixtures/lib/models/ai_chatbot/ai_gpt_fn_index.py"
            ],
            "expectations": [
                "Creates lib/routers/ai_assistant.py with the /chatbot endpoint (and no /image_to_text or /voice_to_text endpoints, since only chatbot was requested)",
                "Generated router passes python3 -m py_compile (runtime validity)",
                "The existing ai_gpt_fn_index.py is byte-identical to the fixture after the run (not regenerated, not reformatted)",
                "Reports that the index already existed and was preserved"
            ]
        }
    ]
}
```

- [ ] **Step 3: Create the eval-2 fixture `playground/gs-billing-app/ai-fixtures/lib/models/ai_chatbot/ai_gpt_fn_index.py`**

Use the skeleton from SKILL.md Step 3 verbatim, with ONE modification so it is detectably "populated": in `get_additional_functions_dict`, replace both `result = {}` lines with `result = {"get_invoice_status": get_invoice_status}` / `result = {"get_invoice_status": get_invoice_status_func}` and add this import block after the `Config` import:

```python
from lib.models.ai_chatbot.ai_gpt_fn_billing import (
    cac as cac_billing,
    get_invoice_status,
    get_invoice_status_func,
)
```

and make `additional_gpt_func_appcontexts` return `[cac_billing]`. (The fixture intentionally imports a module that does not exist on disk — it is never executed, only compared byte-for-byte; do not py_compile-import it, `py_compile` only checks syntax and will pass.)

- [ ] **Step 4: Validate**

Run:
```bash
(cd skills/skill-creator && python3 -m scripts.quick_validate ../../skills/python-ai-code-builder)
python3 -m py_compile playground/gs-billing-app/ai-fixtures/lib/models/ai_chatbot/ai_gpt_fn_index.py
python3 -c "import json; json.load(open('skills/python-ai-code-builder/evals/evals.json')); print('OK')"
```
Expected: skill valid (exit 0); fixture compiles; `OK`.

- [ ] **Step 5: Register the skill**

`.claude-plugin/marketplace.json` — add `"./skills/python-ai-code-builder"` to the `code-generation-skills` skills array (alphabetical). `CLAUDE.md` table row (alphabetical):

```markdown
| `skills/python-ai-code-builder/` | Wires the GenericSuite AI assistant into a backend (router, skeleton GPT-functions index, env checklist) |
```

Run: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('OK')"` → `OK`.

- [ ] **Step 6: Commit (if commits enabled)**

```bash
git add skills/python-ai-code-builder playground/gs-billing-app/ai-fixtures .claude-plugin/marketplace.json CLAUDE.md
git commit -m "Add: python-ai-code-builder skill — AI assistant wiring with skeleton GPT-functions index, evals and fixture [GS-254]"
```

---

### Task 3: `python-ai-tools-code-builder` skill

**Files:**
- Create: `skills/python-ai-tools-code-builder/SKILL.md`
- Create: `skills/python-ai-tools-code-builder/evals/evals.json`
- Modify: `.claude-plugin/marketplace.json`, `CLAUDE.md`

**Interfaces:**
- Consumes: `skills/python-ai-tools-code-builder/references/**` (Task 1); the skeleton index hook names from Task 2 (`assign_app_specific_gpt_functions`, `get_additional_functions_dict`, `additional_gpt_func_appcontexts`, `additional_run_one_function`, `get_additional_function_specs`).
- Produces: the skill; its output convention — every `@tool` has a plain `<name>_func` companion and a module-level `cac = CommonAppContext()` — is what Task 4's mcp-builder consumes.

- [ ] **Step 1: Write `skills/python-ai-tools-code-builder/SKILL.md`**

````markdown
---
name: python-ai-tools-code-builder
description: Generate app-specific AI tools (LangChain @tool functions with plain *_func companions) for the GenericSuite AI assistant, and register them in the GPT-functions index (ai_gpt_fn_index.py). Use when the user wants the assistant to perform app actions — query entities, call external APIs, create records. Requires the assistant wiring from python-ai-code-builder to exist. The *_func companions are later wrapped by mcp-builder.
argument-hint: [tool-name ...]
---

Generate GenericSuite AI tool modules and register them, following the
canonical patterns bundled under `references/`:

- `references/ai_gpt_fn_fda.py` — tool module wrapping an external API
  (Pydantic params schema, @tool + _func pair, cac, translation support)
- `references/ai_gpt_fn_app.py` — tool module with many DB-backed tools
  and exported prompt functions
- `references/ai_gpt_fn_index.py` — a POPULATED index showing every
  registration point

READ the reference files before generating. Conventions (non-negotiable):

1. **Every tool is a pair**: `@tool`-decorated `<name>` (LangChain) that
   delegates to a plain `<name>_func` (used in raw GPT-function mode and
   wrapped by the MCP server). The `_func` holds ALL the logic.
2. **Module-level `cac = CommonAppContext()`** — the index propagates the
   app context into it.
3. **Params**: a Pydantic `BaseModel` schema per tool;
   `interpret_tool_params(tool_params=params, first_param_name=..., schema=...)`
   normalizes the input.
4. **Errors**: return `gpt_func_error(<message>)` on failure; results are
   strings or JSON-dumped dicts of the standard result shape.
5. **Security**: any URL that comes from tool params or AI output must be
   checked with `is_safe_url()` before fetching; any local path with
   `is_safe_local_path()`. Never log raw user input (sanitize newlines).

## Step 1 — Gather requirements

1. **Domain name** (snake_case): becomes the module
   `lib/models/ai_chatbot/ai_gpt_fn_<domain>.py`.
2. **Tools**: for each — name (snake_case verb phrase), one-line purpose,
   parameters (name, type, required, default), and what it calls
   (existing model function? DB middleware? external API?).
3. **Project root** and whether `lib/models/ai_chatbot/ai_gpt_fn_index.py`
   exists (it must — if missing, run `python-ai-code-builder` first).
4. **Translation**: should text params be translated to the user's
   language (`lang_translate`)? Default no.

## Step 2 — Generate the tool module

File: `lib/models/ai_chatbot/ai_gpt_fn_<domain>.py`. One block per tool:

```python
"""
<Domain> AI Tools
"""
from typing import Optional, Any
import json

from langchain.tools import tool
from pydantic import BaseModel, Field

from genericsuite.util.app_context import CommonAppContext
from genericsuite.util.app_logger import log_debug

from genericsuite_ai.lib.ai_langchain_tools import (
    interpret_tool_params,
)
from genericsuite_ai.lib.ai_utilities import (
    gpt_func_error,
)

DEBUG = False
cac = CommonAppContext()


class <ToolName>Params(BaseModel):
    """
    <tool_name> parameters
    """
    <param>: <type> = Field(description="<param description>")
    <optional_param>: Optional[<type>] = Field(
        None, description="<param description>")


@tool
def <tool_name>(params: Any) -> str:
    """
<One-line description the LLM reads to decide when to call this tool.>
Args: params (dict): Tool parameters. Must have: "<param>" (<type>): <description>.
    """  # noqa: E501
    return <tool_name>_func(params)


def <tool_name>_func(params: Any) -> str:
    """
    <What it does.>
    """
    params = interpret_tool_params(
        tool_params=params,
        first_param_name="<param>",
        schema=<ToolName>Params)
    <param> = params.<param>
    # ... business logic; on failure:
    #     return gpt_func_error('<what failed>')
    # On success return a string or json.dumps(result)
    result = {"error": False, "error_message": None, "resultset": {}}
    return json.dumps(result)
```

For DB access inside `_func` bodies, use the same three approaches as the
`python-fastapi-code-builder` skill (fetch_all_from_db /
GenericDbHelper / GenericDbHelperSuper) — see
`references/ai_gpt_fn_app.py` for `fetch_all_from_db` and
`add_item_to_db` working idioms with `cac.app_context`.

## Step 3 — Register in the index

Edit `lib/models/ai_chatbot/ai_gpt_fn_index.py` — five registration
points, all of them, idempotently (skip any already present):

1. **Imports** (after the `Config` import):
```python
from lib.models.ai_chatbot.ai_gpt_fn_<domain> import (
    cac as cac_<domain>,
    <tool_name>,
    <tool_name>_func,
)
```
2. **`get_additional_functions_dict`** — add to BOTH branches:
   `"<tool_name>": <tool_name>` in the `is_lc` dict and
   `"<tool_name>": <tool_name>_func` in the else dict.
3. **`additional_gpt_func_appcontexts`** — add `cac_<domain>` to the list.
4. **`additional_run_one_function`** — one `elif` per tool:
```python
    elif function_name == "<tool_name>":
        function_response = fuction_to_call(
            params={
                "<param>": function_args.get("<param>"),
            }
        )
```
   (If the function body still has the skeleton's
   `# <python-ai-tools-code-builder: add one elif per tool here>` marker
   and no prior branches, convert the first tool to `if` instead of
   `elif` and keep the marker below the last branch.)
5. **`get_additional_function_specs`** — append one OpenAI
   function-calling spec dict per tool:
```python
        {
            "name": "<tool_name>",
            "description": "<one-line description>",
            "parameters": {
                "type": "object",
                "properties": {
                    "<param>": {
                        "type": "<json_type>",
                        "description": "<param description>",
                    },
                },
                "required": ["<param>"],
            },
        },
```

## Step 4 — Verify and summarize

1. `python3 -m py_compile` on the tool module AND the edited index.
2. `grep -n "^from fastapi\|^import fastapi"` on both — must return
   nothing.
3. Cross-check: every tool name appears in both branches of
   `get_additional_functions_dict`, in `additional_run_one_function`, and
   in `get_additional_function_specs`; `cac_<domain>` is in
   `additional_gpt_func_appcontexts`.
4. Summarize tools created, registrations applied/skipped.
5. Next step: `/mcp-builder` to expose the new tools over MCP.
````

- [ ] **Step 2: Write `skills/python-ai-tools-code-builder/evals/evals.json`**

```json
{
    "skill_name": "python-ai-tools-code-builder",
    "evals": [
        {
            "id": 1,
            "prompt": "Create AI tools for the billing domain: (1) search_customer_invoices — search a customer's invoices by customer name (string, required); (2) get_overdue_invoice_count — count invoices past due date, no parameters. Both read the DB through the GenericSuite middleware against json_file 'invoices'. The project already has the skeleton index: copy playground/python-ai-code-builder-test/eval-1/lib/ to playground/python-ai-tools-code-builder-test/eval-1/lib/ first if it exists, otherwise copy playground/gs-billing-app/ai-fixtures/lib/ and remove the ai_gpt_fn_billing import block, functions-dict entries and cac_billing reference from the copied index to restore the empty skeleton. Project root: playground/python-ai-tools-code-builder-test/eval-1/",
            "expected_output": "lib/models/ai_chatbot/ai_gpt_fn_billing.py with two @tool/_func pairs, and the index updated at all five registration points",
            "files": [],
            "expectations": [
                "Creates lib/models/ai_chatbot/ai_gpt_fn_billing.py with search_customer_invoices, search_customer_invoices_func, get_overdue_invoice_count, get_overdue_invoice_count_func and a module-level cac = CommonAppContext()",
                "Tool module and edited ai_gpt_fn_index.py both pass python3 -m py_compile (runtime validity)",
                "Both tools use interpret_tool_params with a Pydantic schema and return gpt_func_error(...) on failure paths",
                "The index imports cac as cac_billing plus both tool pairs, registers both tools in BOTH is_lc branches of get_additional_functions_dict, includes cac_billing in additional_gpt_func_appcontexts, has a dispatch branch per tool in additional_run_one_function, and one spec per tool in get_additional_function_specs",
                "Neither file imports fastapi"
            ]
        },
        {
            "id": 2,
            "prompt": "Create an AI tool fetch_exchange_rate for the finance domain: it receives a currency code (string, required) and fetches https://api.frankfurter.dev/v1/latest?base=<code> with requests.get. The URL must be validated before fetching. Use a fresh skeleton index: copy playground/gs-billing-app/ai-fixtures/lib/ to playground/python-ai-tools-code-builder-test/eval-2/lib/ and strip the billing-specific registrations from the index first. Project root: playground/python-ai-tools-code-builder-test/eval-2/",
            "expected_output": "lib/models/ai_chatbot/ai_gpt_fn_finance.py with the tool pair, URL guarded by is_safe_url, index registered",
            "files": [],
            "expectations": [
                "Creates lib/models/ai_chatbot/ai_gpt_fn_finance.py with fetch_exchange_rate and fetch_exchange_rate_func",
                "Both generated/edited .py files pass python3 -m py_compile (runtime validity)",
                "The _func validates the request URL with is_safe_url before calling requests.get, and returns gpt_func_error(...) when the check fails",
                "The index has all five registration points updated for fetch_exchange_rate",
                "No network call is executed during generation"
            ]
        }
    ]
}
```

- [ ] **Step 3: Validate**

Run:
```bash
(cd skills/skill-creator && python3 -m scripts.quick_validate ../../skills/python-ai-tools-code-builder)
python3 -c "import json; json.load(open('skills/python-ai-tools-code-builder/evals/evals.json')); print('OK')"
```
Expected: skill valid; `OK`.

- [ ] **Step 4: Register the skill**

marketplace.json: add `"./skills/python-ai-tools-code-builder"` (alphabetical). CLAUDE.md row:

```markdown
| `skills/python-ai-tools-code-builder/` | Generates LangChain @tool/_func pairs for the AI assistant and registers them in ai_gpt_fn_index.py |
```

Run: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('OK')"` → `OK`.

- [ ] **Step 5: Commit (if commits enabled)**

```bash
git add skills/python-ai-tools-code-builder .claude-plugin/marketplace.json CLAUDE.md
git commit -m "Add: python-ai-tools-code-builder skill — LangChain tool/_func pairs with full index registration, evals [GS-254]"
```

---

### Task 4: `mcp-builder` skill

**Files:**
- Create: `skills/mcp-builder/SKILL.md`
- Create: `skills/mcp-builder/evals/evals.json`
- Create: `playground/gs-billing-app/ai-fixtures/lib/models/ai_chatbot/ai_gpt_fn_billing.py` (eval fixture; Step 3)
- Modify: `.claude-plugin/marketplace.json`, `CLAUDE.md`

**Interfaces:**
- Consumes: `skills/mcp-builder/references/**` (Task 1); the tool-module convention from Task 3 (`<name>_func` companions, module-level `cac`).
- Produces: the skill (`/mcp-builder [project-root]`).

- [ ] **Step 1: Write `skills/mcp-builder/SKILL.md`**

````markdown
---
name: mcp-builder
description: Build or extend a GenericSuite MCP server that exposes the app's AI tools (the *_func companions generated by python-ai-tools-code-builder) and optionally CRUD entities as MCP tools, with authentication, prompts and Claude Desktop / VS Code client configs. Use when the user wants their GenericSuite backend reachable from MCP clients. Re-runnable: adds wrappers for new tools without duplicating existing ones.
argument-hint: [project-root]
---

Build the project's MCP server, following the canonical patterns bundled
under `references/`:

- `references/mcp_server_full_example.py` — exampleapp's complete server
  (auth tools, many tool wrappers, prompts, resources)
- `references/mcp_server_minimal.py` — fastapitemplate's minimal starter
- `references/mcp-server-package.json`, `references/mcp-server-README.md`
  — mcp-server directory scaffolding
- `references/claude_desktop_{stdio,http}_config.json`,
  `references/vscode_mcp_{stdio,http}_config.json` — client config
  STRUCTURE only. WARNING: these carry stale `genericsuite-codegen`
  names/paths from an earlier template — always generate configs with the
  TARGET app's own name, paths and env var names.

READ the reference files before generating. Conventions:

1. The server is built with
   `genericsuite.mcplib.util.create_app.create_app(app_name=..., settings=..., log_file=...)`;
   `mcp = app.mcp`.
2. Every app AI tool is wrapped as an async `@mcp.tool()` that: declares
   TYPED parameters (not a params dict — MCP clients need the schema),
   calls `verify_app_context(app, cac_object_list)`, delegates to the
   tool's `<name>_func({...})`, and returns
   `tool_result(result)` (optionally with a metadata dict).
3. `cac_object_list` collects the `cac` object imported from EVERY tool
   module (`from lib.models.ai_chatbot.ai_gpt_fn_<domain> import cac as
   cac_<domain>`).
4. Standard auth block always present: `get_api_keys()` tool exposing
   `GS_USER_ID`/`GS_USER_NAME`/`GS_API_KEY` env vars, an
   `authentication_tool(username, password)` using
   `mcp_authenticate(app, cac_object_list, username, password)` /
   `verify_app_context`, and the `user://login/{username}/{password}`
   resource.
5. If a tool module exports prompt functions, wrap each as
   `@mcp.prompt("<name>")`.
6. Entry point: `def main(): app.run()` guarded by
   `if __name__ == "__main__":`.

## Step 1 — Gather inputs

1. **Project root** (where `lib/` lives) and the **mcp-server location**:
   `server/lib/mcp_server.py` for fastapitemplate-style single-package
   projects, or a sibling `mcp-server/mcp_server.py` directory for
   exampleapp-style monorepos (then scaffold the directory).
2. **Tool modules**: scan `lib/models/ai_chatbot/ai_gpt_fn_*.py`
   (excluding `ai_gpt_fn_index.py`) and list every `<name>_func`; confirm
   with the user which to expose (default: all).
3. **CRUD entities** (optional): which entries from
   `config_dbdef/backend/endpoints.json` to expose as list/get/create/
   update/delete MCP tools (default: none).
4. **Existing server?** If `mcp_server.py` exists, operate in EXTEND mode:
   only add missing imports, `cac_<domain>` entries and `@mcp.tool()`
   wrappers — never duplicate a wrapper whose function name already
   exists, never reorder existing code.

## Step 2 — Generate or extend `mcp_server.py`

New-server skeleton (adapt names; wrappers per Step 3):

```python
#!/usr/bin/env python3
"""
MCP Server
A Model Context Protocol server that exposes <app_name>'s
tools to AI clients.
"""
from typing import Dict, Any
import os

from genericsuite.util.app_logger import log_info
from genericsuite.mcplib.util.create_app import create_app
from genericsuite.mcplib.util.utilities import (
    mcp_authenticate,
    verify_app_context,
    tool_result,
)

from lib.config.config import Config
from lib.models.ai_chatbot.ai_gpt_fn_<domain> import (
    cac as cac_<domain>,
    <tool_name>_func,
)

DEBUG = False

settings = Config()
app = create_app(app_name=f'{settings.APP_NAME.lower()}-mcp-server',
                 settings=settings, log_file='./logs/mcp_server.log')
mcp = app.mcp
cac_object_list = [cac_<domain>]


@mcp.tool()
async def get_api_keys() -> Dict[str, Any]:
    """
    Get API keys
    """
    _ = DEBUG and log_info("Getting API keys")
    return {
        "resultset": {
            "GS_USER_ID": os.environ.get("GS_USER_ID"),
            "GS_USER_NAME": os.environ.get("GS_USER_NAME"),
            "GS_API_KEY": os.environ.get("GS_API_KEY")
        }
    }


@mcp.tool()
async def authentication_tool(
    username: str,
    password: str,
) -> str:
    """
    Authenticate user
    """
    _ = DEBUG and log_info("Authenticating user")
    if not username and not password:
        if verify_app_context(app, cac_object_list):
            return tool_result("User already authenticated with API key")
        return tool_result("Username and password are required")
    return mcp_authenticate(app, cac_object_list, username, password)


@mcp.resource("user://login/{username}/{password}",
              mime_type="application/json")
async def authenticate(
    username: str,
    password: str,
) -> str:
    """
    Get user login as a resource
    """
    return mcp_authenticate(app, cac_object_list, username, password)


# <tool wrappers go here — one per exposed *_func, see Step 3>


def main():
    """
    Main entry point for the MCP Server
    """
    print(f"Starting {settings.APP_NAME} MCP Server...")
    app.run()


if __name__ == "__main__":
    main()
```

## Step 3 — Tool wrappers

One wrapper per exposed `_func`, with typed parameters mirroring the
tool's Pydantic schema (required params first, optional ones with
defaults):

```python
@mcp.tool()
async def <tool_name>(
    <param>: <type>,
    <optional_param>: <type> = <default>,
) -> Dict[str, Any]:
    """
    <Docstring the MCP client shows — copy the tool's purpose line.>
    """
    _ = DEBUG and log_info(f"<tool_name>: {<param>}")
    verify_app_context(app, cac_object_list)
    result = <tool_name>_func({
        "<param>": <param>,
        "<optional_param>": <optional_param>,
    })
    return tool_result(result)
```

Prompt functions (when the tool module exports them):

```python
@mcp.prompt("<prompt_name>")
async def <prompt_name>_prompt(
    <param>: str = "<default>",
) -> str:
    """
    <What the prompt template is for.>
    """
    verify_app_context(app, cac_object_list)
    return <prompt_name>_prompt_func(<param>=<param>)
```

Optional CRUD wrappers (per selected entity, delegating to the
GenericSuite DB middleware through a `_func`-style helper the skill also
generates in `lib/models/ai_chatbot/ai_gpt_fn_<entity>_crud.py` following
the python-ai-tools-code-builder conventions) — only when the user asked
for CRUD exposure in Step 1.

## Step 4 — Scaffolding (new mcp-server directory only)

When creating a sibling `mcp-server/` directory, also generate:

- `package.json` — adapt `references/mcp-server-package.json`, replacing
  the app name/repo URLs with the target app's.
- Client configs — `claude_desktop_stdio_config.json`,
  `claude_desktop_http_config.json`, `vscode_mcp_stdio_config.json`,
  `vscode_mcp_http_config.json` — same JSON structure as the references
  but with the target app's server name, absolute-path placeholder
  (`/absolute/path/to/<app>/mcp-server/run_mcp_server.sh`) and
  `MCP_API_KEY=<your-api-key>` placeholder.
- `README.md` — adapt `references/mcp-server-README.md` run instructions.

## Step 5 — Verify and summarize

1. `python3 -m py_compile mcp_server.py` — exit 0.
2. Cross-check: every exposed `_func` has exactly ONE `@mcp.tool()`
   wrapper; every imported tool module's `cac` is in `cac_object_list`;
   generated JSON configs parse (`python3 -c "import json, ..."`).
3. In EXTEND mode: diff summary — wrappers added vs. skipped as already
   present.
4. Summarize files created, how to run (`python3 mcp_server.py` or the
   package.json scripts), and where to paste the client configs.
````

- [ ] **Step 2: Write `skills/mcp-builder/evals/evals.json`**

```json
{
    "skill_name": "mcp-builder",
    "evals": [
        {
            "id": 1,
            "prompt": "Build an MCP server for the gs-billing-app backend. Its AI tools live in playground/gs-billing-app/ai-fixtures/lib/models/ai_chatbot/ai_gpt_fn_billing.py (copy the whole playground/gs-billing-app/ai-fixtures/lib/ tree to playground/mcp-builder-test/eval-1/lib/ first). Expose all tools; no CRUD entities. Create the server as playground/mcp-builder-test/eval-1/mcp-server/mcp_server.py with the full sibling-directory scaffolding (package.json, client configs, README).",
            "expected_output": "mcp_server.py wrapping get_invoice_status_func plus auth tools, and the mcp-server directory scaffolding with app-specific names",
            "files": [
                "playground/gs-billing-app/ai-fixtures/lib/models/ai_chatbot/ai_gpt_fn_billing.py"
            ],
            "expectations": [
                "Creates mcp-server/mcp_server.py that passes python3 -m py_compile (runtime validity)",
                "The server imports cac as cac_billing and get_invoice_status_func from lib.models.ai_chatbot.ai_gpt_fn_billing, and cac_billing is in cac_object_list",
                "Has an async @mcp.tool() get_invoice_status with a typed invoice_id parameter that calls verify_app_context, delegates to get_invoice_status_func({...}) and returns tool_result(result)",
                "Has the standard auth block: get_api_keys tool, authentication_tool using mcp_authenticate, and the user://login resource",
                "All four client config JSON files parse and contain the app's own server name — none contain the string 'genericsuite-codegen' (runtime validity + stale-template check)",
                "package.json parses as valid JSON"
            ]
        },
        {
            "id": 2,
            "prompt": "EXTEND an existing MCP server: first copy playground/mcp-builder-test/eval-1/ (produced by eval 1; if absent, build it per eval 1 first) to playground/mcp-builder-test/eval-2/. A new tool module playground/mcp-builder-test/eval-2/lib/models/ai_chatbot/ai_gpt_fn_finance.py must be created first as a copy of ai_gpt_fn_billing.py with get_invoice_status renamed to fetch_exchange_rate everywhere (including the cac import alias context). Then run mcp-builder on playground/mcp-builder-test/eval-2/ to add the new tool to mcp-server/mcp_server.py.",
            "expected_output": "mcp_server.py gains the fetch_exchange_rate wrapper and cac_finance; the existing get_invoice_status wrapper is untouched and not duplicated",
            "files": [],
            "expectations": [
                "The extended mcp_server.py passes python3 -m py_compile (runtime validity)",
                "Contains exactly ONE @mcp.tool() wrapper for get_invoice_status and exactly ONE for fetch_exchange_rate (no duplicates)",
                "cac_object_list contains both cac_billing and cac_finance",
                "Reports which wrappers were added and which were skipped as already present"
            ]
        }
    ]
}
```

- [ ] **Step 3: Create the eval fixture `playground/gs-billing-app/ai-fixtures/lib/models/ai_chatbot/ai_gpt_fn_billing.py`**

```python
"""
Billing AI Tools (eval fixture)
"""
from typing import Any
import json

from langchain.tools import tool
from pydantic import BaseModel, Field

from genericsuite.util.app_context import CommonAppContext

from genericsuite_ai.lib.ai_langchain_tools import (
    interpret_tool_params,
)
from genericsuite_ai.lib.ai_utilities import (
    gpt_func_error,
)

DEBUG = False
cac = CommonAppContext()


class InvoiceStatusParams(BaseModel):
    """
    get_invoice_status parameters
    """
    invoice_id: str = Field(description="Invoice ID to look up")


@tool
def get_invoice_status(params: Any) -> str:
    """
Useful to get the current status of an invoice by its ID.
Args: params (dict): Tool parameters. Must have: "invoice_id" (str): invoice ID.
    """  # noqa: E501
    return get_invoice_status_func(params)


def get_invoice_status_func(params: Any) -> str:
    """
    Get the current status of an invoice by its ID.
    """
    params = interpret_tool_params(
        tool_params=params,
        first_param_name="invoice_id",
        schema=InvoiceStatusParams)
    invoice_id = params.invoice_id
    if not invoice_id:
        return gpt_func_error('invoice_id is required')
    result = {
        "error": False,
        "error_message": None,
        "resultset": {"invoice_id": invoice_id, "status": "paid"},
    }
    return json.dumps(result)
```

(This fixture is also what makes Task 2's eval-2 index fixture coherent: that index imports `ai_gpt_fn_billing`, which now exists in the same fixture tree.)

- [ ] **Step 4: Validate**

Run:
```bash
(cd skills/skill-creator && python3 -m scripts.quick_validate ../../skills/mcp-builder)
python3 -m py_compile playground/gs-billing-app/ai-fixtures/lib/models/ai_chatbot/ai_gpt_fn_billing.py
python3 -c "import json; json.load(open('skills/mcp-builder/evals/evals.json')); print('OK')"
```
Expected: skill valid; fixture compiles; `OK`.

- [ ] **Step 5: Register the skill**

marketplace.json: add `"./skills/mcp-builder"` (alphabetical — after `jsx-code-builder`, before `menu-builder`). CLAUDE.md row:

```markdown
| `skills/mcp-builder/` | Builds/extends the MCP server exposing the app's AI tools (*_func wrappers, auth, prompts, client configs) |
```

Run: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('OK')"` → `OK`.

- [ ] **Step 6: Commit (if commits enabled)**

```bash
git add skills/mcp-builder playground/gs-billing-app/ai-fixtures .claude-plugin/marketplace.json CLAUDE.md
git commit -m "Add: mcp-builder skill — MCP server generation from AI tool *_func companions, with evals and fixtures [GS-254]"
```

---

### Task 5: Eval smoke run (all three skills)

**Files:**
- Create (transient, not committed): `playground/python-ai-code-builder-test/`, `playground/python-ai-tools-code-builder-test/`, `playground/mcp-builder-test/`

**Interfaces:**
- Consumes: evals.json of Tasks 2–4.
- Produces: pass/fail evidence per expectation; accept/iterate decision.

- [ ] **Step 1: Execute the 6 eval prompts with each skill loaded**

Dispatch one subagent per eval: prompt = the eval's `prompt` verbatim, prefixed with the instruction to read and follow the corresponding SKILL.md, acting autonomously (infer answers to "ask the user" steps from the eval prompt; no git commands; no network calls). ORDER MATTERS: run python-ai-code-builder eval 1 BEFORE python-ai-tools-code-builder eval 1 (which copies its output), and mcp-builder eval 1 BEFORE mcp-builder eval 2 (which copies its output). The other evals are independent.

- [ ] **Step 2: Grade every expectation mechanically where possible**

```bash
# examples of the mechanical checks
python3 -m py_compile playground/python-ai-code-builder-test/eval-1/lib/routers/ai_assistant.py
grep -c "@mcp.tool()" playground/mcp-builder-test/eval-2/mcp-server/mcp_server.py
grep -c "async def get_invoice_status" playground/mcp-builder-test/eval-2/mcp-server/mcp_server.py   # expect 1
grep -L "genericsuite-codegen" playground/mcp-builder-test/eval-1/mcp-server/*_config.json
cmp playground/gs-billing-app/ai-fixtures/lib/models/ai_chatbot/ai_gpt_fn_index.py playground/python-ai-code-builder-test/eval-2/lib/models/ai_chatbot/ai_gpt_fn_index.py
python3 -c "import json,glob; [json.load(open(p)) for p in glob.glob('playground/mcp-builder-test/eval-1/mcp-server/*.json')]; print('OK')"
```

Non-mechanical expectations (e.g. "reports that the index already existed") are graded by reading the eval subagent's final message.

- [ ] **Step 3: Report and decide**

Per-skill pass-rate table to the user. 100% → accept. Any failure → fix the SKILL.md (not the expectation, unless the expectation is wrong), re-run that eval once; still failing → stop and discuss.

- [ ] **Step 4: Commit adjustments only (if commits enabled; skip when nothing changed)**

```bash
git status --short
git add skills/ playground/gs-billing-app/
git commit -m "Change: adjustments from Phase-2 eval smoke run [GS-254]"
```

---

## Follow-up plans (not in this document)

1. **Phase 3** — `jsx-ai-code-builder` (frontend AI wiring).
2. **Phase 4** — `app-starter` (wraps basecamp's `new-project-from-template.sh`).
3. **Phase 5** — `gs-app-builder` orchestrator + end-to-end playground app.
4. **Phase 6** — docs, CHANGELOG, `gs-app-builder-suite` plugin-group decision, publish to Claude Skills marketplace and skills.sh (GS-254 close-out).
