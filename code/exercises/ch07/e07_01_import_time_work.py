"""Exercise 7.1 -- move the work out of import time.

This module reads the environment and builds a settings dictionary. It does
it at import time, so every importer pays for it, the value depends on when
the first import happened, and a test cannot change the environment and see
a different answer.

Make it lazy: delete the module-level SETTINGS and give the module a
build_settings() function that does the same work when it is called. The
test checks both halves -- that nothing is built at import, and that the
function returns what the environment says at the moment it runs.
"""

import os

DEFAULTS = {"region": "eu-west-1", "retries": "3"}

# Module level: this runs on the first import and never again.
SETTINGS = {
    key: os.environ.get(f"PYBOOK_{key.upper()}", default)
    for key, default in DEFAULTS.items()
}
