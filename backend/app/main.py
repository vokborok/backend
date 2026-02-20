import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config_manager

logging.basicConfig(
    level=getattr(logging, config_manager.app_config.log_level),
    format=config_manager.app_config.log_format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {os.getenv('GAME_NAME', 'ExampleGame')} Server...")

    from app.migrations import run_migrations_with_retry
    logger.info("Running database migrations...")
    migration_success = run_migrations_with_retry(max_retries=2, delay=2)

    if not migration_success:
        logger.warning("Database migrations failed! Continuing server startup...")
    else:
        logger.info("Database migrations completed successfully")

    logger.info("Server started successfully")

    yield

    logger.info("Shutting down server...")
    logger.info("Server shutdown complete")


game_prefix = os.getenv("GAME_PREFIX", "eg")

app = FastAPI(
    title=config_manager.app_config.title,
    version=config_manager.app_config.version,
    docs_url=config_manager.app_config.docs_url,
    redoc_url=config_manager.app_config.redoc_url,
    openapi_url=config_manager.app_config.openapi_url,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config_manager.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.users.routes import users_router
from app.energy.routes import energy_router
from app.game.routes import game_router
from app.tg.routes import telegram_router

app.include_router(users_router, prefix=f"/{game_prefix}", tags=["users"])
app.include_router(energy_router, prefix=f"/{game_prefix}", tags=["energy"])
app.include_router(game_router, prefix=f"/{game_prefix}", tags=["game"])
app.include_router(telegram_router, prefix="/telegram", tags=["telegram"])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": config_manager.app_config.version,
        "game": os.getenv("GAME_NAME", "ExampleGame"),
        "environment": "production" if config_manager.is_production() else "development"
    }


@app.get("/info")
async def app_info():
    return {
        "name": config_manager.app_config.title,
        "version": config_manager.app_config.version,
        "game_prefix": game_prefix,
        "environment": "production" if config_manager.is_production() else "development",
        "features": {
            "users": True,
            "energy": True,
            "telegram": True,
            "analytics": os.getenv("ANALYTICS_ENABLED", "false").lower() == "true"
        }
    }


if config_manager.app_config.enable_metrics:
    @app.get(config_manager.app_config.metrics_path)
    async def metrics():
        return {
            "cache_stats": {"status": "active", "type": "in_memory"},
            "database_stats": {
                "status": "connected",
                "pool_size": config_manager.get_database_config().pool_size if config_manager.get_database_config() else "unknown"
            }
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn_config = {
        "host": "0.0.0.0",
        "port": 8000,
        "log_level": config_manager.app_config.log_level.lower(),
    }

    if config_manager.is_production():
        uvicorn_config.update({
            "workers": 4,
            "access_log": False,
        })
    else:
        uvicorn_config.update({
            "reload": True,
            "reload_dirs": ["app"],
        })

    logger.info(f"Starting server with config: {uvicorn_config}")
    uvicorn.run("app.main:app", **uvicorn_config)
