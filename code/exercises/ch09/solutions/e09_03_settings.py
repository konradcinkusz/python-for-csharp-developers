"""Reference solution for exercise 9.4."""

from __future__ import annotations

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def build_settings(secrets_dir: str) -> type[BaseSettings]:
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_prefix="OPS_",
            env_file=".env",
            secrets_dir=secrets_dir,
            extra="forbid",
        )

        database_url: str
        api_key: SecretStr
        request_timeout_seconds: float = Field(default=5.0, gt=0)
        workers: int = Field(default=1, ge=1)

    return Settings
