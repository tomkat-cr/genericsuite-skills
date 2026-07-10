---
name: python-fastapi-code-builder
description: Generate GenericSuite Python backend code — custom FastAPI endpoints and business-logic model modules built on the genericsuite-be abstraction layer (GenericDbHelper, BlueprintOne, standard result shape). Use when the user needs a backend endpoint or feature beyond the generic CRUD handlers, such as wrapping an external API, computed/aggregate endpoints, or custom actions. Not for plain CRUD entities (use config-builder + endpoints-builder for those).
argument-hint: [feature-name]
---

Generate custom GenericSuite backend code following the canonical patterns
bundled under `references/`:

- `references/routers/fda_food_endpoint.py` — FastAPI router wrapping an
  external API (POST with JSON body)
- `references/routers/food_moments.py` — FastAPI router for entity-specific
  custom actions
- `references/models/fda_food_endpoint_model.py` — model (business logic)
  layer for the external-API case
- `references/models/food_moments_model.py` — model layer using
  GenericDbHelper for DB access
- `references/main.py` — how routers are registered with `include_router`

READ the relevant reference files before generating — they are the source of
truth for idioms. Key architecture rules (non-negotiable):

1. **Two layers, always**: `lib/routers/<feature>.py` (framework wiring,
   FastAPI-specific) + `lib/models/<domain>/<feature>.py` (business logic,
   framework-agnostic — written against `genericsuite.util.*`, never
   importing `fastapi`).
2. **Standard result shape**: every model function returns
   `{"error": bool, "error_message": str | None, "resultset": Any}` —
   usually via `return_resultset_jsonified_or_exception()`.
3. **DB access**: MongoDB-style query syntax only (the DbAbstractor
   translates); parameterized values, never string-built queries.
4. **Security**: never log raw user input (sanitize newlines first); wrap
   AI/user-provided URLs and paths with `is_safe_url()` /
   `is_safe_local_path()` from genericsuite; secrets only via `Config`
   (env vars), never hardcoded.

## Step 1 — Gather requirements

Ask the user:

1. **Feature name** (snake_case, becomes the module name) and one-line
   purpose.
2. **Domain folder**: subdirectory under `lib/models/` (e.g.
   `external_apis`, `billing`, `utilities`).
3. **HTTP method(s)** and request parameters (name, type, required,
   default).
4. **What it does**: external API call, DB read/aggregate, custom write
   action? Which tables (config_dbdef backend JSON names) are involved?
5. **Auth**: JWT-protected (default, via `get_current_user`) or public?
6. **Project root**: where `lib/` lives (default `server/` for
   fastapitemplate-style projects, `apps/api-fastapi/` for
   exampleapp-style). Output to `playground/` when testing this skill.

## Step 2 — Generate the model layer

File: `lib/models/<domain>/<feature>.py` (create
`lib/models/<domain>/__init__.py` if the folder is new).

Template (adapt from `references/models/fda_food_endpoint_model.py`):

```python
"""
<Feature description>
"""
from typing import Optional

from genericsuite.util.framework_abs_layer import Response, BlueprintOne
from genericsuite.util.app_logger import log_debug
from genericsuite.util.jwt import AuthorizedRequest
from genericsuite.util.utilities import (
    get_request_body,
    return_resultset_jsonified_or_exception,
)
from genericsuite.config.config_from_db import app_context_and_set_env

DEBUG = False


def <feature>(
    request: AuthorizedRequest,
    blueprint: BlueprintOne,
    other_params: Optional[dict] = None,
) -> Response:
    """
    <Docstring: what it does, params, returns>
    """
    if other_params is None:
        other_params = {}
    params = get_request_body(request)

    app_context = app_context_and_set_env(request=request,
                                          blueprint=blueprint)
    if app_context.has_error():
        return return_resultset_jsonified_or_exception(
            app_context.get_error_resultset()
        )

    # ... business logic building `result` as
    # {"error": bool, "error_message": str | None, "resultset": ...}
    result = {"error": False, "error_message": None, "resultset": {}}
    return return_resultset_jsonified_or_exception(result)
```

For DB access inside the business logic, use GenericDbHelper with the
entity's backend JSON config name (see
`references/models/food_moments_model.py` for the working idiom):

```python
from genericsuite.util.generic_db_middleware import (
    fetch_all_from_db,
)
result = fetch_all_from_db(
    app_context=app_context,
    json_file='<entity_backend_config_name>',
    like_query_params={'name': '<search_value>'},
    combinator='$or',
)
```

## Step 3 — Generate the router layer

File: `lib/routers/<feature>.py`.

Template (adapt from `references/routers/fda_food_endpoint.py`):

```python
"""
<Feature> FastAPI endpoint
"""
from typing import Any
import json

from fastapi import Depends, Request as FaRequest
from fastapi.security import HTTPBasic

from genericsuite.fastapilib.framework_abstraction import BlueprintOne
from genericsuite.fastapilib.util.dependencies import (
    get_current_user,
    get_default_fa_request,
)

from lib.models.<domain>.<feature> import <feature> as <feature>_model

router = BlueprintOne()
security = HTTPBasic()


@router.post('', tags='<feature_tag>')
async def <feature>_endpoint(
    request: FaRequest,
    current_user: str = Depends(get_current_user),
) -> Any:
    """
    <Docstring>
    """
    try:
        params = await request.json()
    except json.JSONDecodeError:
        params = {}
    gs_request, other_params = get_default_fa_request(
        current_user=current_user,
        json_body=params,
    )
    router.set_current_request(request, gs_request)
    return <feature>_model(
        request=gs_request,
        blueprint=router,
        other_params=other_params,
    )
```

Validate required parameters in the router before calling the model, and
return the standard error shape directly on bad input:

```python
    if params.get('<required_param>', '') == '':
        return {
            'error': True,
            'error_message': '<required_param> is required',
            'status_code': 400,
            'resultset': {}
        }
```

## Step 4 — Wiring snippet for lib/main.py

Do NOT rewrite main.py. Output this snippet for the user to add (or apply it
if the user confirms):

```python
from lib.routers import <feature>

app.include_router(
    <feature>.router,
    prefix=f'/{settings.API_VERSION}/<feature_url>')
```

Note: custom FastAPI routers do NOT go into `config_dbdef/backend/endpoints.json`
(that file is for GenericEndpointHelper CRUD entities — see the
`endpoints-builder` skill).

## Step 5 — Verify and summarize

1. Syntax-check every generated file:
   `python3 -m py_compile <each generated .py file>` — must exit 0.
2. Lint if available: `flake8 <files>` (fall back to
   `python3 -m flake8`); fix any findings.
3. Confirm the model layer imports nothing from `fastapi` (layer
   separation): `grep -n "fastapi" lib/models/<domain>/<feature>.py`
   must return nothing.
4. Summarize files created, the main.py wiring snippet, and remind the user
   to add tests and run the dev server (`make dev`).
