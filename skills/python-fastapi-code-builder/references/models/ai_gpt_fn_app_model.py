"""
AI Tools: App specific
"""
# Ignore large lines
# pylint: disable=line-too-long
# flake8: noqa: E501

from typing import Union, Any, List, Optional
import json
import re
from datetime import datetime
from uuid import uuid4

from pydantic_core import PydanticCustomError
from pydantic import BaseModel, Field, field_validator

from langchain.tools import tool
from langchain_classic.schema import Document

from genericsuite.util.app_context import CommonAppContext
from genericsuite.util.app_logger import log_debug
from genericsuite.util.config_dbdef_helpers import get_json_def_both
from genericsuite.util.datetime_utilities import interpret_any_date
from genericsuite.util.utilities import (
    get_default_resultset,
    is_under_test,
)
from genericsuite.util.generic_db_middleware import (
    fetch_all_from_db,
    add_item_to_db,
    get_item_from_db,
    modify_item_in_db,
)
from genericsuite.constants.const_tables import get_constant

from genericsuite_ai.lib.ai_utilities import (
    standard_gpt_func_response,
    get_assistant_you_are,
)
from genericsuite_ai.lib.ai_sub_bots import ask_ai
from genericsuite_ai.lib.ai_langchain_tools import (
    interpret_tool_params,
)
from genericsuite_ai.lib.json_reader import (
    prepare_metadata,
    index_dict,
)

from lib.models.utilities.food_utilities import (
    FoodUtilities,
)

DEBUG = False
cac = CommonAppContext()


# Structures


class Ingredient(BaseModel):
    """
    Ingredients without quantity structure
    """
    # id: UUID = Field(description="Row ID", default_factory=uuid4)
    name: str = Field(
        description="Ingredient name")
    calories_value: float = Field(
        description="Ingredient calories")
    calories_unit: str = Field(
        description="Ingredient calories unit")
    serving_size: float = Field(
        description="Ingredient serving size")
    serving_size_unit: str = Field(
        description="Ingredient serving size unit")
    brand_name: Optional[str] = Field(
        default="",
        description="Ingredient brand_name if any. Defaults to None")
    observations: Optional[str] = Field(
        default="",
        description="Ingredient observations if any. Defaults to None")

    @field_validator("calories_unit", mode="after")
    @classmethod
    def validate_calories_unit(cls, v: str) -> str:
        valid_units = ["kcal", "kj"]
        if v not in valid_units:
            raise PydanticCustomError(
                "invalid_calories_unit",
                "Calories unit must be one of: {valid_units}, got {unit}",
                {"valid_units": ", ".join(valid_units), "unit": v}
            )
        return v

    @field_validator("serving_size_unit", mode="after")
    @classmethod
    def validate_serving_size_unit(cls, v: str) -> str:
        valid_units = ["g", "u", "tsp", "tablespoon", "bowl", "cup", "scup",
                       "ml", "mg", "ug", "oz", "lb", "iu", "mlt"]
        if v not in valid_units:
            raise PydanticCustomError(
                "invalid_serving_size_unit",
                "Serving size unit must be one of: {valid_units}, got {unit}",
                {"valid_units": ", ".join(valid_units), "unit": v}
            )
        return v


class IngredientWithQty(Ingredient):
    """
    Ingredients with quantity structure
    """
    id: Optional[str] = Field(
        default=None,
        description="row ID generated as str(uuid4())")
    quantity: float = Field(
        description="Ingredient quantity")
    total_calories: Optional[float] = Field(
        default=0.0,
        description="Total calories")


class IngredientWithQtyAndFoodMoment(IngredientWithQty):
    """
    Ingredients with quantity structure
    """
    # food_moment: str = Field(description="Food moment")
    meal_type: str = Field(description="Meal type")

    @field_validator("meal_type", mode="after")
    @classmethod
    def validate_meal_type(cls, v: str) -> str:
        valid_types = ["Breakfast", "Brunch", "Elevenses", "Lunch", "Tea",
                       "Supper", "Dinner", "Other", "Unknown"]
        if v not in valid_types:
            raise PydanticCustomError(
                "invalid_meal_type",
                "Meal type must be one of: {valid_types}, got {meal_type}",
                {"valid_types": ", ".join(valid_types), "meal_type": v}
            )
        return v


class Dish(BaseModel):
    """
    Dish structure
    """
    name: str = Field(
        description="The name of the user's dish")
    calories_value: float = Field(
        description="The total calories resulted" +
                    " of sum the total_calories of all " +
                    "ingredients converted to the calories_unit")
    calories_unit: str = Field(
        description="The calories unit in the dish (eq. kcal)")
    serving_size: float = Field(
        description="The serving size of the dish")
    serving_size_unit: str = Field(
        description="The serving size unit code in the dish")
    brand_name: Optional[str] = Field(
        default="",
        description="The brand name of the dish")
    observations: Optional[str] = Field(
        default="",
        description="Any additional observations about the dish")
    ingredients: List[IngredientWithQty] = Field(
        description="Dish ingredients list")


