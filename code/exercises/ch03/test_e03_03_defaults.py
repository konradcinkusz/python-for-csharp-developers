from exercises._loader import load


def test_two_calls_do_not_share_a_default() -> None:
    module = load("ch03", "e03_03_defaults")
    assert module.collect("alpha") == ["alpha"]
    assert module.collect("beta") == ["beta"]


def test_a_bucket_that_is_passed_in_is_still_used() -> None:
    module = load("ch03", "e03_03_defaults")
    mine = ["alpha"]
    assert module.collect("beta", mine) is mine
    assert mine == ["alpha", "beta"]
    # And two later callers who pass nothing are unaffected by that one,
    # and by each other. One call through the default is not enough to
    # show a default that is shared.
    assert module.collect("gamma") == ["gamma"]
    assert module.collect("delta") == ["delta"]
