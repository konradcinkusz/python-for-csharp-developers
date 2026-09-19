import pytest

from exercises._loader import load

KEY = "e07_01_import_time_work"


def test_nothing_is_built_at_import_time() -> None:
    module = load("ch07", KEY)
    assert not hasattr(module, "SETTINGS"), (
        "importing this module still builds SETTINGS; move the work into "
        "build_settings() so that an importer pays for nothing"
    )


def test_build_settings_returns_the_defaults() -> None:
    module = load("ch07", KEY)
    assert module.build_settings() == {
        "region": "eu-west-1",
        "retries": "3",
    }


def test_build_settings_reads_the_environment_when_it_runs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load("ch07", KEY)
    monkeypatch.setenv("PYBOOK_REGION", "eu-central-1")
    # The module was imported BEFORE the environment changed. A function
    # sees the change; a module-level dict comprehension never could.
    assert module.build_settings()["region"] == "eu-central-1"