class DailyMeal(BaseModel):
    """
    Daily Meal structure
    """
    meal_date: str = Field(description="Meal date")
    observations: Optional[str] = Field(
        default="",
        description="Any additional observations")
    ingredients: List[IngredientWithQtyAndFoodMoment] = Field(
        description="Meal ingredients list")


class JustName(BaseModel):
    """
    Tool with only a name parameter structure
    """
    name: str = Field(description="Name to process")


class FindDate(BaseModel):
    """
    Tool with only a find_date parameter structure
    """
    find_date: str = Field(
        description="Date to search, with format YYYY-MM-DD")


# Support Funcions


def get_food_moments() -> str:
    """
    Retrieve all food moments from the database.

    Args:
        None.

    Returns:
        str: The result of retrieving the food moments for GPT.
    """
    result = fetch_all_from_db(
        app_context=cac.app_context,
        json_file="food_moments",
    )
    result = standard_gpt_func_response(
        result=result,
        action_description="Food Moments retrieval",
        include_resultset=True,
    )
    if DEBUG:
        log_debug(f'AI_GFM-1) get_food_moments | result: {result}')
    return result


def get_food_moments_list() -> dict:
    """
    Retrieve all food moments from the database.

    Args:
        None.

    Returns:
        list[dict]: The result of retrieving the food moments.
    """
    result = fetch_all_from_db(
        app_context=cac.app_context,
        json_file="food_moments",
    )
    if DEBUG:
        log_debug(f'AI_GFML-1) get_food_moments_list | result: {result}')
    return result


def food_moment_id_from_ai(food_moment: str, food_moments: dict) -> dict:
    """
    Fetch the food moment ID using AI
    """
    self_debug = DEBUG or is_under_test()

    def build_document(code: str, meal_type: dict) -> Document:
        """ Build one Document and debug data """
        metadata = {
            "code": code,
            "meal_type": meal_type,
        }
        result = Document(page_content=meal_type, metadata=metadata)
        if self_debug:
            log_debug('>> FOOD_MOMENT_ID_FROM_AI -> build_document' +
                      f'\n | code: {code} | meal_type: {meal_type}' +
                      f'\n | result: {result}')
        return result

    result = get_default_resultset()
    result["vector_store"] = None
    # Create the array of Document() to be used by the retriever
    docs = [
        build_document(idx, meal_type)
        for idx, meal_type in food_moments.items()
    ]

    # Power prompt
    prompt = f"What is the the meal type '{food_moment}'" + \
        " in english? if you find it, return the code."

    if self_debug:
        log_debug('AI_FMIFA-1) FOOD_MOMENT_ID_FROM_AI' +
                  f' | prompt: {prompt}' +
                  f' | docs: {docs}')

    # Ask the question to the model
    result = ask_ai(
        app_context=cac.get(),
        documents_list=docs,
        question=prompt,
        response_type="answer",
    )
    if self_debug:
        log_debug(f'AI_FMIFA-2) FOOD_MOMENT_ID_FROM_AI | result: {result}')
    return result


def food_moments_dict() -> dict:
    """
    Returns a dict of meal types 9foormerly food_moments

    Returns:
        dict: of meal types with code and name attributes
    """
    self_debug = DEBUG or is_under_test()
    food_moments = get_food_moments_list()
    _ = self_debug and \
        log_debug('AI_FMD-1) FOOD_MOMENTS_DICT' +
                  f'\n | food_moments (raw list): {food_moments}' +
                  '\n')
    if food_moments["error"]:
        return food_moments
    food_moment_rs = json.loads(food_moments["resultset"])
    food_moments['resultset'] = \
        {str(fm['_id']['$oid']): fm['name'] for fm in food_moment_rs}
    _ = self_debug and \
        log_debug('AI_FMD-2) FOOD_MOMENTS_DICT' +
                  f'\n | food_moments: {food_moments}' +
                  '\n')
    return food_moments


