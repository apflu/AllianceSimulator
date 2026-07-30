from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ASIM_",
        extra="ignore",
        case_sensitive=False,
        env_ignore_empty=True,
    )

    environment: Literal["development", "test", "production"] = "development"
    database_url: str = "postgresql+asyncpg://alliancesim:alliancesim@127.0.0.1:5432/alliancesim"
    log_level: str = "INFO"
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)
    worker_poll_interval_seconds: float = Field(default=1.0, gt=0, le=60)
    discord_token: SecretStr | None = None
    discord_guild_id: int | None = None
    telegram_token: SecretStr | None = None
    proxy_url: SecretStr | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
