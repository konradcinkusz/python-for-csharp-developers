"""yield is yield return, and then it keeps going.

A C# iterator block is one-way: it hands values out, a foreach disposes it
at the end, and a finally inside it runs on that dispose. Python has all
three of those. It also has two things C# has no spelling for at all: a
value sent back IN at the point of the yield, and a return value carried
out of the generator when it stops.

Run it from code/:

    uv run python ch05/generators.py
"""

from collections.abc import Generator

LOG: list[str] = []


# --8<-- [start:yield_return]
def batched(items: list[str], size: int) -> Generator[list[str]]:
    """Exactly an iterator block: lazy, resumable, and disposable.

    The finally runs when the consumer stops early, which is what
    IEnumerator.Dispose does for an iterator block at the end of a foreach.
    """
    batch: list[str] = []
    try:
        for item in items:
            batch.append(item)
            if len(batch) == size:
                yield batch
                batch = []
        if batch:
            yield batch
    finally:
        LOG.append("batched cleaned up")
# --8<-- [end:yield_return]


# --8<-- [start:two_way]
def tally() -> Generator[int, str, str]:
    """Values in as well as out, and a value returned when it stops.

    The three parameters of Generator are what it yields, what may be sent
    into it, and what it returns. C# has a spelling for the first only.
    """
    counts: dict[str, int] = {}
    total = 0
    while True:
        try:
            word = yield total          # the value SENT in lands here
        except GeneratorExit:
            return f"closed after {total}"
        counts[word] = counts.get(word, 0) + 1
        total += 1
# --8<-- [end:two_way]


def main() -> int:
    LOG.clear()
    for batch in batched(["a", "b", "c", "d", "e"], 2):
        print("batch:", batch)
        if len(batch) == 2 and batch[0] == "c":
            break                        # stop early; the finally still runs
    print(LOG[-1])

    counter = tally()
    print("primed at", next(counter))    # runs to the first yield
    print("after 'retry':", counter.send("retry"))
    print("after 'retry':", counter.send("retry"))
    print("returned:", counter.close())  # C# cannot return a value here
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
