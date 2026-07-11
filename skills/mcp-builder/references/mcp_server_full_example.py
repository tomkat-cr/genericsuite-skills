#!/usr/bin/env python3
"""
ExampleApp MCP Server

A Model Context Protocol server that exposes the ExampleApp
food and nutrition management tools to AI clients.

This server provides:
- User ingredient management
- Dish creation and management
- Daily meal tracking
- User profile and health calculations
- FDA food database integration

Based on the ExampleApp's ai_gpt_fn_app.py and ai_gpt_fn_fda.py
"""

from typing import Dict, Any
import os

from genericsuite.mcplib.util.create_app import create_app
from genericsuite.mcplib.util.utilities import (
    mcp_authenticate,
    verify_app_context,
    tool_result,
    resource_result,
)
from genericsuite.util.app_logger import log_info

from lib.config.config import Config
from lib.models.ai_chatbot.ai_gpt_fn_fda import (
    cac as cac_fda_tools,
    get_fda_food_query_func,
)
from lib.models.ai_chatbot.ai_gpt_fn_app import (
    cac as cac_gpt_tools,
    create_user_ingredient_func,
    search_user_ingredient_func,
    get_user_ingredient_list_func,
    get_user_ingredient_list_raw,
    create_dish_func,
    search_dishes_func,
    get_dishes_list_func,
    get_dishes_list_raw,
    create_daily_meal_func,
    search_daily_meals_func,
    get_daily_meal_list_func,
    get_daily_meal_list_raw,
    get_user_profile_func,
    get_user_profile_raw,
    get_full_user_profile_func,

    nutrition_analysis_prompt as nutrition_analysis_prompt_func,
    meal_planning_prompt as meal_planning_prompt_func,

    # Dish,
    # DailyMeal,
)

DEBUG = False

# Initialize FastMCP server
settings = Config()
app = create_app(app_name=f'{settings.APP_NAME.lower()}-mcp-server',
                 settings=settings, log_file='mcp_server.log')
mcp = app.mcp
cac_object_list = [cac_gpt_tools, cac_fda_tools]


# ============================================================================
# DATA MODELS (Based on original ExampleApp structures)
# ============================================================================


# class NameSearch(BaseModel):
#     """Simple name search structure"""
#     name: str = Field(description="Name or partial name to search for")


# class DateSearch(BaseModel):
#     """Date search structure"""
#     find_date: str = Field(description="Date to search in YYYY-MM-DD format")

#     @field_validator("find_date", mode="after")
#     @classmethod
#     def validate_date_format(cls, v: str) -> str:
#         try:
#             datetime.strptime(v, '%Y-%m-%d')
#         except ValueError:
#             raise PydanticCustomError(
#                 "invalid_date_format",
#                 "Date must be in YYYY-MM-DD format, got {date}",
#                 {"date": v}
#             )
#         return v


# ============================================================================
# MCP TOOLS - USER AUTHENTICATION
# ============================================================================


@mcp.tool()
async def get_api_keys() -> Dict[str, Any]:
    """
    Get API keys
    """
    _ = DEBUG and log_info("Getting API keys")
    result = {
        "resultset": {
            "GS_USER_ID": os.environ.get("GS_USER_ID"),
            "GS_USER_NAME": os.environ.get("GS_USER_NAME"),
            "GS_API_KEY": os.environ.get("GS_API_KEY")
        }
    }
    return result


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
        else:
            return tool_result("Username and password are required")
    return mcp_authenticate(app, cac_object_list, username, password)


# ============================================================================
# MCP TOOLS - FDA FOOD DATABASE INTEGRATION
# ============================================================================


@mcp.tool()
async def get_fda_food_query(
    food_name: str, source_lang: str = "EN"
) -> Dict[str, Any]:
    """
    Get nutritional information for a food ingredient from FDA database.
    Returns name, description, calories, serving size and unit for the
    ingredient.
    """
    _ = DEBUG and log_info(f"FDA food query: {food_name}")
    verify_app_context(app, cac_object_list)
    result = get_fda_food_query_func({
        "food_name": food_name,
        "source_lang": source_lang
    })
    return tool_result(result, {"search_term": food_name})


# ============================================================================
# MCP TOOLS - USER INGREDIENT MANAGEMENT
# ============================================================================


@mcp.tool()
async def create_user_ingredient(
    name: str,
    calories_value: float,
    calories_unit: str = "kcal",
    serving_size: float = 100.0,
    serving_size_unit: str = "g",
    brand_name: str = "",
    observations: str = ""
) -> Dict[str, Any]:
    """
    Add a new user ingredient to their personal ingredient list.

    The ingredient will be stored with nutritional information and can be
    used later when creating dishes or daily meals.
    """
    _ = DEBUG and log_info(f"Creating user ingredient: {name}")
    verify_app_context(app, cac_object_list)
    result = create_user_ingredient_func({
        "name": name,
        "calories_value": calories_value,
        "calories_unit": calories_unit,
        "serving_size": serving_size,
        "serving_size_unit": serving_size_unit,
        "brand_name": brand_name,
        "observations": observations
    })
    return tool_result(result)


