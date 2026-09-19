"""Configuration: pydantic-settings where IOptions<T> used to be.

There is no provider chain and no appsettings.json. There is a model, it is
validated at startup rather than at first read, and its sources are the
environment, a .env file and a directory of secret files -- which is how a
container hands a password to a process without putting it in the
environment.

    uv run python ch09/settings.py
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


def build_settings_class(secrets: Path) -> type[BaseSettings]:
    # --8<-- [start:settings]
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_prefix="OPS_",         # OPS_DATABASE_URL -> database_url
            env_file=".env",           # read if present, ignored if not
            secrets_dir=str(secrets),  # one file per setting, for
                                       # containers
            extra="forbid",            # rejects an unknown key in .env or
        )                              # in __init__ -- but NOT an unknown
                                       # OPS_* in the environment, which
                                       # every source here simply does not
                                       # look at. Measured, not assumed.

        database_url: str                       # no default: required
        api_key: SecretStr                      # never in a repr or a log
        request_timeout_seconds: float = Field(default=5.0, gt=0)
        workers: int = Field(default=1, ge=1)
    # --8<-- [end:settings]

    return Settings


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        secrets = Path(directory)
        # The FILE NAME carries the env prefix, and matching is
        # case-insensitive: "api_key" alone is not found, "ops_api_key"
        # and "OPS_API_KEY" both are. Measured, because it is the kind of
        # thing that costs an afternoon in a container that starts and
        # then says a required setting is missing.
        (secrets / "ops_api_key").write_text("s3cret", encoding="utf8")
        settings_class = build_settings_class(secrets)

        os.environ["OPS_DATABASE_URL"] = "postgresql://localhost/ops"
        os.environ["OPS_REQUEST_TIMEOUT_SECONDS"] = "2.5"
        settings = settings_class()
        for name, value in settings.model_dump().items():
            print(f"  {name:24} {value!r}")

        os.environ["OPS_REQUEST_TIMEOUT_SECONDS"] = "-1"
        try:
            settings_class()
        except ValidationError as exc:
            error = exc.errors()[0]
            print("bad value       :", error["loc"][0], "--", error["msg"])

        del os.environ["OPS_DATABASE_URL"]
        del os.environ["OPS_REQUEST_TIMEOUT_SECONDS"]
        try:
            settings_class()
        except ValidationError as exc:
            error = exc.errors()[0]
            print("missing required:", error["loc"][0], "--", error["msg"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
