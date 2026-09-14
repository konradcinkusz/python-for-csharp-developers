"""Exercise 9.4 -- configuration that fails at startup, not at first use.

Write the settings model this service would start from. It must:

  * read OPS_-prefixed environment variables;
  * require `database_url`, with no default;
  * take `request_timeout_seconds`, a float, defaulting to 5.0, which must
    be greater than 0;
  * take `workers`, an int, defaulting to 1, which must be at least 1;
  * read nothing that is not prefixed: a bare DATABASE_URL in the
    environment must not reach it;
  * read `api_key` from a file in the directory passed to `build_settings`,
    and hold it as a SecretStr so it cannot be printed by accident.

`build_settings(secrets_dir)` returns the CLASS, not an instance, so the
tests can construct it under different environments.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings


def build_settings(secrets_dir: str) -> type[BaseSettings]:
    """Return the settings CLASS described above."""
    raise NotImplementedError("your turn: replace this line")
