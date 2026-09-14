"""What am I actually running? Five questions, answered by the interpreter.

    cd code && uv run python ch01/interpreter.py

Nothing here is written down: every line is read out of the running process.
That matters more in this chapter than anywhere else in the book, because
every claim it makes -- there is a compile step, there is a lock, the
free-threaded build is a different binary -- is a claim about the machine in
front of you, and the machine will answer it.

Run the same file under the free-threaded interpreter and three of the five
answers change:

    python3.14t ch01/interpreter.py
"""

import sys
import sysconfig


# --8<-- [start:facts]
def facts() -> list[tuple[str, str]]:
    """The five questions, each answered by the interpreter itself."""
    version = ".".join(str(part) for part in sys.version_info[:3])

    # sys._is_gil_enabled() has existed since 3.13 and is the only answer
    # here that is about the running PROCESS rather than about the build.
    # Private by name only: the documentation names it as the probe.
    gil = sys._is_gil_enabled()  # pyright: ignore[reportPrivateUsage]

    # Py_GIL_DISABLED is a BUILD variable: 1 on the free-threaded binary and
    # 0 on the default one. It answers "which python is this", where the
    # call above answers "is the lock on right now" -- and the two really
    # can disagree: run the free-threaded binary with PYTHON_GIL=1, or
    # -X gil=1, and the build says 1 while the lock says True.
    build = sysconfig.get_config_var("Py_GIL_DISABLED") == 1

    # The 3.14 JIT. Available means the binary was compiled with it;
    # enabled means this process is using it. The gap between the two is
    # the whole answer to "does Python have a JIT like the CLR's".
    jit = sys._jit  # pyright: ignore[reportPrivateUsage]
    jit_state = f"{jit.is_available()} / {jit.is_enabled()}"

    return [
        ("interpreter", f"{sys.implementation.name} {version}"),
        ("free-threaded build", str(build)),
        ("GIL enabled right now", str(gil)),
        ("JIT available / enabled", jit_state),
        # sys.abiflags carries "t" on the free-threaded build, which is
        # where the binary's name comes from. The cache tag does NOT: both
        # builds write and read the same .pyc files, because they run the
        # same bytecode and differ only in the runtime under it.
        ("ABI flags", repr(sys.abiflags)),
        ("bytecode cache tag", sys.implementation.cache_tag),
    ]
# --8<-- [end:facts]


def main() -> int:
    for label, answer in facts():
        print(f"{label:24} {answer}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
