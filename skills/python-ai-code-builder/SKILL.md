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
  `additional_callable=assign_app_gpt_functions` (the router imports
  `assign_app_specific_gpt_functions` from
  `lib.models.ai_chatbot.ai_gpt_fn_index` aliased as
  `assign_app_gpt_functions`).
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
    fuction_to_call = available_functions[function_name]  # used by the per-tool branches below
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
