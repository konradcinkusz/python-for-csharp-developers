"""Exercise 11.3: the patch has to reach the call, not just run.

One test, and it is the whole exercise. An earlier draft added a
second one asserting that monkeypatch had undone the substitution
afterwards -- true, worth knowing, and independent of anything the
reader writes, so it passed on the untouched starter and `make
starters` failed it as an unexpected pass. A test in an exercise
that does not depend on the reader's answer is not a check.
"""

import pytest
from invoice import gross_bound

from exercises._loader import load


def test_the_patch_reaches_the_call(monkeypatch: pytest.MonkeyPatch) -> None:
    target = load("ch11", "e11_03_patch_target").PATCH_TARGET
    monkeypatch.setattr(target, lambda: 0)
    assert gross_bound(1000) == 1000, (
        f"patching {target!r} left the real rate in place: gross_bound "
        f"returned {gross_bound(1000)} on a net of 1000, so the rate it "
        f"read was not the one you replaced"
    )

