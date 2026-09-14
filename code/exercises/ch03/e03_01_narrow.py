"""Exercise 3.1 -- narrow a type so the checker follows you.

test_e03_01_narrow.py fails until `is_str_list` answers correctly AND is
annotated with TypeIs rather than bool. Both halves are yours: the body is
missing and the return annotation below is the wrong one. A predicate that
returns bool tells the checker nothing, so the run-time answer and the
static narrowing are two separate jobs and this exercise wants both.

The parameter is a Sequence rather than a list on purpose. TypeIs requires
the type you narrow TO to be assignable to the type you narrow FROM, and
list is invariant, so `list[object] -> TypeIs[list[str]]` is rejected
where the Sequence pair is accepted. Section 3.2 says why.

An empty sequence counts as a sequence of strings: there is nothing in it
that is not one.
"""

from collections.abc import Sequence


def is_str_list(value: Sequence[object]) -> bool:
    """True when every item is a str."""
    raise NotImplementedError("your turn: replace this line, and the bool")
