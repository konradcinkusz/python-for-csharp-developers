"""Exercise 1.1 -- read the bytecode the compiler produced.

C# has ildasm; Python has `dis`, and it is in the standard library rather
than in a separate SDK. The test beside this file disassembles two
functions and checks what came back, so the answer has to be computed from
the function object rather than typed out.

Nothing here needs the function to be CALLED. The bytecode exists the
moment the module is compiled, which is the whole point of the exercise.
"""

from collections.abc import Callable
from typing import Any


def instruction_names(func: Callable[..., Any]) -> list[str]:
    """Return the opcode names of `func`, in the order they will execute.

    For a function whose body is `return 7` on the pinned interpreter the
    answer is three names long and starts with RESUME.
    """
    raise NotImplementedError("your turn: replace this line")
