"""D.2 -- group anagrams: a sorted string is the key.

defaultdict(list) is what a Dictionary<string, List<string>> plus a
TryGetValue-or-add is in C#. The subtlety is in the last line rather than
the grouping: sort each group BEFORE sorting the groups, or the outer sort
orders them by whatever happened to arrive first.

Run it from code/:

    uv run python appd/p02_group_anagrams.py
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable


# --8<-- [start:solution]
def group_anagrams(words: Iterable[str]) -> list[list[str]]:
    """Anagrams grouped together, each group sorted, groups sorted."""
    groups: defaultdict[str, list[str]] = defaultdict(list)
    for word in words:
        groups["".join(sorted(word))].append(word)
    # Normalise each group first: sorting the groups before their contents
    # are ordered sorts them by insertion order, which is not an order.
    return sorted(sorted(group) for group in groups.values())
# --8<-- [end:solution]


def main() -> int:
    print(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
