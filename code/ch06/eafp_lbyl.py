"""The same failure handled both ways, and the race one of them has.

Run it from code/:

    uv run python ch06/eafp_lbyl.py

`lookup_lbyl` asks first and then acts; `lookup_eafp` acts and handles the
failure. Both return the same answers. The third function is the reason the
first shape is not merely slower: between the question and the act, the
dictionary can change.
"""

from __future__ import annotations

from collections.abc import Mapping


# --8<-- [start:lbyl]
def lookup_lbyl(rates: Mapping[str, float], code: str) -> float:
    """Look before you leap: ask, then act. Two lookups on success."""
    if code in rates:
        return rates[code]
    return 0.0
# --8<-- [end:lbyl]


# --8<-- [start:eafp]
def lookup_eafp(rates: Mapping[str, float], code: str) -> float:
    """Easier to ask forgiveness: act, and handle the one failure.

    Raises nothing: a missing code is not an error here, it is a zero.
    """
    try:
        return rates[code]
    except KeyError:
        return 0.0
# --8<-- [end:eafp]


# --8<-- [start:race]
class Shrinking(dict[str, float]):
    """A mapping that drops the key between the question and the answer."""

    def __contains__(self, key: object) -> bool:
        answer = super().__contains__(key)
        self.clear()  # another thread, another request, a cache eviction
        return answer
# --8<-- [end:race]


def main() -> None:
    rates = {"GBP": 1.0, "EUR": 1.17}
    for code in ("GBP", "ZZZ"):
        a, b = lookup_lbyl(rates, code), lookup_eafp(rates, code)
        print(f"{code}: lbyl={a} eafp={b} agree={a == b}")

    hostile = Shrinking(GBP=1.0)
    try:
        lookup_lbyl(hostile, "GBP")
    except KeyError as exc:
        print(f"lbyl on a mapping that changed: KeyError({exc.args[0]!r})")

    hostile = Shrinking(GBP=1.0)
    print(f"eafp on the same mapping: {lookup_eafp(hostile, 'GBP')}")


if __name__ == "__main__":
    main()
