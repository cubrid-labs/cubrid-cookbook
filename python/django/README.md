# Django + CUBRID Cookbook (Hybrid Integration)

Django does not have a native CUBRID backend. This example shows two integration patterns:

1. Pattern 1: Raw SQL via `pycubrid` in a Django view
2. Pattern 2: SQLAlchemy ORM used alongside Django for CUBRID tables

Django still uses SQLite for its own framework tables (`auth`, `admin`, `sessions`, etc.).
Application data for this example is stored in CUBRID using SQLAlchemy and pycubrid.

## Project Structure

```
django/
├── manage.py
├── requirements.txt
├── README.md
├── cubrid_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── cookbook/
    ├── __init__.py
    ├── cubrid_db.py
    ├── sa_models.py
    ├── views.py
    ├── urls.py
    └── templates/cookbook/
        ├── dashboard.html
        └── raw_sql.html
```

## CUBRID Connection

- SQLAlchemy URL: `cubrid+pycubrid://dba@localhost:33000/testdb`
- pycubrid connect call:

```python
pycubrid.connect(host="localhost", port=33000, database="testdb", user="dba")
```

`pycubrid` uses `qmark` parameter style (`?`) for raw SQL placeholders.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Optional environment overrides:

   - `CUBRID_SQLALCHEMY_URL`
   - `CUBRID_HOST`
   - `CUBRID_PORT`
   - `CUBRID_DB`
   - `CUBRID_USER`
   - `CUBRID_PASSWORD`

3. Run Django migrations for SQLite-backed Django framework tables:

   ```bash
   python manage.py migrate
   ```

4. Start the app:

   ```bash
   python manage.py runserver
   ```

## Routes

- `/` - Dashboard and add-employee form (SQLAlchemy ORM pattern)
- `/raw-sql/` - Raw SQL examples with pycubrid

## Why This Hybrid Approach

- Django ORM cannot target CUBRID directly because no official Django CUBRID backend exists.
- SQLAlchemy + `sqlalchemy-cubrid` provides robust CUBRID dialect support.
- Django still provides routing, templating, and request handling.
