"""Reference solution for exercise 3.3."""


def collect(item: str, bucket: list[str] | None = None) -> list[str]:
    """Append item to bucket and return it.

    None is the sentinel and the list is built inside the call, so two
    callers who pass nothing get two lists.
    """
    bucket = [] if bucket is None else bucket
    bucket.append(item)
    return bucket
