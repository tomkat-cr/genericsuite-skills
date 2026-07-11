"""
AI Langchain Tools and GPT functions management
"""
from genericsuite.util.app_logger import log_debug
from genericsuite.util.app_context import AppContext

from genericsuite_ai.lib.ai_gpt_functions import (
    get_functions_dict,
)

from lib.config.config import Config
from lib.models.ai_chatbot.ai_gpt_fn_fda import (
    cac as cac_fda,
    get_fda_food_query,
    get_fda_food_query_func,
)

from lib.models.ai_chatbot.ai_gpt_fn_app import (
    cac as cac_app,
    create_user_ingredient,
    create_user_ingredient_func,
    search_user_ingredient,
    search_user_ingredient_func,
    get_user_ingredient_list,
    get_user_ingredient_list_func,
    create_dish,
    create_dish_func,
    search_dishes,
    search_dishes_func,
    get_dishes_list,
    get_dishes_list_func,
    create_daily_meal,
    create_daily_meal_func,
    search_daily_meals,
    search_daily_meals_func,
    get_daily_meal_list,
    get_daily_meal_list_func,
    get_user_profile,
    get_user_profile_func,
    get_full_user_profile,
    get_full_user_profile_func,
)

DEBUG = False
EXTRA_DEBUG = False


def assign_app_specific_gpt_functions(
    app_context: AppContext,
) -> None:
    """
    Assign specific ExampleApp GPT functions
    """
    _ = DEBUG and log_debug('ASSIGN_APP_SPECIFIC_GPT_FUNCTIONS |'
                            ' Assigning App-specific GPT functions')
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
    Get the available ChatGPT functions and its callables (app-specific).

    Returns:
        dict: A dictionary containing the available ChatGPT functions
        and its callable.
    """
    _ = DEBUG and log_debug('GET_ADDITIONAL_FUNCTIONS_DICT |'
                            ' Assigning App-specific GPT functions dict')
    settings = Config(app_context)
    is_lc = settings.AI_TECHNOLOGY == 'langchain'
    if is_lc:
        # Langchain Tools
        result = {
            "get_fda_food_query": get_fda_food_query,
            "create_user_ingredient": create_user_ingredient,
            "search_user_ingredient": search_user_ingredient,
            "get_user_ingredient_list": get_user_ingredient_list,
            "create_dish": create_dish,
            "search_dishes": search_dishes,
            "get_dishes_list": get_dishes_list,
            "create_daily_meal": create_daily_meal,
            "search_daily_meals": search_daily_meals,
            "get_daily_meal_list": get_daily_meal_list,
            "get_user_profile": get_user_profile,
            "get_full_user_profile": get_full_user_profile,
        }
    else:
        # GPT Functions
        result = {
            "get_fda_food_query": get_fda_food_query_func,
            "create_user_ingredient": create_user_ingredient_func,
            "search_user_ingredient": search_user_ingredient_func,
            "get_user_ingredient_list": get_user_ingredient_list_func,
            "create_dish": create_dish_func,
            "search_dishes": search_dishes_func,
            "get_dishes_list": get_dishes_list_func,
            "create_daily_meal": create_daily_meal_func,
            "search_daily_meals": search_daily_meals_func,
            "get_daily_meal_list": get_daily_meal_list_func,
            "get_user_profile": get_user_profile_func,
            "get_full_user_profile": get_full_user_profile_func,
        }
    if DEBUG and EXTRA_DEBUG:
        log_debug(f"EXAMPLEAPP GET_FUNCTIONS_DICT | is_lc: {is_lc}" +
                  f" result: {result}")
    return result


def additional_gpt_func_appcontexts(
    app_context: AppContext,
) -> list:
    """
    Assign the app_context to the ChatGPT functions.

    Args:
        app_context (AppContext): GPT Context
    """
    _ = DEBUG and \
        log_debug('ADDITIONAL_GPT_FUNC_APPCONTEXTS |' +
                  ' Assigning App-specific additional GPT function' +
                  ' AppContexts')
    available_func_context = [
        cac_fda,
        cac_app,
    ]
    return available_func_context


def additional_run_one_function(
    app_context: AppContext,
    function_name: str,
    function_args: dict,
) -> dict:
    """
    Execute a function based on the given function_name
    and function_args.

    Args:
        app_context (AppContext): GPT Context
        function_name (str): function name
        function_args (dict): function args

    Returns:
        The result of the function execution.
    """
    _ = DEBUG and log_debug('ADDITIONAL_RUN_ONE_FUNCTION |' +
                            ' App-specific run_one_function')
    user_lang = app_context.get_user_data().get('language', 'auto')
    available_functions = get_functions_dict(app_context)
    fuction_to_call = available_functions[function_name]
    function_response = None
    _ = DEBUG and \
        log_debug("AI_FA_ROF-1) run_one_function_from_chatgpt" +
                  f" | function_name: {function_name}" +
                  f" | function_args: {function_args}")

    if function_name == "get_fda_food_query":
        function_response = fuction_to_call(
            params={
                "food_name": function_args.get("food_name"),
                "source_lang": user_lang,
            }
        )
    elif function_name == "create_user_ingredient":
        function_response = fuction_to_call(
            params={
                "name": function_args.get("name"),
                "calories_value": function_args.get("calories_value"),
                "calories_unit": function_args.get("calories_unit"),
                "serving_size": function_args.get("serving_size"),
                "serving_size_unit": function_args.get("serving_size_unit"),
                "brand_name": function_args.get("brand_name"),
                "observations": function_args.get("observations"),
            }
        )
    elif function_name == "search_user_ingredient":
        function_response = fuction_to_call(
            params={
                "name": function_args.get("name"),
            }
        )
    elif function_name == "get_user_ingredient_list":
        function_response = fuction_to_call(
            params={}
        )
    elif function_name == "create_dish":
        function_response = fuction_to_call(
            params={
                "dish_name": function_args.get("dish_name"),
                "calories_value": function_args.get("calories_value"),
                "calories_unit": function_args.get("calories_unit"),
                "serving_size": function_args.get("serving_size"),
                "serving_size_unit": function_args.get("serving_size_unit"),
                "brand_name": function_args.get("brand_name"),
                "observations": function_args.get("observations"),
                "ingredients": function_args.get("ingredients"),
            }
        )
    elif function_name == "search_dishes":
        function_response = fuction_to_call(
            params={
                "name": function_args.get("name"),
            }
        )
    elif function_name == "get_dishes_list":
        function_response = fuction_to_call(
            params={}
        )
    elif function_name == "create_daily_meal":
        function_response = fuction_to_call(
            params={
                "meal_date": function_args.get("meal_date"),
                "observations": function_args.get("observations"),
                "ingredients": function_args.get("ingredients"),
            }
        )
    elif function_name == "search_daily_meals":
        function_response = fuction_to_call(
            params={
                "name": function_args.get("find_date"),
            }
        )
    elif function_name == "get_daily_meal_list":
        function_response = fuction_to_call(
            params={}
        )
    elif function_name == "get_user_profile":
        function_response = fuction_to_call(
            params={}
        )
    elif function_name == "get_full_user_profile":
        function_response = fuction_to_call(
            params={}
        )

    result = {
        "function_response": function_response,
        "function_name": function_name,
        "function_args": function_args,
    }
    _ = DEBUG and \
        log_debug('AI_FA_ROF-2) run_one_function_from_chatgpt' +
                  f' | result: {result}')
    return result


def get_additional_function_specs(
    app_context: AppContext,
) -> list:
    """
    Get the ChatGPT function specifications (parameters, documentation).

    Returns:
        list[dict]: A list of dictionaries containing the available
        ChatGPT functions.
    """
    _ = DEBUG and log_debug('GET_ADDITIONAL_FUNCTION_SPECS |' +
                            ' App-specific additional GPT function specs')
    _ = DEBUG and \
        log_debug("AI_FA_GFS-1) get_function_specs")
    result = [{
        "name": "get_fda_food_query",
        "description": "Get the name, description, calories, serving size" +
        " amount and serving size unit in a given food ingredient.",
        "parameters": {
            "type": "object",
            "properties": {
                "food_name": {
                    "type": "string",
                    "description": "The name of the food ingredient,"
                    " e.g. brocoli",
                },
                "source_lang": {
                    "type": "string",
                    "description": "The original language of the food " +
                    "ingredient, e.g. es, fr, en",
                },
            },
            "required": ["food_name"],
        },
    }, {
        "name": "create_user_ingredient",
        "description": "Add a new user ingredient without a quantity" +
        ". e.g.: add brocoli to my ingredients",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the" +
                    " ingredient",
                },
                "calories_value": {
                    "type": "number",
                    "description": "The calories value of" +
                    " the ingredient",
                },
                "calories_unit": {
                    "type": "string",
                    "description": "The calories unit code" +
                    " of the ingredient." +
                    " Preferred value: kcal",
                },
                "serving_size": {
                    "type": "number",
                    "description": "The serving size of the" +
                    " ingredient",
                },
                "serving_size_unit": {
                    "type": "string",
                    "description": "The serving size unit" +
                    " code of the ingredient. It could be: " +
                    "Grams (g), " +
                    "Unit (u), " +
                    "Tea spoon (tsp), " +
                    "Table spoon (tablespoon), " +
                    "Bowl (bowl), " +
                    "Cup (cup), " +
                    "Small Cup (scup), " +
                    "Milliliters (ml), " +
                    "Milligrams (mg), " +
                    "Micro grams (ug), " +
                    "Ounce (oz), " +
                    "Pound (lb), " +
                    "International units (iu), " +
                    "Mass, length, time (mlt), " +
                    "Note: codes are between parenthesis"
                },
                "brand_name": {
                    "type": "string",
                    "description": "The brand name of"
                    " the ingredient (value can be blank)",
                },
                "observations": {
                    "type": "string",
                    "description": "Any observations about" +
                    " the ingredient (value can be blank)",
                },
            },
            "required": [
                "name",
                "calories_value",
                "calories_unit",
                "serving_size",
                "serving_size_unit",
                "brand_name",
                "observations",
            ],
        },
    }, {
        "name": "search_user_ingredient",
        "description": "Search for user's ingredients by name.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "description": "the string to search, contained in the" +
                    " ingredient name",
                    "type": "string",
                }
            }
        },
        "required": ["name"],
    }, {
        "name": "get_user_ingredient_list",
        "description": "Get all the user's preferred ingredients",
        "parameters": {
            "type": "object",
            "properties": {
            }
        },
        "required": [],
    }, {
        "name": "create_dish",
        "description": "Create a new user dish with a list of ingredients" +
        " and quantities with no specific date",
        "parameters": {
            "type": "object",
            "properties": {
                "dish_name": {
                    "type": "string",
                    "description": "The name of the dish",
                },
                "calories_value": {
                    "type": "number",
                    "description": "The calories value of" +
                    " the dish",
                },
                "calories_unit": {
                    "type": "string",
                    "description": "The calories unit code" +
                    " of the dish." +
                    " Preferred value: kcal",
                },
                "serving_size": {
                    "type": "number",
                    "description": "The serving size of the" +
                    " dish",
                },
                "serving_size_unit": {
                    "type": "string",
                    "description": "The serving size unit " +
                    "code of the dish. The preferred value is 'u'. " +
                    "Available codes are: " +
                    "Grams (g), " +
                    "Unit (u), " +
                    "Tea spoon (tsp), " +
                    "Table spoon (tablespoon), " +
                    "Cup (cup), " +
                    "Small Cup (scup), " +
                    "Milliliters (ml), " +
                    "Milligrams (mg), " +
                    "Micro grams (ug), " +
                    "Ounce (oz), " +
                    "Pound (lb), " +
                    "International units (iu), " +
                    "Mass, length, time (mlt), " +
                    "Note: the codes are between parenthesis"
                },
                "brand_name": {
                    "type": "string",
                    "description": "The brand name of"
                    " the dish (value can be blank)",
                },
                "observations": {
                    "type": "string",
                    "description": "Any observations about" +
                    " the dish (value can be blank)",
                },
                "ingredients": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the" +
                                " ingredient",
                            },
                            "calories_value": {
                                "type": "number",
                                "description": "The calories value of" +
                                " the ingredient",
                            },
                            "calories_unit": {
                                "type": "string",
                                "description": "The calories unit code" +
                                " of the ingredient." +
                                " Preferred value: kcal",
                            },
                            "serving_size": {
                                "type": "number",
                                "description": "The serving size of the" +
                                " ingredient",
                            },
                            "serving_size_unit": {
                                "type": "string",
                                "description": "The serving size unit" +
                                " code of the ingredient. It could be: " +
                                "Grams (g), " +
                                "Unit (u), " +
                                "Tea spoon (tsp), " +
                                "Table spoon (tablespoon), " +
                                "Cup (cup), " +
                                "Small Cup (scup), " +
                                "Milliliters (ml), " +
                                "Milligrams (mg), " +
                                "Micro grams (ug), " +
                                "Ounce (oz), " +
                                "Pound (lb), " +
                                "International units (iu), " +
                                "Mass, length, time (mlt), " +
                                "Note: codes are between parenthesis"
                            },
                            "quantity": {
                                "type": "number",
                                "description": "The quantity of the" +
                                " ingredient",
                            },
                            "brand_name": {
                                "type": "string",
                                "description": "The brand name of"
                                " the ingredient (value can be blank)",
                            },
                            "observations": {
                                "type": "string",
                                "description": "Any observations about" +
                                " the ingredient (value can be blank)",
                            },
                        },
                        "required": [
                            "name",
                            "calories_value",
                            "calories_unit",
                            "serving_size",
                            "serving_size_unit",
                            "quantity",
                            "brand_name",
                            "observations",
                        ],
                    },
                    "description": "The ingredients of the dish",
                },
            },
            "required": ["dish_name", "ingredients"],
        },
    }, {
        "name": "search_dishes",
        "description": "Search user's dishes by name. The function" +
        " searches for names that contains the search string",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "description": "the string to search, contained in the" +
                    " dish name",
                    "type": "string",
                }
            }
        },
        "required": ["name"],
    }, {
        "name": "get_dishes_list",
        "description": "Get all user's dishes.",
        "parameters": {
            "type": "object",
            "properties": {
            }
        },
        "required": [],
    }, {
        "name": "create_daily_meal",
        "description": "Add a new daily meal for a specific date." +
        " Useful when the user ask to e.g. 'add a meat soup to my" +
        " yesterday's meals', or' add a hamburger to my meal of" +
        " november 14th, 2023', or 'add 2 broiled eggs to today's" +
        " breakfast'",
        "parameters": {
            "type": "object",
            "properties": {
                "meal_date": {
                    "type": "string",
                    "description": "The date of the meal",
                },
                "observations": {
                    "type": "string",
                    "description": "Any observations about the meal" +
                    " (value can be blank)",
                },
                "ingredients": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "meal_type": {
                                "type": "string",
                                "description": "Meal type" +
                                " (e.g., Breakfast, Brunch, Elevenses," +
                                " Lunch, Tea, Supper, Dinner" +
                                " Other, Unassigned).",
                            },
                            "name": {
                                "type": "string",
                                "description": "The name of the" +
                                " ingredient",
                            },
                            "calories_value": {
                                "type": "number",
                                "description": "The calories value of" +
                                " the ingredient",
                            },
                            "calories_unit": {
                                "type": "string",
                                "description": "The calories unit code" +
                                " of the ingredient." +
                                " Preferred value: kcal",
                            },
                            "serving_size": {
                                "type": "number",
                                "description": "The serving size of the" +
                                " ingredient",
                            },
                            "serving_size_unit": {
                                "type": "string",
                                "description": "The serving size unit" +
                                " code of the ingredient. It could be: " +
                                "Grams (g), " +
                                "Unit (u), " +
                                "Tea spoon (tsp), " +
                                "Table spoon (tablespoon), " +
                                "Cup (cup), " +
                                "Small Cup (scup), " +
                                "Milliliters (ml), " +
                                "Milligrams (mg), " +
                                "Micro grams (ug), " +
                                "Ounce (oz), " +
                                "Pound (lb), " +
                                "International units (iu), " +
                                "Mass, length, time (mlt), " +
                                "Note: codes are between parenthesis"
                            },
                            "quantity": {
                                "type": "number",
                                "description": "The quantity of the" +
                                " ingredient",
                            },
                            "brand_name": {
                                "type": "string",
                                "description": "The brand name of"
                                " the ingredient (value can be blank)",
                            },
                            "observations": {
                                "type": "string",
                                "description": "Any observations about" +
                                " the ingredient (value can be blank)",
                            },
                        },
                        "required": [
                            "name",
                            "calories_value",
                            "calories_unit",
                            "serving_size",
                            "serving_size_unit",
                            "quantity",
                            "brand_name",
                            "observations",
                        ],
                    },
                    "description": "The ingredients of the meal",
                },
            },
            "required": ["meal_date", "observations", "ingredients"],
        },
    }, {
        "name": "search_daily_meals",
        "description": "Search user's daily meals by date. Useful to" +
        " answer questions like 'give me the total calories I consumed" +
        " today', or 'how many calories I consumed during the last" +
        " week?', or 'what are the meals I ate the most last month?'." +
        " the meal date comes as a timestamp in the 'meal_date'" +
        " attribute. Calulate the 'find_date' date or date ranges" +
        " separated by comma before call this function, because it" +
        " only admits dates with format YYYY-MM-DD.",
        "parameters": {
            "type": "object",
            "properties": {
                "find_date": {
                    "description": "one date or date range with" +
                    " format YYYY-MM-DD. It does not admit other formats" +
                    " for dates, nor words like today, yesterday, etc," +
                    " nor function names." +
                    " For date ranges separate the dates by comma." +
                    " To filter from a date until today, specify the date" +
                    " and a comma. To filter from the begining until a date," +
                    " specify a comma and the date. To filter" +
                    " a single day, specify the date without commas.",
                    "type": "string",
                }
            }
        },
        "required": ["find_date"],
    }, {
        "name": "get_daily_meal_list",
        "description": "Get all user's daily meals, ordered by meal_date." +
        " Useful too know the user's meal habits." +
        " descending.",
        "parameters": {
            "type": "object",
            "properties": {
            }
        },
        "required": [],
    }, {
        "name": "get_user_profile",
        "description": "Get the user profile without the eating habits." +
        " The profile contains data like:" +
        " gender, weight, height, age, physical health goals," +
        " other goals, training days, training hour, food times, historic" +
        " data (weight, height, physical goals, and other goals)." +
        " The user may reffer to this profile as 'my profile', 'search in" +
        " my profile', 'it is in my profile', 'health profile', " +
        " 'my health condition', and things like that." +
        "",
        "parameters": {
            "type": "object",
            "properties": {
            }
        },
        "required": [],
    }, {
        "name": "get_full_user_profile",
        "description": "Get an answer for a question made about the user's" +
        " complete profile. The full user profile contains eating habits" +
        " and data like: gender, weight, height, age, physical goals, other" +
        " goals, training days, training hour, food times, historic data" +
        "  (weight,  height, physical goals, and other goals), user's" +
        " preferred food ingredients, user's dishes, and user's historic" +
        " daily meals. This full profile contains all the information" +
        " about the user: health, diet, nutrition and training data." +
        " The user may reffer to this profile as 'my profile', 'search in" +
        " my profile', 'it is in my profile', 'health profile', 'nutrition" +
        " profile', 'my diet habits', 'my health condition', 'all my" +
        " profile', 'according to my profile', and things like that.",
        "parameters": {
            "type": "object",
            "properties": {
            }
        },
        "required": [],
    }]
    return result
