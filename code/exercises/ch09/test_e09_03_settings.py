import os
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

import pytest
from pydantic import ValidationError

from exercises._loader import load


@pytest.fixture
def settings_class(tmp_path: Path) -> Iterator[type]:
    # The secret's FILE NAME carries the env prefix, and the match is
    # case-insensitive.
    (tmp_path / "ops_api_key").write_text("s3cret", encoding="utf8")
    module: ModuleType = load("ch09", "e09_03_settings")
    kept = dict(os.environ)
    os.environ["OPS_DATABASE_URL"] = "postgresql://localhost/ops"
    try:
        yield module.build_settings(str(tmp_path))
    finally:
        os.environ.clear()
        os.environ.update(kept)


def test_reads_the_environment_and_the_defaults(settings_class: type) -> None:
    settings = settings_class()
    assert settings.database_url == "postgresql://localhost/ops"
    assert settings.request_timeout_seconds == 5.0
    assert settings.workers == 1


def test_reads_the_secret_from_a_file(settings_class: type) -> None:
    assert settings_class().api_key.get_secret_value() == "s3cret"


def test_the_secret_is_not_in_the_repr(settings_class: type) -> None:
    assert "s3cret" not in repr(settings_class())


def test_a_required_setting_is_missing(settings_class: type) -> None:
    del os.environ["OPS_DATABASE_URL"]
    with pytest.raises(ValidationError) as caught:
        settings_class()
    assert caught.value.errors()[0]["loc"] == ("database_url",)


def test_an_out_of_range_value_is_refused(settings_class: type) -> None:
    os.environ["OPS_REQUEST_TIMEOUT_SECONDS"] = "0"
    with pytest.raises(ValidationError):
        settings_class()


def test_an_unprefixed_variable_is_not_read(settings_class: type) -> None:
    # The prefix is isolation, not decoration: a bare DATABASE_URL set by
    # something else on the machine must not reach this service.
    del os.environ["OPS_DATABASE_URL"]
    os.environ["DATABASE_URL"] = "postgresql://elsewhere/other"
    with pytest.raises(ValidationError):
        settings_class()
