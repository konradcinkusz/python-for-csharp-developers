"""Four lines that are not wrong, and that stop working under one name.

    cd code && uv run python ch07/shadow/innocent.py

ch07/shadowing.py copies this file into a scratch directory AS random.py
and runs it there. Nothing in it changes. It fails anyway.
"""

import random

VALUE = random.random()
print(f"a number between 0 and 1: {VALUE < 1}")
