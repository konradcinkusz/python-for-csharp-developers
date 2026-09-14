"""A type hint is a claim. Nothing at run time checks it.

Run it from code/:

    uv run python ch03/hint_is_a_claim.py

Every call below violates the annotation above it, and the interpreter has
no opinion about any of them. Nothing raises, nothing is logged, and two of
the three results are quietly the wrong type.

The one line that needed help is the `# type: ignore` on the first call:
that comment is not for Python, which never looks at it, but for the
checker, which would otherwise have refused to print this file. Chapter 3
section 5 comes back to what else that comment can hide.
"""


def shout(word: str) -> str:
    """Annotated str in, str out. Neither half is enforced."""
    return f"{word}!"


def port_of(config: dict[str, str]) -> int:
    """Annotated to return an int. Read what it actually returns."""
    return config["port"]  # type: ignore[return-value]


def main() -> None:
    # A parameter annotated str, handed an int.
    print("shout(7)      ->", repr(shout(7)))  # type: ignore[arg-type]

    # A function annotated -> int, returning a str.
    port = port_of({"port": "8080"})
    print("port_of(...)  ->", repr(port), "which is a", type(port).__name__)

    # The annotations are ordinary data. You can read them, and you can
    # replace them with something false, and nothing anywhere notices.
    print("annotations   ->", shout.__annotations__)
    shout.__annotations__["word"] = "anything at all"
    print("after editing ->", shout.__annotations__)


if __name__ == "__main__":
    main()