def food_moment_id_fetch(food_moment: str) -> dict:
    """
    Fetch the food moment ID
    """
    self_debug = DEBUG or is_under_test()

    food_moments = food_moments_dict()
    if food_moments["error"]:
        return food_moments

    food_moment_id = next(
        (fm_key
         for fm_key, fm_name in food_moments["resultset"].items()
         if fm_name == food_moment
         ), None
    )
    if self_debug:
        log_debug('AI_FMIF-1) FOOD_MOMENT_ID_FETCH' +
                  f' | food_moment_id: {food_moment_id}')
    if not food_moment_id:
        id_from_ai = food_moment_id_from_ai(
            food_moment,
            food_moments["resultset"])
        if self_debug:
            log_debug('AI_FMIF-2) FOOD_MOMENT_ID_FETCH' +
                      f' | id_from_ai: {id_from_ai}')
        if id_from_ai["error"]:
            return id_from_ai
        food_moment_id = id_from_ai["resultset"]
    result = get_default_resultset()
    result["food_moment_id"] = food_moment_id
    if self_debug:
        log_debug(f'AI_FMIF-3) FOOD_MOMENT_ID_FETCH | result: {result}')
    return result


def transform_code_desc(
    definition_file: str,
    resultset: dict
) -> Union[dict, None]:
    """
    Returns the resultset with the 'select' type columns
    transformed from code to description.
    """
    table_def = get_json_def_both(definition_file)
    if not table_def:
        return None
    return {
        item_def["name"]:
        get_constant(item_def["select_elements"],
                     resultset[item_def.get("name", '')])
        if item_def["type"] == "select" and
        item_def.get("select_elements")
        else resultset.get(item_def["name"])
        for item_def in table_def["fieldElements"]
        if item_def["type"] not in ["hr", "label"]
    }


# Funcions called by ChatGPT


# User's ingredients


@tool
def create_user_ingredient(params: Any) -> str:
    """
Useful when you need to add a new user ingredient to the database.
Args: params (dict): Tool parameters. It must contain:
"name" (str): ingredient name.
"calories_value" (float): ingredient calories.
"calories_unit" (str): ingredient calorie unit. Use only these codes: "kcal" and "kj".
"serving_size" (float): ingredient serving size.
"serving_size_unit" (str): ingredient serving size code. Use only these codes:
g=Grams
u=Unit
tsp=Tea spoon
tablespoon=Table spoon
bowl=Bowl (300 ml)
cup=Cup (200 ml)
scup=Small Cup (150 ml)
ml=Milliliters
mg=Milligrams
ug=Micro grams
oz=Ounce
lb=Pound
iu=International units
mlt=Mass,length,time.
"brand_name" (str): ingredient brand if any.
"observations" (str): additional observations about the ingredient if any.
    """
    return create_user_ingredient_func(params)


def create_user_ingredient_func(params: Any) -> str:
    """
    Add a new user ingredient to the database.
    """
    params = interpret_tool_params(tool_params=params, schema=Ingredient)

    name = params.name
    calories_value = params.calories_value
    calories_unit = params.calories_unit
    serving_size = params.serving_size
    serving_size_unit = params.serving_size_unit
    brand_name = params.brand_name
    observations = params.observations

    new_item = {
        "user_id": cac.app_context.get_user_id(),
        "type": "I",
        "name": name,
        "calories_value": calories_value,
        "calories_unit": calories_unit,
        "serving_size": serving_size,
        "serving_size_unit": serving_size_unit,
        "brand_name": brand_name,
        "observations": observations,
    }
    # filters = {
    #     "user_id": cac.app_context.get_user_id(),
    # }
    if DEBUG:
        log_debug('AI_CUI-1) create_user_ingredient |' +
                  f' new_item: {new_item}')
    result = add_item_to_db(
        app_context=cac.app_context,
        json_file='user_ingredients',
        data=new_item,
        # filters=filters,
    )
    return standard_gpt_func_response(result, "User Ingredient creation")


@tool
def search_user_ingredient(params: Any) -> str:
    """
Useful when you need to search user's ingredients by name.
Args: params (dict): Tool parameters. It must have: name (str): the string to search, contained in the ingredient name.
    """
    return search_user_ingredient_func(params)


def search_user_ingredient_func(params: Any) -> str:
    """
    Search user's ingredients by name.
    """
    params = interpret_tool_params(tool_params=params, schema=JustName)
    name = params.name
    if DEBUG:
        log_debug('AI_SUIBN-1) search_user_ingredient |' +
                  f' name: {name}')
    resultset = fetch_all_from_db(
        app_context=cac.app_context,
        json_file='user_ingredients',
        like_query_params={"name": name},
        combinator="$or",
    )
    if DEBUG:
        log_debug('AI_SUIBN-2) search_user_ingredient |' +
                  f' resultset: {resultset}')
    return standard_gpt_func_response(
        result=resultset,
        action_description="User's Ingredient retrieval",
        include_resultset=True
    )


@tool
def get_user_ingredient_list(params: Any = None) -> str:
    """
Useful when you need to get all user's ingredients.
    """
    return get_user_ingredient_list_func(params)


