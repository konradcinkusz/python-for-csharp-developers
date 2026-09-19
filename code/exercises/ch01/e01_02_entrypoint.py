"""Exercise 1.2 -- one file that is both a module and a program.

A C# project has one entry point declared in the project file; a Python
file has none, and gets one by asking at run time which of the two things
it is. That question is `__name__`, and the answer is "__main__" only when
this file is the one the interpreter was pointed at.

Finish `main` so that it appends "main" to RAN and returns 0, and then add
the guard at the bottom that calls it when -- and only when -- the file is
run rather than imported. The test imports this module and insists RAN is
still empty, then runs the file as a program and insists it is not.
"""

RAN: list[str] = []


def main() -> int:
    """Record that the program ran, print one line, and return 0."""
    raise NotImplementedError("your turn: replace this line")


# Your guard goes here. It must call main() and hand its return value to
# sys.exit(), so that a shell and a CI job can tell success from failure --
# which means this file also needs to import sys, and deliberately does not
# yet: an import nothing uses is the one thing the linter would object to in
# an otherwise untouched starter.
