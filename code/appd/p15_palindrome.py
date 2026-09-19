"""D.15 -- is it a palindrome, ignoring punctuation and case?

`cleaned[::-1]` is the reversal and it is a slice, not a method: there is
no list.reverse() that returns. casefold rather than lower is the detail
an interviewer may or may not want -- it is the one that handles the
German sharp s, where lower does not.

Run it from code/:

    uv run python appd/p15_palindrome.py
"""

from __future__ import annotations


# --8<-- [start:solution]
def is_palindrome(text: str) -> bool:
    """Ignoring case and anything that is not a letter or digit."""
    cleaned = [c.casefold() for c in text if c.isalnum()]
    return cleaned == cleaned[::-1]
# --8<-- [end:solution]


def main() -> int:
    print(is_palindrome("A man, a plan, a canal: Panama"))
    print(is_palindrome("hello"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
