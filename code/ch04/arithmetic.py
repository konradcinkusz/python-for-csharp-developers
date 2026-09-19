"""Two operators that read the same in both languages and are not the same.

`/` on two ints is integer division in C# and true division in Python, and
`//` is not C#'s `/` either: it floors, and it floors towards negative
infinity where C# truncates towards zero. So the two languages disagree
about -7 divided by 2 in a way no cast fixes, and the disagreement is
silent -- both produce a number, and only one of them is the number the
other language would have produced.

Run it from code/:

    uv run python ch04/arithmetic.py
"""

from __future__ import annotations

import math


# --8<-- [start:division]
def divisions(a: int, b: int) -> tuple[float, int, float, int]:
    """The four answers Python gives, where C# gives two.

    C#'s `a / b` on two ints is Python's `int(a / b)` -- truncation -- and
    is NOT Python's `a // b` whenever the result is negative. math.fmod
    keeps the sign of the dividend, the way C#'s % does; Python's own %
    keeps the sign of the divisor, which is the same choice as //.
    """
    return a / b, a // b, math.fmod(a, b), a % b
# --8<-- [end:division]


# --8<-- [start:close]
def compare_floats(x: float, y: float) -> tuple[bool, bool]:
    """== is exact and is almost never what you meant for a computed float.

    math.isclose is the standard library's answer and takes both a
    relative and an absolute tolerance. The absolute one matters near
    zero, where a relative tolerance has nothing to be relative to.
    """
    return x == y, math.isclose(x, y, rel_tol=1e-9)
# --8<-- [end:close]


def main() -> int:
    head = f"{'a, b':>8}  {'a / b':>8}  {'a // b':>7}"
    print(f"{head}  {'fmod':>6}  {'a % b':>6}")
    for a, b in ((7, 2), (-7, 2), (7, -2)):
        true_div, floor_div, fmod, mod = divisions(a, b)
        print(f"{a:4},{b:3}  {true_div:8}  {floor_div:7}  {fmod:6}  {mod:6}")

    print()
    print("C# would give -3 for -7 / 2; Python's // gives -4, because it")
    print("floors rather than truncating. int(-7 / 2) is the C# answer.")
    print(f"int(-7 / 2)  {int(-7 / 2)}     -7 // 2  {-7 // 2}")

    exact, close = compare_floats(0.1 + 0.2, 0.3)
    print()
    print(f"0.1 + 0.2 == 0.3          {exact}")
    print(f"math.isclose(...)         {close}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