def get_user_ingredient_list_func(params: Any = None) -> str:
    """
    Get all user's ingredients.
    """
    if params:
        params = interpret_tool_params(tool_params=params)
    else:
        params = {}
    if DEBUG:
        log_debug('AI_GUIL-1) get_user_ingredient_list' +
                  f' params: {params}')
    resultset = get_user_ingredient_list_raw()
    return standard_gpt_func_response(
        result=resultset,
        action_description="User's Ingredient list",
        include_resultset=True
    )


def get_user_ingredient_list_raw() -> dict:
    """
    Get all user's ingredients.

    Args:
        None.

    Returns:
        dict: user's ingredients resultset.
    """
    if DEBUG:
        log_debug('AI_GUILR-1) get_user_ingredient_list_raw')
    resultset = fetch_all_from_db(
        app_context=cac.app_context,
        json_file='user_ingredients',
    )
    if DEBUG:
        log_debug('AI_GUILR-2) get_user_ingredient_list_raw |' +
                  f' resultset: {resultset}')
    return resultset


# User's dishes


@tool
def create_dish(params: Any = None) -> str:
    """
Useful to create a new user dish with a list of ingredients and quantities and no date.
Args: params (dict): Tool parameters. Must have these attributes:
name (str): dish name
calories_value (float): the sum of all ingredients' calories, converted to the dish's calorie unit
calories_unit (str): Use only kcal
serving_size (float): must be 1
serving_size_unit (str): must be "u" (Unit)
brand_name (str): must be ""
observations (str): if any
ingredients (list): Must have at least one. Each one have these attributes:
```
id (str): generated as uuid4
name (str)
calories_value (float)
calories_unit (str): Use only kcal and kj
serving_size (float)
serving_size_unit (str): Use only these codes:
g
u
tsp
tablespoon
bowl
cup
scup
ml
mg
ug
oz
lb
iu
mlt
quantity (float)
total_calories (float): calculated as round((ingredient["calories_value"] * ingredient["quantity"]/ingredient["serving_size"]) if ingredient["serving_size"] > 0 else 0, 2)
brand_name (str): if any
observations (str): if any
```
    """
    return create_dish_func(params)


def create_dish_func(params: Any = None) -> str:
    """
    Create a new user dish with a list of ingredients and
    quantities and no date.
    """
    params = interpret_tool_params(tool_params=params, schema=Dish)

    if DEBUG:
        log_debug('AI-CD-1) create_dish |' +
                  f' params: {params}')

    name = params.name
    calories_value = params.calories_value
    calories_unit = params.calories_unit
    serving_size = params.serving_size
    serving_size_unit = params.serving_size_unit
    brand_name = params.brand_name
    observations = params.observations

    fu_lib = FoodUtilities(cac.get())

    new_item = {
        "user_id": cac.app_context.get_user_id(),
        "type": "D",
        "name": name,
        "calories_value": calories_value,
        "calories_unit": calories_unit,
        "serving_size": serving_size,
        "serving_size_unit": serving_size_unit,
        "brand_name": brand_name,
        "observations": observations,
        "dish_ingredients": []
    }

    for ingredient in params.ingredients:
        new_ingredient = {
            "id": str(uuid4())
            if None or not isinstance(ingredient.id, str)
            else ingredient.id,
            "name": ingredient.name,
            "calories_value": ingredient.calories_value,
            "calories_unit": ingredient.calories_unit,
            "serving_size": ingredient.serving_size,
            "serving_size_unit": ingredient.serving_size_unit,
            "quantity": ingredient.quantity,
            "total_calories": fu_lib.total_calories(
                calories_value=ingredient.calories_value,
                serving_size=ingredient.serving_size,
                quantity=ingredient.quantity,
            ),
            "brand_name": ingredient.brand_name,
            "observations": ingredient.observations,
        }
        new_item["dish_ingredients"].append(new_ingredient)

    new_item = fu_lib.sum_total_calories(
        new_item, "dish_ingredients"
    )

    if DEBUG:
        log_debug('AI-CD-2) create_dish |' +
                  f' new_item: {new_item}')

    result = add_item_to_db(
        app_context=cac.app_context,
        json_file='dishes',
        data=new_item,
    )

    return standard_gpt_func_response(result, "Dish creation")


@tool
def search_dishes(params: Any) -> str:
    """
Useful when you need to search user's dishes by name.
Args: params (dict): Tool parameters. Must have: "name" (str): string to search, contained in the dish name.
    """
    return search_dishes_func(params)


def search_dishes_func(params: Any) -> str:
    """
    Search user's dishes by name.
    """
    params = interpret_tool_params(tool_params=params, schema=JustName)
    name = params.name
    if DEBUG:
        log_debug('AI_SD-1) search_dishes |' +
                  f' name: {name}')
    resultset = fetch_all_from_db(
        app_context=cac.app_context,
        json_file='dishes',
        like_query_params={"name": name},
        combinator="$or",
    )
    if DEBUG:
        log_debug('AI_SD-2) search_dishes |' +
                  f' resultset: {resultset}')
    return standard_gpt_func_response(
        result=resultset,
        action_description="Dishes retrieval",
        include_resultset=True,
        json_result=False,
    )


