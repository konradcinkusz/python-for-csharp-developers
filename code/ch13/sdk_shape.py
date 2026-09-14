"""Read the SDK you installed, rather than the one you remember.

Every claim this chapter makes about an SDK is printed by this listing out
of the package in the lockfile. That is the only source that cannot be
stale: the documentation describes a happy path, a blog post describes a
version, and a model describes whatever it read. `pip show` tells you which
one you have.

The three things the chapter says an SDK is -- a pydantic model, an httpx
client and a streaming iterator -- are each checked here rather than
asserted on the page.

    cd code && uv run python ch13/sdk_shape.py
"""

from __future__ import annotations

from importlib.metadata import requires, version

import pydantic
from anthropic import Anthropic
from anthropic.types import Message
from openai import OpenAI
from openai.types.responses import Response


# --8<-- [start:models]
def base_classes(result: type[object]) -> list[str]:
    """What a response type is built out of, read off the class itself
    rather than off a type hint -- a hint is a claim about the version
    the checker sees, and the question here is about the one installed."""
    return [c.__name__ for c in result.__mro__]


def result_types_are_pydantic() -> bool:
    """A response object is a pydantic model. Both SDKs, same answer."""
    return all(
        "BaseModel" in base_classes(result) for result in (Message, Response)
    )


def extra_policy(model: type[pydantic.BaseModel]) -> str:
    """What an SDK model does with a field the provider added today."""
    return str(model.model_config.get("extra", "ignore"))
# --8<-- [end:models]


# --8<-- [start:transport]
def transport_of(client: object) -> str:
    """The package the SDK's HTTP client actually comes from."""
    inner = getattr(client, "_client", None)
    # The class is an httpx Client subclass. WHICH httpx is the question:
    # the distribution named `httpx` and the one named `httpx2` are two
    # packages, and both SDKs depend on the second.
    for base in type(inner).__mro__:
        if base.__name__ == "Client":
            return base.__module__
    return "unknown"
# --8<-- [end:transport]


def httpx_requirement(distribution: str) -> str:
    """What the SDK's own metadata asks for."""
    wanted = [r for r in (requires(distribution) or []) if "httpx" in r]
    return wanted[0] if wanted else "none"


def main() -> int:
    anthropic_client = Anthropic(api_key="not-a-real-key")
    openai_client = OpenAI(api_key="not-a-real-key")

    print(f"pydantic      {pydantic.VERSION}")
    print(f"httpx         {version('httpx')}")
    print(f"httpx2        {version('httpx2')}")
    print()
    print(f"results are pydantic models   {result_types_are_pydantic()}")
    print(f"Message is a              {base_classes(Message)}")
    print(f"unknown fields are            {extra_policy(Message)!r}")
    print()
    for name, client in (
        ("anthropic", anthropic_client),
        ("openai", openai_client),
    ):
        print(f"{name:10} {version(name):8} transport {transport_of(client)}")
        print(f"{'':10} {'':8} requires  {httpx_requirement(name)}")

    # The listing is the check. If a later version changes any of this,
    # this file fails in CI and the chapter is wrong on the same day.
    assert result_types_are_pydantic()
    assert transport_of(openai_client) == transport_of(anthropic_client)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
