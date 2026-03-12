from __future__ import annotations

import os
from collections.abc import Callable
from importlib import import_module
from typing import cast

_ = os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cubrid_project.settings")

get_wsgi_application = cast(
    Callable[[], object],
    import_module(".".join(["django", "core", "wsgi"])).get_wsgi_application,
)

application = get_wsgi_application()
