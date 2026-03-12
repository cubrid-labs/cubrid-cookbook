from __future__ import annotations

import os
import sys
from collections.abc import Callable
from importlib import import_module
from typing import cast


def main() -> None:
    _ = os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cubrid_project.settings")
    try:
        management_module = import_module(".".join(["django", "core", "management"]))
        execute_from_command_line = cast(
            Callable[[list[str]], object],
            management_module.execute_from_command_line,
        )
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available on your "
            + "PYTHONPATH environment variable?"
        ) from exc
    _ = execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
