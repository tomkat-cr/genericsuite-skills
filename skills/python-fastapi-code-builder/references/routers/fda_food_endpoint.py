"""
FastAPI FDA food API endpoint
"""
from typing import Any
import json

from fastapi import Depends, Request as FaRequest
from fastapi.security import HTTPBasic

from genericsuite.fastapilib.framework_abstraction import (
    BlueprintOne,
)
from genericsuite.util.app_logger import log_debug

from genericsuite.fastapilib.util.dependencies import (
    get_current_user,
    get_default_fa_request,
)

from lib.models.external_apis.fda_food_endpoint import (
    fda_food_endpoint as fda_food_endpoint_model
)

DEBUG = False

# Set FastAPI router
router = BlueprintOne()

# Set up Basic Authentication
security = HTTPBasic()


@router.post('', tags='fda')
async def fda_food_endpoint(
    request: FaRequest,
    current_user: str = Depends(get_current_user),
) -> Any:
    """
    This endpoint is used to fetch food data from the FDA API.
    It takes in a request and other parameters and returns a response.

    :param request: The request object containing the request data.
    :param other_params: Any other parameters that may be needed.
    :return: A response object containing the response data.
    """
    # Parse JSON body
    try:
        # Used await request.json() to correctly parse the JSON body and
        # passed it to the model layer via
        # get_default_fa_request(..., json_body=params).
        params = await request.json()
    except json.JSONDecodeError:
        params = {}

    food_name = params.get('food_name', '')
    if DEBUG:
        log_debug(f'GFFQ-1) GET_FDA_FOOD_QUERY | food_name: {food_name}' +
                  f' | current_user: {current_user} | params: {params}')
    if food_name == '':
        return {
            'error': True,
            'error_message': 'Food name is required',
            'status_code': 400,
            'resultset': {}
        }
    gs_request, other_params = get_default_fa_request(
        current_user=current_user,
        json_body=params
    )
    router.set_current_request(request, gs_request)
    return fda_food_endpoint_model(
        request=gs_request,
        blueprint=router,
        other_params=other_params
    )
