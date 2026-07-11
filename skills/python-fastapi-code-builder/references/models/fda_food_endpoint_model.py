"""
FDA food API endpoint
"""
from typing import Optional
import json

from genericsuite.util.framework_abs_layer import Response, BlueprintOne
from genericsuite.util.app_logger import log_debug
from genericsuite.util.jwt import AuthorizedRequest
from genericsuite.util.utilities import (
    get_request_body,
    return_resultset_jsonified_or_exception,
)
from genericsuite.config.config_from_db import app_context_and_set_env

from lib.models.external_apis.fda_food_api import (
    call_fda_api, get_calories
)


def fda_food_endpoint(
    request: AuthorizedRequest,
    blueprint: BlueprintOne,
    other_params: Optional[dict] = None
) -> Response:
    """
    This endpoint is used to fetch food data from the FDA API.
    It takes in a request and other parameters and returns a response.

    :param request: The request object containing the request data.
    :param other_params: Any other parameters that may be needed.
    :return: A response object containing the response data.
    """
    if other_params is None:
        other_params = {}
    params = get_request_body(request)

    # Set environment variables from the database configurations.
    app_context = app_context_and_set_env(request=request, blueprint=blueprint)
    if app_context.has_error():
        return return_resultset_jsonified_or_exception(
            app_context.get_error_resultset()
        )

    food_name = params.get('food_name', '')
    first = params.get('first', '0')
    raw_result = params.get('raw_result', '0')
    autocomplete = params.get('autocomplete', '0')
    mandatory_serving_size = params.get(
        'mandatory_serving_size',
        '1' if autocomplete == '1' else '0'
    )

    log_debug(f'FFQEP-0) FDA_FOOD_ENDPOINT - food_name: {food_name}' +
              f' | first: {first} | raw_result: {raw_result}'
              f' | autocomplete: {autocomplete}')

    api_response = call_fda_api(app_context, food_name)
    # log_debug(f'FFQEP-1) FDA_FOOD_ENDPOINT - api_response: {api_response}')
    if raw_result == '1' or api_response["error"]:
        return return_resultset_jsonified_or_exception(
            api_response
        )
    calories = get_calories(
        api_response=api_response["response"],
        only_first=(first == '1'),
        detailed=(autocomplete == '1'),
        mandatory_serving_size=(mandatory_serving_size == '1')
    )
    if len(calories) == 0:
        food_response = json.dumps([])
        api_response["error"] = True
        api_response["error_message"] = "Sorry, I couldn't get the" + \
                                        " calories for that food."
    else:
        if first == '1':
            food_response = json.dumps(calories[0]
                                       if len(calories) > 0 else {})
        else:
            food_response = calories

    # log_debug(f'FFQEP-2) FDA_FOOD_ENDPOINT - calories: {calories}')
    # log_debug(f'FFQEP-3) FDA_FOOD_ENDPOINT - food_response: {food_response}')
    api_response["resultset"] = food_response

    return return_resultset_jsonified_or_exception(
        api_response
    )
