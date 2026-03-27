from __future__ import annotations

import celery  # pyright: ignore[reportMissingImports]

BROKER_URL = "redis://localhost:6379/0"
DATABASE_URL = "cubrid+pycubrid://dba@localhost:33000/testdb"

app = getattr(celery, "Celery")(
    "cubrid_cookbook_celery",
    broker=BROKER_URL,
    backend=f"db+{DATABASE_URL}",
    include=["tasks.data_tasks", "tasks.email_tasks"],
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)
