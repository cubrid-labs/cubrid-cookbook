from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import final

from sqlalchemy import Date, Integer, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


@final
class Employee(Base):
    __tablename__ = "cookbook_employee"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    salary: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
