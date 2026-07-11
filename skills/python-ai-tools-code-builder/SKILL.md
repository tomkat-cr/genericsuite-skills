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
