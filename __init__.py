"""Package marker for AppDaemon apps.

Making the apps directory a package allows `from . import helpers` / `from . import constants`
and helps linters/IDEs resolve imports. Keep runtime imports out of this file.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # type-only imports to help IDEs / mypy / pylint (won't run at runtime)
    # from . import automationlib  # noqa: F401
    # from . import constants     # noqa: F401
    try:
        from . import constants as const
    except Exception:
        print("Failed to import constants")
        # runtime under AppDaemon: apps dir is on sys.path, import absolute
        import constants as const

    try:
        from . import automationlib as _helpers  # type: ignore
    except Exception:
        # runtime under AppDaemon: apps dir is on sys.path, import absolute
        print("Failed to import automationlib")
        import automationlib as _helpers  # type: ignore
