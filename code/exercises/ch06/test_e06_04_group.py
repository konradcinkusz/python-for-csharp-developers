import pytest

from exercises._loader import load


def bad_name(record: dict[str, str]) -> None:
    if not record.get("name"):
        raise ValueError("name is empty")


def bad_port(record: dict[str, str]) -> None:
    if "port" not in record:
        raise KeyError("port")


def always_fine(_record: dict[str, str]) -> None:
    return None


def test_silence_when_everything_passes() -> None:
    module = load("ch06", "e06_04_group")
    assert module.check_all({"name": "web", "port": "80"},
                            [bad_name, bad_port, always_fine]) is None


def test_every_failure_is_reported_not_only_the_first() -> None:
    module = load("ch06", "e06_04_group")
    with pytest.raises(ExceptionGroup) as caught:
        module.check_all({}, [bad_name, bad_port])
    kinds = [type(e).__name__ for e in caught.value.exceptions]
    assert kinds == ["ValueError", "KeyError"]


def test_the_group_can_be_split_by_type() -> None:
    module = load("ch06", "e06_04_group")
    seen: list[str] = []
    try:
        module.check_all({}, [bad_name, bad_port, always_fine])
    except* ValueError as group:
        seen += [f"value:{len(group.exceptions)}"]
    except* KeyError as group:
        seen += [f"key:{len(group.exceptions)}"]
    assert seen == ["value:1", "key:1"]
