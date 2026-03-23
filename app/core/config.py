from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Analytics PRO API"
    env: str = "dev"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/analytics_pro"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120

    rate_limit: str = "120/minute"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