@tool
def get_dishes_list(params: Any = None) -> str:
    """
Useful when you need to get all user's dishes.
    """
    return get_dishes_list_func(params)


def get_dishes_list_func(params: Any = None) -> str:
    """
    Get all user's dishes.
    """
    if params:
        params = interpret_tool_params(tool_params=params)
    else:
        params = {}
    if DEBUG:
        log_debug('AI_GDL-1) get_dishes_list' +
                  f' params: {params}')
    resultset = get_dishes_list_raw()
    return standard_gpt_func_response(
        result=resultset,
        action_description="Dishes list",
        include_resultset=True
    )


def get_dishes_list_raw() -> dict:
    """
    Get all user's dishes.

    Args:
        None.

    Returns:
        dict: user's dishes resultset
    """
    if DEBUG:
        log_debug('AI_GDLR-1) get_dishes_list_raw')
    resultset = fetch_all_from_db(
        app_context=cac.app_context,
        json_file='dishes',
    )
    if DEBUG:
        log_debug('AI_GDLR-2) get_dishes_list |' +
                  f' resultset: {resultset}')
    return resultset


# Daily Meals


@tool
def create_daily_meal(params: Any) -> str:
    """
Useful when you need to add a new user daily meal to the database.
Args: params (dict): Tool parameters. Must have the following attributes:
meal_date (str): meal date as GMT-0 YYYY-MM-DD
observations (str)
ingredients (list): each one must have these attributes:
```
id (str): generated as uuid4
meal_type (str): e.g., Breakfast,Brunch,Elevenses,Lunch,Tea,Supper,Dinner,Other,Unkown
name (str)
calories_value (float)
calories_unit (str): Use only: kcal and kj
serving_size (float): always 1
serving_size_unit (str): Use only "u"
quantity (float)
total_calories (float): calculated as round((ingredient["calories_value"] * ingredient["quantity"]/ingredient["serving_size"]) if ingredient["serving_size"] > 0 else 0, 2)
brand_name (str): brand_name if any
observations (str): observations if any
```
"""
    return create_daily_meal_func(params)


def create_daily_meal_func(params: Any) -> str:
    """
    Add a new user daily meal to the database.
    """

    params = interpret_tool_params(tool_params=params, schema=DailyMeal)

    meal_date = params.meal_date
    observations = params.observations

    fu_lib = FoodUtilities(cac.get())

    # Convert meal_date to timestamp
    meal_date_timestamp = interpret_any_date(meal_date)
    if meal_date_timestamp == -1:
        return f"Failed to convert '{meal_date}' to timestamp"

    if DEBUG:
        log_debug('AI_CDM-1) create_daily_meal' +
                  f' Parameters | meal_date: {meal_date}' +
                  f', observations: {observations}' +
                  f', ingredients: {params.ingredients}')

    # Convert meal_date to 00:00 UTC timestamp
    # meal_date_timestamp = datetime.strptime(meal_date, '%Y-%m-%d').replace(
    #     hour=0, minute=0, second=0, microsecond=0
    # ).timestamp()

    existing_meal = get_item_from_db(
        app_context=cac.app_context,
        json_file="daily_meals",
        entry_name="meal_date",
        entry_value=meal_date_timestamp,
        user_id=cac.app_context.get_user_id(),
    )
    if existing_meal["error"]:
        return f"Failed to get daily meal for {meal_date}" + \
            str({existing_meal["error_message"]})

    meal_ingredients = []
    if existing_meal["resultset"]:
        meal_ingredients = existing_meal["resultset"]["meal_ingredients"]

    for ingredient in params.ingredients:

        id_resultset = food_moment_id_fetch(ingredient.meal_type)
        if id_resultset["error"]:
            # return f"Failed to get food moment ID for " + \
            #     "'{ingredient.food_moment}'" + \
            #     str({id_resultset["error_message"]})
            food_moment_id = ""
        else:
            food_moment_id = id_resultset["food_moment_id"]

        new_ingredient = {
            "id": str(uuid4())
            if None or not isinstance(ingredient.id, str)
            else ingredient.id,
            "food_moment_id": str(food_moment_id),
            "meal_type": ingredient.meal_type,
            "name": ingredient.name,
            "calories_value": ingredient.calories_value,
            "calories_unit": ingredient.calories_unit,
            "serving_size": ingredient.serving_size,
            "serving_size_unit": ingredient.serving_size_unit,
            "quantity": ingredient.quantity,
            "total_calories": fu_lib.total_calories(
                calories_value=ingredient.calories_value,
                serving_size=ingredient.serving_size,
                quantity=ingredient.quantity,
            ),
            "brand_name": ingredient.brand_name,
            "observations": ingredient.observations,
        }
        meal_ingredients.append(new_ingredient)

    if not existing_meal["resultset"]:
        # Create new daily meal item
        new_meal = {
            "meal_date": meal_date_timestamp,
            "user_id": cac.app_context.get_user_id(),
            "observations": observations,
        }
        new_meal["meal_ingredients"] = meal_ingredients
        new_meal = fu_lib.sum_total_calories(
            new_meal, "meal_ingredients"
        )
        result = add_item_to_db(
            app_context=cac.app_context,
            json_file="daily_meals",
            data=new_meal
        )
    else:
        # Add ingredients to existing meal
        existing_meal["meal_ingredients"] = meal_ingredients
        existing_meal = fu_lib.sum_total_calories(
            existing_meal, "meal_ingredients"
        )
        result = modify_item_in_db(
            app_context=cac.app_context,
            json_file="daily_meals",
            data=existing_meal
        )
    if DEBUG:
        log_debug('AI_CDM-2) create_daily_meal' +
                  f' | result: {result}')

    return standard_gpt_func_response(result, "Daily Meal creation")


