"""04_relationships.py — ORM relationships with CUBRID.

Demonstrates:
- One-to-many relationships
- Many-to-many relationships
- Eager/lazy loading
- Cascading deletes
"""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Table, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    selectinload,
)

DATABASE_URL = "cubrid+pycubrid://dba@localhost:33000/testdb"


class Base(DeclarativeBase):
    pass


# Many-to-many association table
course_student = Table(
    "cookbook_course_student",
    Base.metadata,
    Column("course_id", Integer, ForeignKey("cookbook_courses.id"), primary_key=True),
    Column("student_id", Integer, ForeignKey("cookbook_students.id"), primary_key=True),
)


class Department(Base):
    __tablename__ = "cookbook_r_departments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))

    # One-to-many: Department has many Professors
    professors: Mapped[list[Professor]] = relationship(back_populates="department")

    def __repr__(self) -> str:
        return f"Department(id={self.id}, name='{self.name}')"


class Professor(Base):
    __tablename__ = "cookbook_professors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    dept_id: Mapped[int | None] = mapped_column(ForeignKey("cookbook_r_departments.id"))

    # Many-to-one: Professor belongs to Department
    department: Mapped[Department | None] = relationship(back_populates="professors")
    # One-to-many: Professor teaches many Courses
    courses: Mapped[list[Course]] = relationship(back_populates="professor")

    def __repr__(self) -> str:
        return f"Professor(id={self.id}, name='{self.name}')"


class Course(Base):
    __tablename__ = "cookbook_courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    credits: Mapped[int] = mapped_column(default=3)
    professor_id: Mapped[int | None] = mapped_column(ForeignKey("cookbook_professors.id"))

    # Many-to-one: Course belongs to Professor
    professor: Mapped[Professor | None] = relationship(back_populates="courses")
    # Many-to-many: Course has many Students
    students: Mapped[list[Student]] = relationship(
        secondary=course_student, back_populates="courses"
    )

    def __repr__(self) -> str:
        return f"Course(id={self.id}, title='{self.title}')"


class Student(Base):
    __tablename__ = "cookbook_students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    grade: Mapped[str | None] = mapped_column(String(10), default=None)

    # Many-to-many: Student takes many Courses
    courses: Mapped[list[Course]] = relationship(
        secondary=course_student, back_populates="students"
    )

    def __repr__(self) -> str:
        return f"Student(id={self.id}, name='{self.name}')"


def setup(engine) -> None:
    print("=== Relationships — Setup ===")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("  ✓ Created tables with foreign keys")


def seed_data(engine) -> None:
    """Create related data."""
    print("\n=== Seed Data ===")

    with Session(engine) as session:
        # Departments
        cs = Department(name="Computer Science")
        math = Department(name="Mathematics")

        # Professors
        prof_a = Professor(name="Dr. Smith", department=cs)
        prof_b = Professor(name="Dr. Jones", department=cs)
        prof_c = Professor(name="Dr. Taylor", department=math)

        # Courses
        algo = Course(title="Algorithms", credits=4, professor=prof_a)
        db = Course(title="Databases", credits=3, professor=prof_a)
        ml = Course(title="Machine Learning", credits=4, professor=prof_b)
        calc = Course(title="Calculus", credits=4, professor=prof_c)

        # Students
        alice = Student(name="Alice", grade="A")
        bob = Student(name="Bob", grade="B+")
        charlie = Student(name="Charlie", grade="A-")

        # Enroll students in courses (many-to-many)
        algo.students.extend([alice, bob, charlie])
        db.students.extend([alice, charlie])
        ml.students.extend([bob, charlie])
        calc.students.extend([alice])

        session.add_all([cs, math, prof_a, prof_b, prof_c, algo, db, ml, calc, alice, bob, charlie])
        session.commit()
        print("  ✓ Seeded 2 departments, 3 professors, 4 courses, 3 students")


def one_to_many(engine) -> None:
    """Navigate one-to-many relationships."""
    print("\n=== One-to-Many ===")

    with Session(engine) as session:
        # Department → Professors
        stmt = select(Department).options(selectinload(Department.professors))
        departments = session.scalars(stmt).all()

        for dept in departments:
            print(f"  {dept.name}:")
            for prof in dept.professors:
                print(f"    • {prof.name}")

        # Professor → Courses
        print()
        stmt = select(Professor).options(selectinload(Professor.courses))
        professors = session.scalars(stmt).all()

        for prof in professors:
            course_list = ", ".join(sorted(c.title for c in prof.courses)) or "none"
            print(f"  {prof.name} teaches: {course_list}")


def many_to_many(engine) -> None:
    """Navigate many-to-many relationships."""
    print("\n=== Many-to-Many ===")

    with Session(engine) as session:
        # Course → Students
        stmt = select(Course).options(selectinload(Course.students))
        courses = session.scalars(stmt).all()

        print("  Course enrollments:")
        for course in courses:
            students = ", ".join(sorted(s.name for s in course.students)) or "none"
            print(f"    {course.title:25s}  ({len(course.students)} students): {students}")

        # Student → Courses
        print("\n  Student schedules:")
        stmt = select(Student).options(selectinload(Student.courses))
        students = session.scalars(stmt).all()

        for student in students:
            courses_str = ", ".join(sorted(c.title for c in student.courses)) or "none"
            print(f"    {student.name:10s}  ({len(student.courses)} courses): {courses_str}")


def eager_loading(engine) -> None:
    """Demonstrate eager loading to avoid N+1 queries."""
    print("\n=== Eager Loading ===")

    with Session(engine) as session:
        # Without eager loading: N+1 problem
        # With selectinload: 2 queries total (1 for courses, 1 for students)
        stmt = (
            select(Course)
            .options(
                selectinload(Course.professor),
                selectinload(Course.students),
            )
            .order_by(Course.title)
        )
        courses = session.scalars(stmt).all()

        print("  Full course catalog:")
        for course in courses:
            prof_name = course.professor.name if course.professor else "TBD"
            student_count = len(course.students)
            print(f"    {course.title:25s}  Prof: {prof_name:15s}  Students: {student_count}")


def cleanup(engine) -> None:
    Base.metadata.drop_all(engine)
    print("\n✓ Cleaned up")


if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)

    try:
        setup(engine)
        seed_data(engine)
        one_to_many(engine)
        many_to_many(engine)
        eager_loading(engine)
    finally:
        cleanup(engine)
        engine.dispose()
