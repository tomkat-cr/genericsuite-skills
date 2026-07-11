"""
AI Langchain Tools and GPT functions management
(eval fixture — intentionally partial: only the functions dict and cac
list are populated; used for byte-comparison in evals, not as an exemplar)
"""
from genericsuite.util.app_logger import log_debug
from genericsuite.util.app_context import AppContext

from genericsuite_ai.lib.ai_gpt_functions import (
    get_functions_dict,
)

from lib.config.config import Config

from lib.models.ai_chatbot.ai_gpt_fn_billing import (
    cac as cac_billing,
    get_invoice_status,
    get_invoice_status_func,
)

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
        result = {"get_invoice_status": get_invoice_status}
    else:
        # GPT Functions (the plain *_func callables)
        result = {"get_invoice_status": get_invoice_status_func}
    return result


def additional_gpt_func_appcontexts(
    app_context: AppContext,
) -> list:
    """
    CommonAppContext (cac) objects of every app tool module.
    Filled by the python-ai-tools-code-builder skill.
    """
    return [cac_billing]


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