@tool
def search_daily_meals(params: Any) -> str:
    """
Useful when you need to search user's daily meals by date. E.g. `what I ate yesterday at lunh?` or `how many caliries I consumed today?`
Args: params (dict): Tool parameters. Must contain: "find_date" (str): date to search, with format YYYY-MM-DD.
    """
    return search_daily_meals_func(params)


def search_daily_meals_func(params: Any) -> str:
    """
    Search user's daily meals by date.
    """
    params = interpret_tool_params(tool_params=params, schema=FindDate)
    if "get_current_date_time" in params:
        find_date = datetime.utcnow().strftime('%Y-%m-%d')
    else:
        find_date = params.find_date
    date_range_list = find_date.split(",")
    # Convert find_date to timestamp
    date_range_list = [str(datetime.strptime(
        v, '%Y-%m-%d'
    ).replace(
        hour=0, minute=0, second=0, microsecond=0
    ).timestamp())
        for v in date_range_list
    ]
    if DEBUG:
        log_debug('AI_SDM-1) search_daily_meals' +
                  f' | find_date: {find_date}' +
                  f' | date_range_list: {date_range_list}'
                  )
    resultset = fetch_all_from_db(
        app_context=cac.app_context,
        json_file='daily_meals',
        like_query_params={"meal_date": ",".join(date_range_list)},
        combinator="$or",
    )
    if DEBUG:
        log_debug('AI_SDM-2) search_daily_meals |' +
                  f' resultset: {resultset}')
    return standard_gpt_func_response(
        result=resultset,
        action_description="Daily Meals retrieval",
        include_resultset=True,
        json_result=False
    )


@tool
def get_daily_meal_list(params: Any = None) -> str:
    """
Useful when you need to get all user's daily meals, ordered by meal date in descending order.
    """
    return get_daily_meal_list_func(params)


def get_daily_meal_list_func(params: Any = None) -> str:
    """
Useful when you need to get all user's daily meals, ordered by meal date in descending order.
    """
    if params:
        params = interpret_tool_params(tool_params=params)
    else:
        params = None
    if DEBUG:
        log_debug('AI_GDML-1) get_daily_meal_list' +
                  f' params: {params}')
    resultset = get_daily_meal_list_raw()
    return standard_gpt_func_response(
        result=resultset,
        action_description="Daily Meals list",
        include_resultset=True
    )


def get_daily_meal_list_raw() -> dict:
    """
    Get all user's daily meals, ordered by meal_date descending.

    Args:
        None.

    Returns:
        dict: user's daily meals resultset
    """
    if DEBUG:
        log_debug('AI_GDMLR-1) get_daily_meal_list_raw')
    resultset = fetch_all_from_db(
        app_context=cac.app_context,
        json_file='daily_meals',
        order_param="meal_date|desc"
    )
    food_moments_rs = food_moments_dict()
    if food_moments_rs['error']:
        return food_moments_rs
    food_moments = food_moments_rs['resultset']
    _ = DEBUG and log_debug(f"food_moments = {food_moments}")
    resultset['resultset'] = json.loads(resultset['resultset'])
    return resultset

# User's Profile


@tool
def get_user_profile(params: Any) -> str:
    """
Useful when you need to get user's summary profile. The summary profile only contains user's data like gender, weight, height, age, physical goals, other goals, training days, training hour, food times, historic data (weight, height, physical goals, and other goals).
    """
    return get_user_profile_func(params)


