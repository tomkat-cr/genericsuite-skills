"""
FastAPI main
"""
from genericsuite_ai.fastapilib.util.create_app import (
    create_app,
    create_handler,
)

from lib.config.config import Config

from lib.routers import ai_assistant as ai_chatbot_endpoint
from lib.routers import parameters as parameters_endpoint


settings = Config()
app = create_app(app_name=f'{settings.APP_NAME.lower()}-backend',
                 settings=settings)

# Register application specific endpoints
app.include_router(parameters_endpoint.router,
                   prefix=f'/{settings.API_VERSION}/parameters')

# Register AI endpoints
app.include_router(ai_chatbot_endpoint.router,
                   prefix=f'/{settings.API_VERSION}/ai')

handler = create_handler(app)
