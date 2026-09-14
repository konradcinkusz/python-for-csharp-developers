"""Reference solution for exercise 3.4.

pydantic is what the chapter points at, and one model replaces the whole
hand-written version: it reads the JSON, refuses what it cannot convert,
and hands back something whose types the rest of the program can trust.
"""

from dataclasses import dataclass

import pydantic


@dataclass(frozen=True, slots=True)
class Settings:
    host: str
    port: int


class _SettingsModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="ignore")

    host: str
    port: int


def parse_settings(blob: str) -> Settings:
    """Parse JSON into Settings, or raise ValueError.

    ValidationError is a ValueError, so the boundary raises one kind of
    thing whichever way this is written.
    """
    validated = _SettingsModel.model_validate_json(blob)
    return Settings(host=validated.host, port=validated.port)
