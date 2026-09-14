"""A package, which is a module that happens to hold other modules.

__init__.py is the package's own body. It runs once, before anything inside
the package, and whatever it binds is what `from shop import x` can find.

This one binds nothing, on purpose. Section 7.2 says why an __init__.py
that does work is a bill every importer of every submodule pays.
"""
