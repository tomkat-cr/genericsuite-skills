"""
Billing AI Tools (eval fixture)
"""
from typing import Any
import json

from langchain.tools import tool
from pydantic import BaseModel, Field

from genericsuite.util.app_context import CommonAppContext

from genericsuite_ai.lib.ai_langchain_tools import (
    interpret_tool_params,
)
from genericsuite_ai.lib.ai_utilities import (
    gpt_func_error,
)

DEBUG = False
cac = CommonAppContext()


class InvoiceStatusParams(BaseModel):
    """
    get_invoice_status parameters
    """
    invoice_id: str = Field(description="Invoice ID to look up")


@tool
def get_invoice_status(params: Any) -> str:
    """
Useful to get the current status of an invoice by its ID.
Args: params (dict): Tool parameters. Must have: "invoice_id" (str): invoice ID.
    """  # noqa: E501
    return get_invoice_status_func(params)


def get_invoice_status_func(params: Any) -> str:
    """
    Get the current status of an invoice by its ID.
    """
    params = interpret_tool_params(
        tool_params=params,
        first_param_name="invoice_id",
        schema=InvoiceStatusParams)
    invoice_id = params.invoice_id
    if not invoice_id:
        return gpt_func_error('invoice_id is required')
    result = {
        "error": False,
        "error_message": None,
        "resultset": {"invoice_id": invoice_id, "status": "paid"},
    }
    return json.dumps(result)
