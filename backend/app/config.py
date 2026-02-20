import os
from typing import List, Optional

from pydantic import BaseModel, Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    dsn: PostgresDsn
    pool_size: int = Field(default=20)
    max_overflow: int = Field(default=30)
    pool_recycle: int = Field(default=3600)
    echo: bool = Field(default=False)


class CacheConfig(BaseModel):
    default_ttl: int = Field(default=300)
    config_ttl: int = Field(default=600)
    user_ttl: int = Field(default=60)
    cleanup_interval: int = Field(default=300)


class PerformanceConfig(BaseModel):
    slow_query_threshold: float = Field(default=1.0)
    rate_limit_per_minute: int = Field(default=60)
    compression_min_size: int = Field(default=1000)
    batch_size: int = Field(default=100)


class GameEnv(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    postgres: DatabaseConfig
    secret_key: SecretStr = Field(alias="SECRET_KEY__JWT")
    tg_bot_token: SecretStr = Field(alias="TG_BOT_TOKEN")

    cache: CacheConfig = Field(default_factory=CacheConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)

    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True)

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"


class AppConfig(BaseModel):
    title: str = Field(default="ExampleGame Server")
    version: str = Field(default="1.0.0")

    cors_origins: List[str] = Field(
        default=[
            "https://localhost",
            "http://localhost",
            "http://localhost:3000",
        ]
    )

    api_prefix: str = Field(default="")
    docs_url: Optional[str] = Field(default="/docs")
    redoc_url: Optional[str] = Field(default="/redoc")
    openapi_url: Optional[str] = Field(default="/openapi.json")

    log_level: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    enable_metrics: bool = Field(default=True)
    metrics_path: str = Field(default="/metrics")


def create_configs() -> tuple[Optional[GameEnv], AppConfig]:
    try:
        game_env = GameEnv()
    except Exception:
        game_env = None

    app_config = AppConfig(
        title=f"{os.getenv('GAME_NAME', 'ExampleGame')} Server"
    )

    if game_env and game_env.is_production:
        app_config.docs_url = None
        app_config.redoc_url = None
        app_config.openapi_url = None
        app_config.log_level = "WARNING"

    return game_env, app_config


game_env, app_config = create_configs()


class ConfigManager:
    def __init__(self) -> None:
        self.game_env = game_env
        self.app_config = app_config

    def get_database_config(self) -> Optional[DatabaseConfig]:
        if self.game_env:
            return self.game_env.postgres
        return None

    def get_cache_config(self) -> CacheConfig:
        if self.game_env:
            return self.game_env.cache
        return CacheConfig()

    def get_performance_config(self) -> PerformanceConfig:
        if self.game_env:
            return self.game_env.performance
        return PerformanceConfig()

    def is_production(self) -> bool:
        if self.game_env:
            return self.game_env.is_production
        return False

    def get_cors_origins(self) -> List[str]:
        return self.app_config.cors_origins

    def get_bot_token(self) -> str:
        if self.game_env:
            return self.game_env.tg_bot_token.get_secret_value()
        return ""

    def get_secret_key(self) -> str:
        if self.game_env:
            return self.game_env.secret_key.get_secret_value()
        return ""


config_manager = ConfigManager()
