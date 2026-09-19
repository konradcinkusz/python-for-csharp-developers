"""Reference solution for exercise 1.1."""

import dis
from collections.abc import Callable
from typing import Any


def instruction_names(func: Callable[..., Any]) -> list[str]:
    """Return the opcode names of `func`, in the order they will execute."""
    return [instruction.opname for instruction in dis.get_instructions(func)]
