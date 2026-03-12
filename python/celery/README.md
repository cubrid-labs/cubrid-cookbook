# Celery + CUBRID Cookbook Example

This example shows a Celery task queue that uses:

- Redis as the message broker
- CUBRID as the SQLAlchemy business database
- CUBRID (via Celery SQLAlchemy backend) for task result storage

Celery requires Redis (or RabbitMQ). CUBRID is used for business data, not as Celery's broker.

## Project files

- `app.py` - Celery app configuration
- `database.py` - SQLAlchemy engine/session setup for CUBRID
- `models.py` - ORM models with `cookbook_` table prefixes
- `tasks/data_tasks.py` - business data tasks (`aggregate_sales`, `generate_report`, `cleanup_old_records`)
- `tasks/email_tasks.py` - email simulation tasks (`send_notification`, `batch_email`)
- `run_tasks.py` - submit tasks and inspect results

## Prerequisites

- Python 3.10+
- Redis running on `localhost:6379`
- CUBRID running on `localhost:33000` with database `testdb`

Database URL used by this example:

`cubrid+pycubrid://dba@localhost:33000/testdb`

Broker URL used by this example:

`redis://localhost:6379/0`

## Optional Redis via Docker Compose

Use this snippet in any existing `docker-compose.yml`:

```yaml
services:
  redis:
    image: redis:7-alpine
    container_name: celery-redis
    ports:
      - "6379:6379"
```

Start Redis:

```bash
docker compose up -d redis
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Celery worker (async mode)

```bash
celery -A app:app worker --loglevel=info
```

In another shell:

```bash
python run_tasks.py
```

This submits:

- a task chain: `aggregate_sales -> generate_report`
- email tasks (`send_notification`, `batch_email`)
- cleanup task (`cleanup_old_records`)

## Standalone mode (no Redis)

Run synchronously without broker/worker:

```bash
python run_tasks.py --standalone
```

Standalone mode uses Celery `.apply()` so you can test task logic with only CUBRID running.

## Notes

- No Celery Beat (periodic scheduler) is used in this cookbook example.
- `send_notification` includes retry logic with `bind=True` and `max_retries=3`.
- CUBRID has no native BOOLEAN type, so model status flags use string/integer-friendly columns.
