from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from datetime import date
from decimal import Decimal, InvalidOperation
from importlib import import_module
from typing import Protocol, cast

from sqlalchemy import select

from .cubrid_db import get_engine, pycubrid_cursor, session_scope
from .sa_models import Base, Employee

django_shortcuts = import_module(".".join(["django", "shortcuts"]))
redirect = cast(Callable[[str], object], django_shortcuts.redirect)
render = cast(Callable[..., object], django_shortcuts.render)


class ParamsLike(Protocol):
    def get(self, key: str, default: object = "") -> object: ...


class RequestLike(Protocol):
    method: str
    POST: ParamsLike | Mapping[str, object]
    GET: ParamsLike | Mapping[str, object]


def _as_text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _ensure_schema() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def dashboard(request: RequestLike) -> object:
    error_message: str | None = None
    employees: list[Employee] = []

    try:
        _ensure_schema()
        with session_scope() as session:
            statement = select(Employee).order_by(Employee.id)
            employees = list(session.scalars(statement).all())
    except Exception as exc:
        error_message = str(exc)

    context = {
        "employees": employees,
        "error_message": error_message,
        "cubrid_url": "cubrid+pycubrid://dba@localhost:33000/testdb",
    }
    return render(request, "cookbook/dashboard.html", context)


def add_employee(request: RequestLike) -> object:
    if request.method != "POST":
        return redirect("dashboard")

    name = _as_text(request.POST.get("name", ""))
    department = _as_text(request.POST.get("department", ""))
    salary_value = _as_text(request.POST.get("salary", ""))
    hire_date_value = _as_text(request.POST.get("hire_date", ""))

    if not name or not department or not salary_value or not hire_date_value:
        return redirect("dashboard")

    try:
        salary = Decimal(salary_value)
        parsed_hire_date = date.fromisoformat(hire_date_value)
    except (InvalidOperation, ValueError):
        return redirect("dashboard")

    try:
        _ensure_schema()
        with session_scope() as session:
            session.add(
                Employee(
                    name=name,
                    department=department,
                    salary=salary,
                    hire_date=parsed_hire_date,
                )
            )
    except Exception:
        return redirect("dashboard")

    return redirect("dashboard")


def raw_sql_examples(request: RequestLike) -> object:
    min_salary_raw = _as_text(request.GET.get("min_salary", "0"))
    try:
        min_salary = Decimal(min_salary_raw)
    except InvalidOperation:
        min_salary = Decimal("0")

    summary: dict[str, object] = {
        "total_employees": None,
        "average_salary": None,
        "departments": [],
        "high_earners": [],
    }
    error_message: str | None = None

    try:
        with pycubrid_cursor() as cursor:
            _ = cursor.execute("SELECT COUNT(*) FROM cookbook_employee")
            count_row = cursor.fetchone()

            _ = cursor.execute("SELECT AVG(salary) FROM cookbook_employee")
            avg_row = cursor.fetchone()

            _ = cursor.execute(
                "SELECT department, COUNT(*) FROM cookbook_employee GROUP BY department ORDER BY department"
            )
            departments = cursor.fetchall()

            _ = cursor.execute(
                "SELECT id, name, salary FROM cookbook_employee WHERE salary >= ? ORDER BY salary DESC",
                (str(min_salary),),
            )
            high_earners = cursor.fetchall()

        summary["total_employees"] = count_row[0] if count_row else 0
        summary["average_salary"] = avg_row[0] if avg_row else None
        summary["departments"] = departments
        summary["high_earners"] = high_earners
    except Exception as exc:
        error_message = str(exc)

    context = {
        "summary": summary,
        "error_message": error_message,
        "query_paramstyle_note": "pycubrid uses qmark placeholders (?).",
        "min_salary": min_salary,
    }
    return render(request, "cookbook/raw_sql.html", context)
