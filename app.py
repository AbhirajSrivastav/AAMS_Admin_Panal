"""Compatibility shim for imports.

`run.py` imports `create_app` via:

    from app import create_app

But this project’s real package directory is named `APP/`.
This module re-exports `APP.create_app`.

Keeping this as a top-level `app.py` avoids any package-resolution edge cases.
"""

# Make `app` behave like a package so imports like `app.services.*` work.
# This is required because modules inside `APP/` use absolute imports under
# the name `app`.
import os as _os

_pkg_root = _os.path.join(_os.path.dirname(__file__), 'APP')

# Create a synthetic package for `app` that points at `APP/`
# (must be set before importing APP modules that use `app.*` imports)
__path__ = [_pkg_root]  # type: ignore

# Expose the real Flask app factory
from APP import create_app  # type: ignore  # noqa: F401



