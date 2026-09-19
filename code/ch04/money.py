"""A Money type, written both ways, against C#'s record.

The hand-written version is what you would write in C# before records
existed, and it is what @dataclass writes for you. Reading them beside each
other is the fastest way to see which dunder methods a record is, and which
ones it is not: a record gives you value equality, a hash and a printable
form, and it does NOT give you ordering unless you ask.

Run it from code/:

    uv run python ch04/money.py
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from decimal import Decimal


# --8<-- [start:byhand]
class MoneyByHand:
    """Every method below is one @dataclass would have written.

    __slots__ is the part with no C# analogue worth the name. It replaces
    the per-instance __dict__ with a fixed layout, which is closer to what
    a struct costs -- and it also means a typo in an attribute name raises
    AttributeError instead of quietly creating a new field.
    """

    __slots__ = ("amount", "currency")

    def __init__(self, amount: Decimal, currency: str) -> None:
        self.amount = amount
        self.currency = currency

    def __repr__(self) -> str:
        return (
            f"MoneyByHand(amount={self.amount!r}, "
            f"currency={self.currency!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MoneyByHand):
            return NotImplemented
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))
# --8<-- [end:byhand]


# --8<-- [start:dataclass]
@dataclass(frozen=True, slots=True, order=True)
class Money:
    """The same type. frozen is the `record` half; order is not.

    frozen=True is what makes it a value: assignment raises
    FrozenInstanceError, and it is also the flag that lets @dataclass write
    __hash__ at all. order=True writes the four comparison dunders from the
    field order, which a C# record does not give you either -- there you
    implement IComparable by hand, and here you pass a flag.
    """

    amount: Decimal
    currency: str

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError(f"{self.currency} + {other.currency}")
        return dataclasses.replace(self, amount=self.amount + other.amount)
# --8<-- [end:dataclass]


# --8<-- [start:decimal]
def why_decimal() -> tuple[bool, bool, str]:
    """float is IEEE 754 in both languages; only the printing differs.

    C# prints a double to 15 significant digits by default and hides this;
    Python prints the shortest string that round-trips, so the mismatch is
    on screen. Neither language is wrong and neither is more accurate. For
    money the answer in both is the decimal type.
    """
    floats_equal = 0.1 + 0.2 == 0.3
    decimals_equal = Decimal("0.1") + Decimal("0.2") == Decimal("0.3")
    return floats_equal, decimals_equal, repr(0.1 + 0.2)
# --8<-- [end:decimal]


def main() -> int:
    rent = Money(Decimal("1200.00"), "GBP")
    same = Money(Decimal("1200.00"), "GBP")
    print(f"repr           {rent}")
    print(f"value equality {rent == same}")
    print(f"hashable       {len({rent, same})} entry for two equal values")
    print(f"ordering       {rent < Money(Decimal('1300.00'), 'GBP')}")

    # dataclasses.replace is `with` on a C# record: a new object, not a
    # mutation, and it runs __init__ so validation is not skipped.
    raised = dataclasses.replace(rent, amount=Decimal("1250.00"))
    print(f"replace        {raised}")
    print(f"               original still {rent.amount}")

    try:
        rent.amount = Decimal("1")  # type: ignore[misc]
    except dataclasses.FrozenInstanceError as exc:
        print(f"frozen         FrozenInstanceError: {exc}")

    print(f"__add__        {rent + Money(Decimal('50.00'), 'GBP')}")

    floats_equal, decimals_equal, total = why_decimal()
    print()
    print(f"0.1 + 0.2 is   {total}")
    print(f"== 0.3         {floats_equal} as float, "
          f"{decimals_equal} as Decimal")

    by_hand = MoneyByHand(Decimal("1200.00"), "GBP")
    print()
    print(f"by hand        {by_hand}")
    twin = MoneyByHand(Decimal("1200.00"), "GBP")
    print(f"equal          {by_hand == twin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
