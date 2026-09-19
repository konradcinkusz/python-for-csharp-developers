"""D.10 -- the n most common words.

Counter.most_common is GroupBy plus OrderByDescending plus Take, written
once in the standard library. The regex is doing the tokenising that
string.Split cannot: it keeps apostrophes and drops punctuation.

Run it from code/:

    uv run python appd/p10_top_words.py
"""

from __future__ import annotations

import re
from collections import Counter

WORD = re.compile(r"[a-z']+")


# --8<-- [start:solution]
def top_words(text: str, n: int) -> list[tuple[str, int]]:
    """The n most common words, commonest first."""
    return Counter(WORD.findall(text.lower())).most_common(n)
# --8<-- [end:solution]


def main() -> int:
    print(top_words("The cat, the dog; the CAT.", 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
