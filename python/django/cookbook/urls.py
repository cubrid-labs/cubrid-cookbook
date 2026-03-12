from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import cast

from .views import add_employee, dashboard, raw_sql_examples

path = cast(Callable[..., object], import_module(".".join(["django", "urls"])).path)

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("employees/add/", add_employee, name="add_employee"),
    path("raw-sql/", raw_sql_examples, name="raw_sql_examples"),
]
