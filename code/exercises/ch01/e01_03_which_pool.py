"""Exercise 1.3 -- which pool, and why the answer moved.

Three kinds of work, two builds, one decision. The rule is the chapter's
and it is short: the lock is held while Python bytecode runs, and dropped
by anything that waits on the operating system or spends its time inside a
C extension. Turn that into a function.

    "python"     pure Python: a loop, a parse, a comprehension
    "io"         a socket, a file, a database round trip
    "extension"  hashing, compressing, an array library's inner loop

`gil_enabled` is a parameter rather than a global read so that the test can
put both builds to you without needing two interpreters installed. Default
it to what the running interpreter says, so a caller who does not care gets
the right answer for the machine they are on.
"""


def pick_pool(workload: str, gil_enabled: bool | None = None) -> str:
    """Return "threads" or "processes" for `workload` on this build.

    Raise ValueError on a workload name that is not one of the three.
    """
    raise NotImplementedError("your turn: replace this line")
