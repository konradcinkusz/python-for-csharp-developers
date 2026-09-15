"""Substituting a dependency, and the one trap that makes a test lie.

Every assertion in this file passes. That is deliberate: the trap is not
described here, it is PROVED here, including the half that does nothing --
`test_patching_the_definition_changes_nothing` asserts that the wrong patch
leaves the real rate in place, so the book's own build fails the day that
stops being true.

    uv run pytest ch11/test_patching.py
    uv run python ch11/test_patching.py
"""

from unittest.mock import Mock, patch

import invoice
import pytest
import rates


# --8<-- [start:wrong]
def test_patching_the_definition_changes_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`invoice` did `from rates import vat_rate_percent` at import time.

    That bound the FUNCTION into invoice's namespace. Rebinding the name on
    `rates` afterwards cannot reach it, and nothing anywhere reports that.
    """
    monkeypatch.setattr("rates.vat_rate_percent", lambda: 0)
    assert invoice.gross_bound(1000) == 1200  # the REAL 20%, still
# --8<-- [end:wrong]


# --8<-- [start:right]
def test_patching_where_the_name_is_looked_up_works(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Patch the name the calling code reads: `invoice.vat_rate_percent`."""
    monkeypatch.setattr("invoice.vat_rate_percent", lambda: 0)
    assert invoice.gross_bound(1000) == 1000
# --8<-- [end:right]


# --8<-- [start:qualified]
def test_a_qualified_call_is_patched_at_the_definition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """And the same wrong target is the RIGHT one for the other spelling.

    `gross_qualified` kept the module and looks the attribute up when it
    calls, so patching `rates.vat_rate_percent` does reach it. The rule is
    not "always patch the importer": it is "patch the name the calling code
    resolves, and which name that is was decided by the import".
    """
    monkeypatch.setattr("rates.vat_rate_percent", lambda: 0)
    assert invoice.gross_qualified(1000) == 1000
    assert rates.vat_rate_percent() == 0
# --8<-- [end:qualified]


# --8<-- [start:mock]
def test_a_mock_records_the_call_as_moq_would() -> None:
    """`unittest.mock` is Moq without the lambda tree.

    `patch` as a context manager is the scope; `assert_called_once_with` is
    `Verify`. There is no `Setup(...).Returns(...)` because there is no type
    to satisfy -- a Mock answers to any attribute, which is why the
    `assert_called` family exists and why a typo in it once passed silently.
    """
    with patch("invoice.vat_rate_percent") as rate:
        rate.return_value = 5
        assert invoice.gross_bound(1000) == 1050
    rate.assert_called_once_with()
# --8<-- [end:mock]


# --8<-- [start:autospec]
def test_autospec_refuses_a_call_the_real_function_would_refuse() -> None:
    """A bare Mock accepts anything, including a call that cannot compile.

    `create_autospec` takes the real signature, so the double is wrong in
    the same ways the original would be. This is the closest thing Python
    has to a strict Moq mock, and it is opt-in.
    """
    loose = Mock()
    loose(1, 2, 3)  # a bare Mock is happy with arguments nothing accepts

    with (
        patch("invoice.vat_rate_percent", autospec=True) as rate,
        pytest.raises(TypeError),
    ):
        rate("unexpected argument")
# --8<-- [end:autospec]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *("-q", "--no-header")]))
