"""A default argument is evaluated once, when the function is defined.

Run it from code/:

    uv run python ch03/defaults.py

The annotation is right, the checker is happy, and the function is wrong.
Both pinned checkers pass this file; the linter does not, which is why
the noqa comment below is here -- it is the evidence, not a tidy-up.
"""


def add_tag(tag: str, tags: list[str] = []) -> list[str]:  # noqa: B006
    """Annotated exactly as you would in C#, and shared by every caller."""
    tags.append(tag)
    return tags


def add_tag_fixed(tag: str, tags: list[str] | None = None) -> list[str]:
    """None is the sentinel, and the list is built inside the call."""
    tags = [] if tags is None else tags
    tags.append(tag)
    return tags


def main() -> None:
    print("The default list, called three times:")
    for tag in ("alpha", "beta", "gamma"):
        print("  ", add_tag(tag))

    print("Its default, after those three calls:")
    print("  ", add_tag.__defaults__)

    print("The same three calls, with None as the sentinel:")
    for tag in ("alpha", "beta", "gamma"):
        print("  ", add_tag_fixed(tag))


if __name__ == "__main__":
    main()