@mcp.tool()
async def search_user_ingredient(name: str) -> Dict[str, Any]:
    """
    Search user's ingredients by name.

    Returns all ingredients whose names contain the search term
    (case-insensitive).
    """
    _ = DEBUG and log_info(f"Searching user ingredients: {name}")
    verify_app_context(app, cac_object_list)
    result = search_user_ingredient_func({
        "name": name
    })
    return tool_result(result)


@mcp.tool()
async def get_user_ingredient_list() -> Dict[str, Any]:
    """
    Get all user's ingredients.

    Returns the complete list of ingredients the user has saved.
    """
    _ = DEBUG and log_info("Getting complete user ingredient list")
    verify_app_context(app, cac_object_list)
    result = get_user_ingredient_list_func()
    return tool_result(result)


# ============================================================================
# MCP TOOLS - DISH MANAGEMENT
# ============================================================================


@mcp.tool()
async def create_dish(
    name: str,
    calories_value: float,
    calories_unit: str,
    serving_size: float,
    serving_size_unit: str,
    brand_name: str,
    observations: str,
    ingredients: list[dict]
) -> Dict[str, Any]:
    """
    Create a new user dish with a list of ingredients and quantities.

    The dish is a collection of ingredients that can be reused in daily meals.
    Total calories are automatically calculated from all ingredients.
    """
    _ = DEBUG and log_info(f"Creating dish: {name}")
    verify_app_context(app, cac_object_list)
    result = create_dish_func({
        "name": name,
        "ingredients": ingredients,
        "calories_value": calories_value,
        "calories_unit": calories_unit,
        "serving_size": serving_size,
        "serving_size_unit": serving_size_unit,
        "brand_name": brand_name,
        "observations": observations
    })
    return tool_result(result)


@mcp.tool()
async def search_dishes(name: str) -> Dict[str, Any]:
    """
    Search user's dishes by name.

    Returns all dishes whose names contain the search term (case-insensitive).
    """
    _ = DEBUG and log_info(f"Searching dishes: {name}")
    verify_app_context(app, cac_object_list)
    result = search_dishes_func({
        "name": name
    })
    return tool_result(result)


@mcp.tool()
async def get_dishes_list() -> Dict[str, Any]:
    """
    Get all user's dishes.

    Returns the complete list of dishes the user has created.
    """
    _ = DEBUG and log_info("Getting complete dishes list")
    verify_app_context(app, cac_object_list)
    result = get_dishes_list_func()
    return tool_result(result)


# ============================================================================
# MCP TOOLS - DAILY MEAL MANAGEMENT
# ============================================================================


@mcp.tool()
async def create_daily_meal(
    meal_date: str,
    observations: str,
    ingredients: list[dict]
) -> Dict[str, Any]:
    """
    Add a new daily meal for a specific date.

    This tracks what the user ate on a particular day, organized by meal types
    (breakfast, lunch, dinner, etc.). If a meal for this date already exists,
    the ingredients will be added to it.
    """
    _ = DEBUG and log_info(f"Creating daily meal for date: {meal_date}")
    verify_app_context(app, cac_object_list)
    result = create_daily_meal_func({
        "meal_date": meal_date,
        "observations": observations,
        "ingredients": ingredients
    })
    return tool_result(result)


@mcp.tool()
async def search_daily_meals(find_date: str) -> Dict[str, Any]:
    """
    Search user's daily meals by date.

    Useful for questions like "what did I eat yesterday?" or
    "how many calories did I consume today?"
    """
    _ = DEBUG and log_info(f"Searching daily meals for date: {find_date}")
    verify_app_context(app, cac_object_list)
    result = search_daily_meals_func({
        "find_date": find_date
    })
    return tool_result(result)


@mcp.tool()
async def get_daily_meal_list() -> Dict[str, Any]:
    """
    Get all user's daily meals, ordered by meal date descending.

    Useful to understand the user's eating habits and meal history.
    """
    _ = DEBUG and log_info("Getting complete daily meal list")
    verify_app_context(app, cac_object_list)
    result = get_daily_meal_list_func()
    return tool_result(result)


# ============================================================================
# MCP TOOLS - USER PROFILE MANAGEMENT
# ============================================================================


@mcp.tool()
async def get_user_profile() -> Dict[str, Any]:
    """
    Get user's summary profile.

    The profile contains health data like gender, weight, height, age,
    physical goals, training days, and calculated minimum daily calories.
    """
    _ = DEBUG and log_info("Getting user summary profile")
    verify_app_context(app, cac_object_list)
    result = get_user_profile_func({})
    return tool_result(result)