def get_user_profile_func(params: Any) -> str:
    """
    Get user's summary profile.
    """
    if params:
        params = interpret_tool_params(tool_params=params)
    else:
        params = {}
    if DEBUG:
        log_debug('AI_GUP-1) get_user_profile' +
                  f' params: {params}')
    result = get_user_profile_raw()
    return standard_gpt_func_response(
        result=result,
        action_description="User profile",
        include_resultset=True
    )


def get_user_profile_raw() -> dict:
    """
    Get user profile. The profile contains user's data like gender, weight,
    height, age, physical goals, other goals, training days, training hour,
    food times, historic data (weight, height, physical goals, and other
    goals).

    Args:
        None.

    Returns:
        dict: the user profile resultset.
    """
    if DEBUG:
        log_debug('AI_GUPR-1) get_user_profile_raw')

    user_data = cac.app_context.get_user_data()

    fu_lib = FoodUtilities(cac.get())

    # Data calculations
    user_data["age"] = fu_lib.calculate_age(
        datetime.utcfromtimestamp(user_data.get("birthday"))
    )

    # Calculate the minimun daily calories from user data
    user_data["minimun_daily_calories"] = fu_lib.get_minimum_daily_calories(
        weight=fu_lib.convert_weight(
            user_data.get("weight", 0),
            user_data.get("weight_unit", "kg"), "kg"),
        height=fu_lib.convert_height(
            user_data.get("height", 0),
            user_data.get("height_unit", "m"), "m"),
        age=user_data["age"],
        gender=user_data.get("gender", ""),
        exercise_days=fu_lib.interpret_string(
            user_data.get("training_days", "")),
        goal_code=user_data.get("goal_code", ""),
    )

    # Save elements not in "users" JSON table definition
    saved_elements = {
        "food_times": user_data.get("food_times", []),
        "user_history": user_data.get("user_history", [])
    }

    # Transform data (codes to descriptions)
    user_data = transform_code_desc("users", user_data)

    # Restore elements not in "users" JSON table definition
    user_data["food_times"] = saved_elements["food_times"]
    user_data["user_history"] = saved_elements["user_history"]

    # Removes the goal code from its description
    user_data["general_goal"] = re.sub(r'^[+-]?\d{1,2}%', '',
                                       user_data.get("goal_code", "")
                                       ).strip()

    # Prepare data to avoid send PII
    for attr_name in ["_id", "id", "firstname", "lastname", "email",
                      "birthday", "goal_code", "creation_date",
                      "update_date", "superuser", "passcode",
                      "passcode_repeat", ""]:
        if attr_name in user_data:
            del user_data[attr_name]

    result = get_default_resultset()
    result["resultset"] = user_data.copy()
    user_data = None
    if DEBUG:
        log_debug('AI_GUPR-2) get_user_profile_raw |' +
                  f' result: {result}')
    return result


@tool("get_full_user_profile", return_direct=True)
def get_full_user_profile(params: Any) -> str:
    """
Useful when you need to get an answer to the Human question made over the context of the user's complete profile, that includes: gender, weight, height, age, physical goals, other goals, training days, training hour, food times, historic data (weight, height, physical goals, and other goals), user's preferred food ingredients, user's dishes, and user's historic daily meals.
    """
    return get_full_user_profile_func(params)


def get_full_user_profile_func(params: Any) -> str:
    """
    Get an answer for a question made about the user's complete profile.
    """
    if params:
        params = interpret_tool_params(tool_params=params)
    else:
        params = {}
    if DEBUG:
        log_debug('AI_GFUP-1) get_full_user_profile' +
                  f' params: {params}')
    result = get_default_resultset()
    # Get the question
    question = cac.app_context.get_other_data("question")["content"]

    # Build the prompt
    prompt = f"You are {get_assistant_you_are(cac.app_context)}" + \
        "\n" + \
        f"Answer this question (in english please): {question}"

    # Get profile data
    result = get_full_user_profile_raw()
    if not result["error"]:
        titles = {
            "user_profile": "user's full profile, containing health, diet, nutrition and training data",
            'user_ingredient_list': "user's food preferences, preferred food ingredients",
            'dishes_list': "user's food preferences, preferred dishes",
            'daily_meal_list': "user's daily meals by date, to have an idea of his/her eating habits, daily calorie consumption and diet",
        }

        # Set the metadata
        json_metadata = prepare_metadata(
            metadata={},    # TODO: enrich the metadata...
            default_element_name="content"
        )

        # Vectorize the profile
        user_id = cac.get().get_user_id()
        json_filename = f"{user_id}_|name|.json"
        documents_list = []
        try:
            for item_name, item_data in result["resultset"].items():
                entries = index_dict(
                    json_content=item_data,
                    json_filename=json_filename.replace('|name|', item_name),
                    json_metadata=json_metadata,
                    title=titles.get(
                        item_name, "User's complete or full profile"),
                )
                documents_list.extend(entries)
        except Exception as err:
            result["error"] = True
            result["error_message"] = \
                "ERROR vectorizing the user's profile [AI-GFUP-E010]:" + \
                f" {str(err)}"

        # Ask the question to the model
        if not result["error"]:
            result = ask_ai(
                app_context=cac.get(),
                documents_list=documents_list,
                question=prompt,
                response_type="answer",
            )
    if DEBUG:
        log_debug('AI_GFUP-2) get_full_user_profile' +
                  f'\nquestion: {question}' +
                  f'\nprompt: {prompt}' +
                  f'\nresult: {result}')
    return standard_gpt_func_response(
        result=result,
        action_description="Thanks for you question. " +
        "According to your profile data:\n",
        include_resultset=True,
        additional_msg="",
        add_success_msg=False,
        json_result=False,
    )


