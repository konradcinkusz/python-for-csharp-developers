import subprocess
import sys

from exercises._loader import load


def test_the_module_does_nothing_until_main_is_called() -> None:
    # The import half of this assertion passes on the untouched starter --
    # which is why it is not a test of its own. Under PYBOOK_STARTERS=fail
    # every test here must fail until the reader finishes the file, so a
    # test that only checks a precondition would be reported as an
    # unexpected pass and would fail the build.
    module = load("ch01", "e01_02_entrypoint")
    assert module.RAN == [], (
        "importing a module must not run its program; that is the whole "
        "job of the __name__ guard"
    )
    assert module.main() == 0
    assert module.RAN == ["main"]


def test_running_the_file_as_a_program_does_run_it() -> None:
    module = load("ch01", "e01_02_entrypoint")
    # A module's __file__ is str | None, and None is a real possibility for
    # a module with no file behind it. This one has one.
    path = module.__file__
    assert isinstance(path, str)
    result = subprocess.run(
        [sys.executable, path],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ran as a program"
