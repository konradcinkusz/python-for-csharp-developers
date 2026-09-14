"""One DTO, four ways, and the same JSON handed to each of them.

Run it from code/:

    uv run python ch03/dto_four_ways.py

A record, a DTO and a POCO are one decision in C#. In Python they are four,
they differ in what they cost and in what they check, and only one of the
four looks at the value at all. Note that no line below needed a
`# type: ignore`: the JSON arrives as Any, and Any is accepted everywhere.
"""

import json
from dataclasses import dataclass
from typing import NamedTuple, TypedDict

import pydantic

# The port is a string. A configuration file written by hand, an environment
# variable, a form field: this is what a boundary actually delivers.
RAW = '{"host": "db.internal", "port": "8080"}'


@dataclass(frozen=True, slots=True)
class SettingsData:
    """Closest to a C# record: __init__, __eq__ and __repr__, generated."""

    host: str
    port: int


class SettingsDict(TypedDict):
    """A shape for a dict that already exists. No class, no instances."""

    host: str
    port: int


class SettingsTuple(NamedTuple):
    """A tuple with names. Immutable, indexable, unpackable."""

    host: str
    port: int


class SettingsModel(pydantic.BaseModel):
    """The only one of the four that looks at the value."""

    host: str
    port: int


def show(label: str, port: object) -> None:
    print(f"  {label:<12} port={port!r:<10} type={type(port).__name__}")


def main() -> None:
    payload = json.loads(RAW)

    print("Handed the same JSON, where port is the string '8080':")
    show("dataclass", SettingsData(**payload).port)
    settings: SettingsDict = payload
    show("TypedDict", settings["port"])
    show("NamedTuple", SettingsTuple(**payload).port)
    show("pydantic", SettingsModel.model_validate(payload).port)

    print("What each one is at run time:")
    print("  TypedDict  ->", type(settings).__name__, "-- there is no class")
    print("  NamedTuple ->", SettingsTuple("db", 1) == ("db", 1))

    # The same wrong value, written as a literal instead of arriving as
    # JSON. The checker sees it now, on both of the lines below, and only
    # the ignore comment gets this file past it. Nothing about the error
    # changed; only where the value came from did.
    print("And the one that refuses nonsense:")
    try:
        SettingsModel(host="db", port="eighty")  # type: ignore[arg-type]
    except pydantic.ValidationError as exc:
        print("  pydantic     ", exc.errors()[0]["type"])
    bad = SettingsData(host="db", port="eighty")  # type: ignore[arg-type]
    print("  dataclass    ", repr(bad.port))


if __name__ == "__main__":
    main()
