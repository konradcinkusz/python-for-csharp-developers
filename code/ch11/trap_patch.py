"""The wrong patch target, kept as a file so the failure is a real one.

This is the test a reader writes first. It patches the place the function is
DEFINED, and it fails, and the report the chapter prints is this file's own
output. Nothing collects it -- the name does not begin with `test_`, so the
suite never picks it up -- and pytest runs it anyway when you name it:

    uv run pytest ch11/trap_patch.py

The passing version of the same lesson is ch11/test_patching.py, where the
trap is asserted rather than merely suffered.
"""

from unittest.mock import patch

from invoice import gross_bound


def test_a_zero_rate_leaves_the_net_alone() -> None:
    # Wrong target: invoice bound the function at import, so rebinding it
    # on `rates` afterwards cannot reach the call below.
    with patch("rates.vat_rate_percent", return_value=0):
        assert gross_bound(1000) == 1000
