"""A function is an object. Everything else in this chapter follows.

A C# engineer already has this idea under two names -- a delegate and
Func<> -- but has it as a *type ceremony*: Func<int, string> and
Func<int, int, string> are different types with different arities, and a
method group converts to one of them. In Python a function is an ordinary
value of an ordinary type, and the only ceremony is the annotation.

Run it from code/:

    uv run python ch05/first_class.py
"""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    """One build job: what ran, how long it took, how it ended."""

    name: str
    seconds: int
    status: str


# --8<-- [start:table]
# In C# this is Dictionary<string, Func<Job, bool>>, and the arity is part
# of the type's name. Here the value type is Callable[[Job], bool] and the
# dictionary is an ordinary dictionary: no delegate declaration, no
# method-group conversion, no Invoke.
Rule = Callable[[Job], bool]

RULES: dict[str, Rule] = {
    "failed": lambda job: job.status == "failed",
    "slow": lambda job: job.seconds > 60,
    "flaky": lambda job: job.status == "failed" and job.seconds < 10,
}


def matching(jobs: list[Job], rule_name: str) -> list[Job]:
    """Look the rule up by name and call it. The lookup returns a value."""
    rule = RULES[rule_name]
    return [job for job in jobs if rule(job)]
# --8<-- [end:table]


JOBS = [
    Job("build", 42, "ok"),
    Job("test", 310, "failed"),
    Job("lint", 4, "failed"),
]


def main() -> int:
    for name in RULES:
        hits = [job.name for job in matching(JOBS, name)]
        print(f"{name}: {hits}")
    # A function has attributes, because it is an object. The checker and
    # the debugger both read these, and so does functools.wraps.
    print("RULES['slow'] is a", type(RULES["slow"]).__name__)
    print("matching.__name__ is", matching.__name__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
