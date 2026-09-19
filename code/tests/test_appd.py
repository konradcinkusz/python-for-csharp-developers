"""Appendix D's twenty solutions, asserted.

Every solution in the appendix is a listing under code/appd/ that runs as
a script, and every one of them is checked here. A worked answer in a book
that nothing runs is the class of claim this repository exists to refuse.

Each test names the problem it checks, so a failure names the page.
"""

from __future__ import annotations

import pytest

from appd.p01_two_sum import two_sum
from appd.p02_group_anagrams import group_anagrams
from appd.p03_first_unique import first_unique
from appd.p04_merge_intervals import merge_intervals
from appd.p05_balanced import balanced
from appd.p06_dedupe import dedupe
from appd.p07_chunk import chunk
from appd.p08_transpose import transpose
from appd.p09_flatten import flatten
from appd.p10_top_words import top_words
from appd.p11_binary_search import index_of
from appd.p12_running_total import running_total
from appd.p13_rotate import rotate
from appd.p14_common_prefix import longest_common_prefix
from appd.p15_palindrome import is_palindrome
from appd.p16_deep_get import deep_get
from appd.p17_dedupe_by import dedupe_by
from appd.p18_latest_per_key import latest_per_key
from appd.p19_pairwise_diff import pairwise_diff
from appd.p20_partition import partition


def test_d01_two_sum() -> None:
    assert two_sum([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum([3, 3], 6) == (0, 1)
    assert two_sum([1, 2], 99) is None
    assert two_sum([], 0) is None


def test_d02_group_anagrams() -> None:
    assert group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]) == [
        ["ate", "eat", "tea"],
        ["bat"],
        ["nat", "tan"],
    ]
    assert group_anagrams([]) == []


def test_d03_first_unique() -> None:
    assert first_unique("swiss") == "w"
    assert first_unique("aabb") is None
    assert first_unique("") is None


def test_d04_merge_intervals() -> None:
    assert merge_intervals([(1, 3), (2, 6), (8, 10), (15, 18)]) == [
        (1, 6), (8, 10), (15, 18),
    ]
    # Touching, and fully contained, are both merges.
    assert merge_intervals([(1, 4), (4, 5)]) == [(1, 5)]
    assert merge_intervals([(1, 9), (3, 4)]) == [(1, 9)]
    assert merge_intervals([]) == []


def test_d05_balanced() -> None:
    assert balanced("{[()]}")
    assert balanced("")
    assert not balanced("(]")
    assert not balanced("(")
    assert not balanced(")")


def test_d06_dedupe() -> None:
    assert dedupe([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert dedupe([]) == []


def test_d07_chunk() -> None:
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert chunk([], 3) == []
    with pytest.raises(ValueError, match="positive"):
        chunk([1], 0)


def test_d08_transpose() -> None:
    assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    # The strict=True is the point: a ragged matrix raises rather than
    # quietly transposing to the shortest row.
    with pytest.raises(ValueError):
        transpose([[1, 2], [3]])


def test_d09_flatten() -> None:
    assert list(flatten([1, [2, [3, 4]], 5])) == [1, 2, 3, 4, 5]
    assert list(flatten([])) == []
    assert list(flatten([[], [[]]])) == []


def test_d10_top_words() -> None:
    assert top_words("The cat, the dog; the CAT.", 2) == [
        ("the", 3), ("cat", 2),
    ]


def test_d11_binary_search() -> None:
    assert index_of([1, 3, 5, 7], 5) == 2
    assert index_of([1, 3, 5, 7], 1) == 0
    assert index_of([1, 3, 5, 7], 4) == -1
    assert index_of([], 1) == -1


def test_d12_running_total() -> None:
    assert running_total([1, 2, 3, 4]) == [1, 3, 6, 10]
    assert running_total([]) == []


def test_d13_rotate() -> None:
    assert rotate([1, 2, 3, 4, 5], 2) == [3, 4, 5, 1, 2]
    # Over-long and negative rotations both have to mean something.
    assert rotate([1, 2, 3, 4, 5], 7) == [3, 4, 5, 1, 2]
    assert rotate([1, 2, 3, 4, 5], -1) == [5, 1, 2, 3, 4]
    assert rotate([], 3) == []


def test_d14_common_prefix() -> None:
    assert longest_common_prefix(["flower", "flow", "flight"]) == "fl"
    assert longest_common_prefix(["dog", "car"]) == ""
    assert longest_common_prefix(["same", "same"]) == "same"
    assert longest_common_prefix([]) == ""


def test_d15_palindrome() -> None:
    assert is_palindrome("A man, a plan, a canal: Panama")
    assert is_palindrome("")
    assert not is_palindrome("hello")


def test_d16_deep_get() -> None:
    config = {"db": {"primary": {"port": 5432}}}
    assert deep_get(config, "db.primary.port") == 5432
    assert deep_get(config, "db.replica.port", 0) == 0
    # Walking INTO a non-dict must return the default, not raise.
    assert deep_get(config, "db.primary.port.deeper", "x") == "x"


def test_d17_dedupe_by() -> None:
    rows = [{"id": 1, "v": "a"}, {"id": 1, "v": "b"}, {"id": 2, "v": "c"}]
    assert dedupe_by(rows, lambda r: r["id"]) == [
        {"id": 1, "v": "a"}, {"id": 2, "v": "c"},
    ]


def test_d18_latest_per_key() -> None:
    rows = [
        {"user": "ada", "at": 1},
        {"user": "ada", "at": 5},
        {"user": "bob", "at": 2},
    ]
    assert latest_per_key(
        rows, lambda r: str(r["user"]), lambda r: int(r["at"])
    ) == [{"user": "ada", "at": 5}, {"user": "bob", "at": 2}]


def test_d19_pairwise_diff() -> None:
    assert pairwise_diff([10, 13, 12, 20]) == [3, -1, 8]
    assert pairwise_diff([7]) == []
    assert pairwise_diff([]) == []


def test_d20_partition() -> None:
    assert partition([1, 2, 3, 4, 5], lambda n: n % 2 == 0) == (
        [2, 4], [1, 3, 5],
    )
    assert partition([], lambda n: True) == ([], [])