@mcp.tool()
async def get_full_user_profile() -> Dict[str, Any]:
    """
    Get user's complete profile including eating habits.

    This includes health data, preferred ingredients, dishes, and meal history.
    Useful for comprehensive analysis of the user's nutrition and health
    patterns.
    """
    _ = DEBUG and log_info("Getting complete user profile with eating habits")
    verify_app_context(app, cac_object_list)
    result = get_full_user_profile_func({})
    return tool_result(result)


# ============================================================================
# MCP RESOURCES - DATA ACCESS
# ============================================================================


@mcp.resource("user://login/{username}/{password}",
              mime_type="application/json")
async def authenticate(
    username: str,
    password: str,
) -> str:
    """
    Get user login as a resource
    """
    _ = DEBUG and log_info("Getting user login for resource")
    return mcp_authenticate(app, cac_object_list, username, password)


@mcp.resource("user://profile")
async def user_profile_resource() -> str:
    """
    Get user profile as a resource
    """
    # Call the underlying function logic directly
    _ = DEBUG and log_info("Getting user summary profile for resource")
    verify_app_context(app, cac_object_list)
    return resource_result(get_user_profile_raw())


@mcp.resource("user://ingredients")
async def user_ingredients_resource() -> str:
    """
    Get user ingredients as a resource
    """
    # Call the underlying function logic directly
    _ = DEBUG and log_info(
        "Getting complete user ingredient list for resource")
    verify_app_context(app, cac_object_list)
    return resource_result(get_user_ingredient_list_raw())


@mcp.resource("user://dishes")
async def user_dishes_resource() -> str:
    """
    Get user dishes as a resource
    """
    _ = DEBUG and log_info("Getting complete dishes list for resource")
    verify_app_context(app, cac_object_list)
    return resource_result(get_dishes_list_raw())


@mcp.resource("user://meals")
async def user_meals_resource() -> str:
    """
    Get user daily meals as a resource
    """
    _ = DEBUG and log_info("Getting complete daily meal list for resource")
    verify_app_context(app, cac_object_list)
    return resource_result(get_daily_meal_list_raw())


# ============================================================================
# MCP PROMPTS - RESPONSE TEMPLATES
# ============================================================================


@mcp.prompt("nutrition_analysis")
async def nutrition_analysis_prompt(
    food_items: str = "apple, banana",
    user_goal: str = "weight_loss",
    meal_type: str = "breakfast"
) -> str:
    """
    Generate a comprehensive nutrition analysis prompt.

    This helps ensure consistent, professional nutrition advice based on
    the user's goals and current eating patterns.
    """
    verify_app_context(app, cac_object_list)
    return nutrition_analysis_prompt_func(
        food_items=food_items,
        user_goal=user_goal,
        meal_type=meal_type
    )


@mcp.prompt("meal_planning")
async def meal_planning_prompt(
    dietary_restrictions: str = "none",
    preferred_cuisines: str = "any",
    cooking_time: str = "moderate"
) -> str:
    """
    Generate a meal planning assistance prompt.

    Helps create consistent meal planning advice based on user preferences.
    """
    verify_app_context(app, cac_object_list)
    return meal_planning_prompt_func(
        dietary_restrictions=dietary_restrictions,
        preferred_cuisines=preferred_cuisines,
        cooking_time=cooking_time
    )


# ============================================================================
# SERVER STARTUP AND CONFIGURATION
# ============================================================================


def main():
    """
    Main entry point for the ExampleApp MCP Server
    """

    print("🥗 Starting ExampleApp Food & Nutrition MCP Server...")
    print("\n📋 Available Tools:")
    print("   🔍 FDA Food Database:")
    print("      - get_fda_food_query: Search FDA food database")
    print("   🥘 User Ingredients:")
    print("      - create_user_ingredient: Add new ingredient")
    print("      - search_user_ingredient: Search ingredients by name")
    print("      - get_user_ingredient_list: Get all user ingredients")
    print("   🍽️  Dishes:")
    print("      - create_dish: Create dish with ingredients")
    print("      - search_dishes: Search dishes by name")
    print("      - get_dishes_list: Get all user dishes")
    print("   📅 Daily Meals:")
    print("      - create_daily_meal: Add daily meal entry")
    print("      - search_daily_meals: Search meals by date")
    print("      - get_daily_meal_list: Get all meal history")
    print("   👤 User Profile:")
    print("      - get_user_profile: Get basic profile")
    print("      - get_full_user_profile: Get complete profile with habits")

    print("\n📂 Available Resources:")
    print("      - user://profile: User profile data")
    print("      - user://ingredients: User ingredients data")
    print("      - user://dishes: User dishes data")
    print("      - user://meals: User meals data")

    print("\n📝 Available Prompts:")
    print("      - nutrition_analysis: Generate nutrition analysis")
    print("      - meal_planning: Generate meal planning advice")

    print("\n✅ Server ready for connections!")

    # Run the FastMCP server
    app.run()


if __name__ == "__main__":
    main()
