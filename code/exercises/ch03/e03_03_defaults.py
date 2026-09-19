"""Exercise 3.3 -- a default argument that is not what it looks like.

This one starts wrong. `collect` is annotated exactly as a C# engineer
would annotate it, the checker is happy with it, and
test_e03_03_defaults.py fails on the second call.

Fix it so that two calls that pass no bucket do not share one. The noqa
comment is there because the linter is right; when you have fixed the
function you should be able to delete it, and the test will tell you
whether you have.
"""


def collect(item: str, bucket: list[str] = []) -> list[str]:  # noqa: B006
    """Append item to bucket and return it."""
    bucket.append(item)
    return bucket
