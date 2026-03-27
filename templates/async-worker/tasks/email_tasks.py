from __future__ import annotations

import json
from datetime import datetime, timezone
from importlib import import_module
from typing import Any

app = import_module("app").app
session_scope = import_module("database").session_scope
models = import_module("models")
EmailLog = models.EmailLog
Job = models.Job


def _start_job(task_name: str) -> int:
    with session_scope() as session:
        job = Job(task_name=task_name, status="STARTED")
        session.add(job)
        session.flush()
        return job.id


def _finish_job(job_id: int, status: str, payload: dict[str, Any]) -> None:
    with session_scope() as session:
        job = session.get(Job, job_id)
        if job is None:
            return
        job.status = status
        job.result = json.dumps(payload)
        job.completed_at = datetime.now(timezone.utc)


@app.task(bind=True, max_retries=3, default_retry_delay=2, name="tasks.send_notification")
def send_notification(
    self,
    recipient: str,
    subject: str,
    message: str,
    simulate_transient_error: bool = False,
) -> dict[str, Any]:
    job_id = _start_job("send_notification")

    try:
        if simulate_transient_error and self.request.retries < 1:
            raise RuntimeError("Simulated transient email provider error")

        with session_scope() as session:
            email_log = EmailLog(
                recipient=recipient,
                subject=subject,
                message=message,
                status="SENT",
            )
            session.add(email_log)

        result: dict[str, object] = {
            "recipient": recipient,
            "subject": subject,
            "status": "SENT",
        }
        _finish_job(job_id, "SUCCESS", result)
        return result
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            _finish_job(job_id, "FAILED", {"error": str(exc), "recipient": recipient})
            raise
        raise self.retry(exc=exc)


@app.task(name="tasks.batch_email")
def batch_email(recipients: list[str], subject: str, message: str) -> dict[str, object]:
    job_id = _start_job("batch_email")

    with session_scope() as session:
        for recipient in recipients:
            session.add(
                EmailLog(
                    recipient=recipient,
                    subject=subject,
                    message=message,
                    status="QUEUED",
                )
            )

    result: dict[str, object] = {
        "queued": len(recipients),
        "subject": subject,
    }
    _finish_job(job_id, "SUCCESS", {"queued": len(recipients), "subject": subject})
    return result
