from sys import prefix

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.Home import home_router
from routes.User import user_router
from routes.Transaction import transaction_router
from routes.Prediction import prediction_router
from database.database import init_db
from database.config import get_settings
import uvicorn
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        FastAPI: Configured application instance
    """

    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(home_router, tags=['Home'])
    app.include_router(user_router, prefix='/api/users', tags=['Users'])
    app.include_router(transaction_router, prefix='/api/transaction', tags=['Transaction'])
    app.include_router(prediction_router, prefix='/api/prediction', tags=['Prediction'])

    return app

app = create_application()

@app.on_event("startup")
def on_startup():
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Application shutting down...")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run(
        'api:app',
        host='0.0.0.0',
        port=80,
        reload=True,
        log_level="info"
    )