from __future__ import annotations

import argparse
from decimal import Decimal

from celery import chain  # type: ignore[import-not-found]
from sqlalchemy import func, select  # type: ignore[import-not-found]

from database import init_db, session_scope  # type: ignore[import-not-found]
from models import Job, SalesRecord  # type: ignore[import-not-found]
from tasks.data_tasks import (  # type: ignore[import-not-found]
    aggregate_sales,
    cleanup_old_records,
    generate_report,
)
from tasks.email_tasks import batch_email, send_notification  # type: ignore[import-not-found]


def seed_sales_data() -> None:
    with session_scope() as session:
        count_stmt = select(func.count(SalesRecord.id))
        record_count = session.execute(count_stmt).scalar_one()
        if record_count > 0:
            return

        session.add_all(
            [
                SalesRecord(product_name="laptop", quantity=2, amount=Decimal("1800.00")),
                SalesRecord(product_name="monitor", quantity=4, amount=Decimal("900.00")),
                SalesRecord(product_name="keyboard", quantity=10, amount=Decimal("650.00")),
            ]
        )


def print_recent_jobs(limit: int = 10) -> None:
    with session_scope() as session:
        stmt = select(Job).order_by(Job.id.desc()).limit(limit)
        jobs = session.execute(stmt).scalars().all()
        if not jobs:
            print("No jobs found.")
            return

        print("\nRecent cookbook_jobs entries:")
        for job in jobs:
            print(f"- id={job.id} task={job.task_name} status={job.status} result={job.result}")


def run_standalone() -> None:
    print("Running in standalone mode (no Redis required)...")

    chain_result = chain(
        aggregate_sales.s(),
        generate_report.s("standalone-sales-report"),
    ).apply()
    print(f"Chained result: {chain_result.get()}")

    send_result = send_notification.apply(
        kwargs={
            "recipient": "ops@example.com",
            "subject": "Standalone Notification",
            "message": "This email task ran synchronously via apply().",
            "simulate_transient_error": False,
        }
    )
    print(f"send_notification result: {send_result.get()}")

    batch_result = batch_email.apply(
        kwargs={
            "recipients": ["alice@example.com", "bob@example.com", "carol@example.com"],
            "subject": "Daily Digest",
            "message": "Synchronous batch email simulation.",
        }
    )
    print(f"batch_email result: {batch_result.get()}")

    cleanup_result = cleanup_old_records.apply(kwargs={"days": 90})
    print(f"cleanup_old_records result: {cleanup_result.get()}")


def run_async() -> None:
    print("Running in async mode (Redis broker + Celery worker required)...")

    chained_async_result = chain(
        aggregate_sales.s(),
        generate_report.s("async-sales-report"),
    ).apply_async()
    print(f"Submitted chain task id: {chained_async_result.id}")

    send_async_result = send_notification.delay(
        recipient="ops@example.com",
        subject="Async Notification",
        message="This email task ran asynchronously via delay().",
        simulate_transient_error=True,
    )
    print(f"Submitted send_notification task id: {send_async_result.id}")

    batch_async_result = batch_email.delay(
        recipients=["alice@example.com", "bob@example.com", "carol@example.com"],
        subject="Daily Digest",
        message="Asynchronous batch email simulation.",
    )
    print(f"Submitted batch_email task id: {batch_async_result.id}")

    cleanup_async_result = cleanup_old_records.delay(days=90)
    print(f"Submitted cleanup_old_records task id: {cleanup_async_result.id}")

    print("\nWaiting for task results...")
    print(f"Chain final result: {chained_async_result.get(timeout=120)}")
    print(f"send_notification result: {send_async_result.get(timeout=120)}")
    print(f"batch_email result: {batch_async_result.get(timeout=120)}")
    print(f"cleanup_old_records result: {cleanup_async_result.get(timeout=120)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Celery + CUBRID cookbook tasks")
    parser.add_argument(
        "--standalone",
        action="store_true",
        help="Execute tasks synchronously with .apply() (no Redis/worker needed)",
    )
    args = parser.parse_args()

    init_db()
    seed_sales_data()

    if args.standalone:
        run_standalone()
    else:
        run_async()

    print_recent_jobs()


if __name__ == "__main__":
    main()
