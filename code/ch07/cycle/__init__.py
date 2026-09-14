"""Eight tiny modules, arranged in a cycle, then three ways out of it.

Every module here begins with an underscore, and that is deliberate twice
over. It is the ordinary Python mark for "internal to this package", and it
is also what tells this repository's listing runner not to execute them on
their own: two of them are MEANT to fail, and half a cycle run by itself
proves nothing. ch07/cycles.py imports every one of them, and that file is
run on every build, so they are all exercised.
"""
