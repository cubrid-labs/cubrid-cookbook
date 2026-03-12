from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Mapping

from sqlalchemy import delete, func, select  # type: ignore[import-not-found]

from app import app  # type: ignore[import-not-found]
from database import session_scope  # type: ignore[import-not-found]
from models import Job, Report, SalesRecord  # type: ignore[import-not-found]


def _start_job(task_name: str) -> int:
    with session_scope() as session:
        job = Job(task_name=task_name, status="STARTED")
        session.add(job)
        session.flush()
        return job.id


def _finish_job(job_id: int, status: str, payload: Mapping[str, object]) -> None:
    with session_scope() as session:
        job = session.get(Job, job_id)
        if job is None:
            return
        job.status = status
        job.result = json.dumps(payload)
        job.completed_at = datetime.now(timezone.utc)


@app.task(name="tasks.aggregate_sales")
def aggregate_sales(
    start_date: str | None = None, end_date: str | None = None
) -> dict[str, object]:
    job_id = _start_job("aggregate_sales")
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    with session_scope() as session:
        stmt = select(func.count(SalesRecord.id), func.coalesce(func.sum(SalesRecord.amount), 0))
        if start_dt is not None:
            stmt = stmt.where(SalesRecord.created_at >= start_dt)
        if end_dt is not None:
            stmt = stmt.where(SalesRecord.created_at <= end_dt)

        total_orders, total_amount = session.execute(stmt).one()
        payload = {
            "start_date": start_date,
            "end_date": end_date,
            "total_orders": int(total_orders or 0),
            "total_amount": float(total_amount or Decimal("0")),
        }

        report = Report(
            report_name="sales-aggregation",
            content=json.dumps(payload),
        )
        session.add(report)

    _finish_job(job_id, "SUCCESS", payload)
    return payload


@app.task(name="tasks.generate_report")
def generate_report(
    aggregation: dict[str, object], report_name: str = "sales-report"
) -> dict[str, object]:
    job_id = _start_job("generate_report")
    report_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "aggregation": aggregation,
    }

    with session_scope() as session:
        report = Report(report_name=report_name, content=json.dumps(report_payload))
        session.add(report)
        session.flush()
        result = {
            "report_id": report.id,
            "report_name": report_name,
        }

    _finish_job(job_id, "SUCCESS", result)
    return result


@app.task(name="tasks.cleanup_old_records")
def cleanup_old_records(days: int = 30) -> dict[str, int]:
    job_id = _start_job("cleanup_old_records")
    threshold = datetime.now(timezone.utc) - timedelta(days=days)

    with session_scope() as session:
        deleted_jobs = session.execute(
            delete(Job).where(Job.completed_at.is_not(None)).where(Job.completed_at < threshold)
        ).rowcount
        deleted_reports = session.execute(
            delete(Report).where(Report.created_at < threshold)
        ).rowcount

    result = {
        "deleted_jobs": int(deleted_jobs or 0),
        "deleted_reports": int(deleted_reports or 0),
    }
    _finish_job(
        job_id,
        "SUCCESS",
        {"deleted_jobs": result["deleted_jobs"], "deleted_reports": result["deleted_reports"]},
    )
    return result
