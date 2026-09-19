"""Build the distribution, and read what came out of it.

Run it from code/:   uv run python ch14/publish.py

`uv build` is one command and it is not the interesting part. What is
interesting is what the wheel turns out to contain and what its metadata
turns out to say, because that -- and not the code -- is what PyPI
publishes and what a user installs.

So this builds into a temporary directory and then opens the wheel it
produced, which is a zip file with a text metadata member, and prints both.
Nothing here is typed from memory: every line below is read back out of an
artefact this script has made.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import zipfile
from email.message import Message
from email.parser import BytesParser
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]


# --8<-- [start:build]
def build(into: Path) -> Path:
    """Run `uv build` and return the wheel it wrote.

    `--offline` because a build that reaches the network is a build that
    can fail on somebody else's morning; the backend is bundled with uv.
    """
    subprocess.run(
        ["uv", "build", "--offline", "--out-dir", str(into)],
        cwd=CODE,
        check=True,
        capture_output=True,
    )
    wheels = sorted(into.glob("*.whl"))
    if len(wheels) != 1:
        raise SystemExit(f"expected one wheel, got {[w.name for w in wheels]}")
    return wheels[0]


def metadata(wheel: Path) -> Message:
    """A wheel is a zip, and its METADATA member is an email header block.

    Parsed rather than split on colons, and returned as the Message rather
    than as a dict, because `Requires-Dist` appears once per dependency
    and a dict keeps the last one. A dict here would have reported this
    package as needing one package when it declares twelve.
    """
    with zipfile.ZipFile(wheel) as zf:
        name = next(
            n for n in zf.namelist() if n.endswith(".dist-info/METADATA")
        )
        with zf.open(name) as handle:
            return BytesParser().parse(handle)
# --8<-- [end:build]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        wheel = build(Path(tmp))
        fields = metadata(wheel)
        with zipfile.ZipFile(wheel) as zf:
            modules = sorted(
                n for n in zf.namelist() if n.endswith(".py")
            )
        print(f"built   {wheel.name.rsplit('-py3', 1)[0]}")
        print(f"name    {fields.get('Name')}")
        print(f"python  {fields.get('Requires-Python')}")
        print(f"needs   {len(fields.get_all('Requires-Dist') or [])} packages")
        print(f"modules {len(modules)}")
        for module in modules:
            print(f"        {module}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
