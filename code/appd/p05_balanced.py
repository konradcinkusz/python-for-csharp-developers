"""D.5 -- balanced brackets: a list is the stack.

There is no Stack<T> to import. A list does push with append and pop with
pop, and the whole check is the four lines below. `not stack` at the end
is the truthiness rule doing the Count == 0.

Run it from code/:

    uv run python appd/p05_balanced.py
"""

from __future__ import annotations

# --8<-- [start:solution]
CLOSERS = {")": "(", "]": "[", "}": "{"}


def balanced(text: str) -> bool:
    """Are the brackets in text correctly nested and closed?"""
    stack: list[str] = []
    for char in text:
        if char in CLOSERS.values():
            stack.append(char)
        elif char in CLOSERS and (
            not stack or stack.pop() != CLOSERS[char]
        ):
            return False
    return not stack
# --8<-- [end:solution]


def main() -> int:
    for text in ("{[()]}", "(]", "("):
        print(f"{text:8} {balanced(text)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
