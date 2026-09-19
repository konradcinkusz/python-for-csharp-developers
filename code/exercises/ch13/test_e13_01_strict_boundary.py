from exercises._loader import load

GOOD = '{"summary": "disk full", "severity": 2, "needs_human": false}'
STRINGY = '{"summary": "disk full", "severity": "2", "needs_human": false}'
BOOLY = '{"summary": "disk full", "severity": 2, "needs_human": "true"}'
BROKEN = '{"summary": "disk full", "severity": 2}'


def test_a_correct_reply_parses() -> None:
    module = load("ch13", "e13_01_strict_boundary")
    reply = module.parse_reply(GOOD)
    assert reply is not None
    assert reply.severity == 2
    assert reply.needs_human is False


def test_a_stringy_integer_is_refused_rather_than_coerced() -> None:
    module = load("ch13", "e13_01_strict_boundary")
    assert module.parse_reply(STRINGY) is None


def test_a_stringy_boolean_is_refused_too() -> None:
    module = load("ch13", "e13_01_strict_boundary")
    assert module.parse_reply(BOOLY) is None


def test_a_missing_field_is_still_refused() -> None:
    module = load("ch13", "e13_01_strict_boundary")
    assert module.parse_reply(BROKEN) is None
