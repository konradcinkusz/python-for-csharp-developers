"""Async tests, and tests that invent their own inputs.

    uv run pytest ch11/test_async_property.py
    uv run python ch11/test_async_property.py
"""

import asyncio

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pricing import DELIVERY_PENCE, FREE_DELIVERY_PENCE, delivery_pence


# --8<-- [start:async]
async def fetch_rate(delay: float = 0.0) -> int:
    """Stands in for the I/O a real test would await."""
    await asyncio.sleep(delay)
    return 20


async def test_an_async_test_is_a_test_with_async_in_front() -> None:
    """No wrapper, no `.Result`, no `GetAwaiter`.

    This works because code/pyproject.toml sets `asyncio_mode = "auto"`.
    Without it pytest-asyncio is in strict mode, and an un-marked async test
    is not failed -- it is SKIPPED, with a warning, which is the async
    equivalent of a green suite that ran nothing.
    """
    assert await fetch_rate() == 20


async def test_gather_inside_a_test_needs_nothing_special() -> None:
    rates = await asyncio.gather(fetch_rate(), fetch_rate(0.001))
    assert rates == [20, 20]
# --8<-- [end:async]


# --8<-- [start:hypothesis]
@given(goods=st.integers(min_value=0, max_value=10_000_000))
def test_delivery_is_never_negative_and_only_ever_two_prices(
    goods: int,
) -> None:
    """FsCheck's bargain: state the property, let the library find the case.

    hypothesis generates, shrinks a failure to its smallest form, and
    remembers it -- so a case found once is replayed on every later run
    rather than depending on the same random draw coming up again.
    """
    charge = delivery_pence(goods)
    assert charge in (0, DELIVERY_PENCE)
    assert (charge == 0) == (goods >= FREE_DELIVERY_PENCE)
# --8<-- [end:hypothesis]


if __name__ == "__main__":
    # The -W filter is an artefact of running this file as a script: importing
    # hypothesis at the top means pytest cannot rewrite its asserts, and says
    # so. Nothing about the tests below changes, so the notice is silenced
    # rather than left to look like a finding.
    raise SystemExit(
        pytest.main(
            [
                __file__,
                "-q",
                "--no-header",
                "-Wignore::pytest.PytestAssertRewriteWarning",
            ]
        )
    )
