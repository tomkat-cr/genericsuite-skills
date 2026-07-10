"""
Chalice Food moments operations
"""
from typing import Any

from fastapi import Depends, Request as FaRequest
from fastapi.security import HTTPBasic

from genericsuite.fastapilib.framework_abstraction import (
    BlueprintOne,
)
# from genericsuite.util.app_logger import log_debug

from genericsuite.fastapilib.util.dependencies import (
    get_current_user,
    get_default_fa_request,
)

from lib.models.admin_food.food_moments import (
    food_moment_in_user as food_moment_in_user_model,
)

DEBUG = False

# Set FastAPI router
router = BlueprintOne()

# Set up Basic Authentication
security = HTTPBasic()


@router.get('/', tags='food_moment_in_user')
async def food_moment_in_user(
    request: FaRequest,
    current_user: str = Depends(get_current_user),
) -> Any:
    """
    Fetch the count of food_moment_id in all user's "food_times" array
    """
    gs_request, other_params = get_default_fa_request(
        current_user=current_user)
    router.set_current_request(request, gs_request)
    return food_moment_in_user_model(
        request=gs_request,
        blueprint=router,
        other_params=other_params
    )
