"""
FDA food data API AI Tools
"""
from typing import Optional, Any
import json

from langchain.tools import tool
from pydantic import BaseModel, Field

from genericsuite.util.app_context import CommonAppContext
from genericsuite.util.app_logger import log_debug

from genericsuite_ai.lib.translator import lang_translate
from genericsuite_ai.lib.ai_langchain_tools import (
    interpret_tool_params,
)
from genericsuite_ai.lib.ai_utilities import (
    gpt_func_error,
    get_user_lang_code,
)

from lib.config.config import Config
from lib.models.external_apis.fda_food_api import (
    call_fda_api,
    get_calories,
)

DEBUG = False
cac = CommonAppContext()


class FdaFoodQuery(BaseModel):
    """
    FDA food query parameters structure
    """
    food_name: str = Field(description="Food or ingredient name")
    source_lang: Optional[str] = Field(description="Source language")


@tool
def get_fda_food_query(params: Any) -> str:
    """
Useful when you need to get the calories of a given food from the FDA API.
Args: params (dict): Tool parameters. Must have: "food_name" (str): food or ingredient name.
    """  # noqa: E501
    return get_fda_food_query_func(params)


def get_fda_food_query_func(params: Any) -> str:
    """
    Get the calories of a given food from the FDA API.
    """
    settings = Config(cac.get())
    params = interpret_tool_params(tool_params=params,
                                   first_param_name="food_name",
                                   schema=FdaFoodQuery)
    food_name = params.food_name
    source_lang = params.source_lang

    # Get user's preferred language
    source_lang = get_user_lang_code(
        cac.get()) if not source_lang else source_lang

    _ = DEBUG and \
        log_debug(f'GFFQ-1) GET_FDA_FOOD_QUERY | food_name: {food_name}' +
                  f' | source_lang: {source_lang}')

    # request = cac.app_context.get_request()
    error_message = None
    error = False

    if not food_name:
        error = True
        error_message = "Food name is required."
    if not error:
        if source_lang == 'en':
            food_name_en = food_name
        else:
            translate_response = lang_translate(
                food_name, source_lang=source_lang, target_lang="en"
            )
            if translate_response["error"]:
                error = True
                error_message = translate_response["error_message"]
            if not error:
                food_name_en = translate_response["output_text"]
                _ = DEBUG and \
                    log_debug('GFFQ-1.5) GET_FDA_FOOD_QUERY' +
                              f' food_name_en: {food_name_en}')
    if not error:
        api_response = call_fda_api(cac.get(), food_name_en)
        food_response = ""
        if api_response["error"]:
            error = True
            error_message = api_response["error_message"]
    if error:
        food_response = "Sorry, I couldn't get food information for:" + \
            f" {food_name_en}."
    else:
        calories = get_calories(
            api_response=api_response["response"],
            detailed=False,
            mandatory_serving_size=True,
        )
        if len(calories) == 0:
            food_response = "Sorry, I couldn't get the calories for:" + \
                f" {food_name_en}."
        else:
            food_response = json.dumps(calories)

    if settings.DEBUG and error_message:
        food_response = f"{food_response} | ERROR detail: {error_message}"

    if error:
        food_response = gpt_func_error(food_response)

    _ = DEBUG and \
        log_debug(
            f'GFFQ-2) GET_FDA_FOOD_QUERY food_response: {food_response}'
        )
    return food_response
