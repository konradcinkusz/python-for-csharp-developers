import io

from exercises._loader import load


class Connection:
    """Never mentions the protocol, and satisfies it."""

    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_protocol_matches_by_shape() -> None:
    module = load("ch03", "e03_02_protocol")
    assert isinstance(Connection(), module.Closable)
    assert isinstance(io.StringIO(), module.Closable)
    assert not isinstance("a string has no close", module.Closable)


def test_closes_only_what_is_closable() -> None:
    module = load("ch03", "e03_02_protocol")
    connection = Connection()
    buffer = io.StringIO()
    assert module.close_all([connection, "not closable", buffer, 7]) == 2
    assert connection.closed is True
    assert buffer.closed is True
