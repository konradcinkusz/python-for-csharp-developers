"""Reference solution for exercise 3.1."""

from collections.abc import Sequence
from typing import TypeIs


def is_str_list(value: Sequence[object]) -> TypeIs[Sequence[str]]:
    """True when every item is a str."""
    return all(isinstance(item, str) for item in value)