def get_full_user_profile_raw() -> dict:
    """
    Get the user's full profile, including user's data like gender, weight,
    height, age, physical goals, other goals, training days, training hour,
    food times, historic data (weight, height, physical goals, and other
    goals), user's preferred food ingredients, user's dishes, and
    user's historic daily meals.

    Args:
        params (dict): parameters for the function.

    Returns:
        dict: the user's full profile resultset.
    """
    if DEBUG:
        log_debug('AI_GFUPR-1) get_full_user_profile_raw')
    result = get_default_resultset()
    # Get the full user profile
    result["resultset"] = {
        "user_profile": get_user_profile_raw(),
        "user_ingredient_list": get_user_ingredient_list_raw(),
        "dishes_list": get_dishes_list_raw(),
        "daily_meal_list": get_daily_meal_list_raw(),
    }
    # Reduce each element response unless the element has an error
    for k, val in result["resultset"].items():
        log_debug(f'get_full_user_profile_raw | k: {k} | val: {val}')
        if val["error"]:
            result["error"] = True
            result["error_message"] += ", {k}"
        else:
            result["resultset"][k] = \
                json.loads(val["resultset"]) \
                if isinstance(val["resultset"], str) \
                else val["resultset"]
    # Adjust the eventual error menssage
    if result["error"]:
        result["error_message"] = 'ERROR(s) in: ' + \
            result["error_message"].strip(", ")
    return result


def nutrition_analysis_prompt(
    food_items: str = "apple, banana",
    user_goal: str = "weight_loss",
    meal_type: str = "breakfast"
) -> str:
    """
    Generate a comprehensive nutrition analysis prompt.

    This helps ensure consistent, professional nutrition advice based on
    the user's goals and current eating patterns.
    """
    user_profile = get_user_profile_raw()
    if user_profile["error"]:
        return user_profile["error_message"]
    user_data = user_profile["resultset"]

    # Get user profile for personalized recommendations
    daily_calories = user_data["minimun_daily_calories"]

    return f"""
You are a certified nutritionist and health expert providing personalized advice.

User's Health Goal: {user_goal}
Meal Type: {meal_type}
Food Items to Analyze: {food_items}
Recommended Daily Calories: {int(daily_calories)} kcal

Guidelines for your analysis:
- Be professional but encouraging
- Focus on sustainable, healthy habits
- Provide specific, actionable recommendations
- Consider the user's caloric needs and goals
- Highlight both positive patterns and areas for improvement
- Suggest realistic meal improvements
- Include portion control advice when relevant

Generate a comprehensive nutrition analysis that:
1. Evaluates current eating patterns
2. Identifies strengths and areas for improvement
3. Provides specific recommendations
4. Suggests healthy alternatives
5. Offers encouragement and motivation

Keep your tone supportive and educational.
"""


def meal_planning_prompt(
    dietary_restrictions: str = "none",
    preferred_cuisines: str = "any",
    cooking_time: str = "moderate"
) -> str:
    """
    Generate a meal planning assistance prompt.

    Helps create consistent meal planning advice based on user preferences.
    """

    return f"""
You are an expert meal planner and nutritionist helping create healthy, balanced meals.

User Preferences:
- Dietary Restrictions: {dietary_restrictions}
- Preferred Cuisines: {preferred_cuisines}  
- Available Cooking Time: {cooking_time}

Your meal planning should:
- Create balanced meals with proper macronutrient ratios
- Consider the user's dietary restrictions and preferences
- Provide realistic cooking times and preparation methods
- Include variety to prevent meal fatigue
- Focus on whole, unprocessed foods when possible
- Provide specific ingredient lists and quantities
- Include preparation tips and cooking methods

Generate meal suggestions that are:
1. Nutritionally balanced
2. Practical to prepare
3. Aligned with user preferences
4. Cost-effective
5. Delicious and satisfying

Include both individual meal ideas and weekly planning strategies.
"""
