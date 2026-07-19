"""
FastAPI ExampleApp main
"""
# import os
from mangum import Mangum

from genericsuite_ai.fastapilib.util.create_app import create_app

from lib.config.config import Config

from lib.routers import ai_assistant as ai_chatbot_endpoint
from lib.routers import food_moments
from lib.routers import fda_food_endpoint

# ############################

# from genericsuite.fastapilib.util.create_app import create_handler


def create_handler(app_object):
    """
    Returns the FastAPI App as a valid AWS Lambda Function handler
    """
    return Mangum(app_object, lifespan="off")

# ############################


settings = Config()
app = create_app(app_name=f'{settings.APP_NAME.lower()}-backend',
                 settings=settings)

# Register application specific endpoints
app.include_router(
    food_moments.router,
    prefix=f'/{settings.API_VERSION}/food_moments')
app.include_router(
    fda_food_endpoint.router, prefix=f'/{settings.API_VERSION}/fda_food_query'
)

# Register AI endpoints
app.include_router(
    ai_chatbot_endpoint.router,
    prefix=f'/{settings.API_VERSION}/ai')

handler = create_handler(app)
