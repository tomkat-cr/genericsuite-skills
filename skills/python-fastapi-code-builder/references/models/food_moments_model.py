"""
Food moments operations
"""
from typing import Optional

# from chalice.app import Response
# from genericsuite.util.blueprint_one import BlueprintOne
from genericsuite.util.framework_abs_layer import Response, BlueprintOne

from genericsuite.util.app_logger import log_debug
from genericsuite.util.generic_db_helpers import GenericDbHelper
from genericsuite.util.jwt import AuthorizedRequest
from genericsuite.util.utilities import (
    return_resultset_jsonified_or_exception,
    get_query_params,
    method_not_allowed,
)
from genericsuite.config.config_from_db import app_context_and_set_env

from genericsuite.util.generic_endpoint_helpers import GenericEndpointHelper

DEBUG = False


def food_moments_crud(
    request: AuthorizedRequest,
    blueprint: BlueprintOne,
    other_params: Optional[dict] = None
) -> Response:
    """
    CRUD operations for food_moments.
    """
    if not other_params:
        other_params = {}
    _ = DEBUG and log_debug('>>--> FOOD_MOMENTS_CRUD' +
        f' | request.method: {request.method}'
        f' | request: {request}'
        )
    # Set environment variables from the database configurations.
    app_context = app_context_and_set_env(request=request, blueprint=bp)
    if app_context.has_error():
        return return_resultset_jsonified_or_exception(
            app_context.get_error_resultset()
        )
    # CRUD operations for food_moments.
    ep_helper = GenericEndpointHelper(
        app_context=app_context,
        json_file="food_moments",
        url_prefix=__name__,
    )
    return ep_helper.generic_crud_main()


def food_moment_in_user(
    request: AuthorizedRequest,
    blueprint: BlueprintOne,
    other_params: Optional[dict] = None
) -> Response:
    """
    Fetch the count of food_moment_id in all user's "food_times" array
    """
    if not other_params:
        other_params = {}
    # Set environment variables from the database configurations.
    app_context = app_context_and_set_env(request=request, blueprint=bp)
    if app_context.has_error():
        return return_resultset_jsonified_or_exception(
            app_context.get_error_resultset()
        )
    # Fetch the count of food_moment_id in all user's "food_times" array
    dbo = GenericDbHelper(json_file="users_food_times", request=request,
        blueprint=blueprint)
    query_params = get_query_params(request)
    food_moment_id = query_params.get('id')
    user_id = app_context.get_user_id()
    if food_moment_id is not None:
        _ = DEBUG and log_debug(f'GFMIU-1) food_moment by id: {food_moment_id}')
        result = dbo.get_array_item_in_row(food_moment_id,
                                          {"user_id": user_id})
        _ = DEBUG and log_debug(f'GFMIU-2) food_moment by id: {food_moment_id}' +
                  f' | result: {result}')
        return return_resultset_jsonified_or_exception(result)
    # If no food moment ID, deny the request.
    return method_not_allowed()
