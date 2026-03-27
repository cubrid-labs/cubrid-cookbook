from __future__ import annotations

from importlib import import_module
from typing import Protocol, cast


class CursorProto(Protocol):
    def execute(self, sql: str, params: tuple[str, ...] | None = None) -> object: ...

    def close(self) -> None: ...


class ConnectionProto(Protocol):
    def cursor(self) -> CursorProto: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def close(self) -> None: ...


class PycubridDriver(Protocol):
    IntegrityError: type[Exception]

    def connect(
        self,
        *,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
    ) -> ConnectionProto: ...


def pycubrid() -> PycubridDriver:
    module = import_module("pycubrid")
    return cast(PycubridDriver, cast(object, module))


def main() -> None:
    driver = pycubrid()

    conn = driver.connect(
        host="localhost",
        port=33000,
        database="testdb",
        user="dba",
        password="",
    )
    cursor = conn.cursor()

    try:
        _ = cursor.execute("DROP TABLE IF EXISTS cookbook_error_users")
        _ = cursor.execute(
            """
            CREATE TABLE cookbook_error_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(200) UNIQUE NOT NULL
            )
            """
        )
        conn.commit()

        _ = cursor.execute(
            "INSERT INTO cookbook_error_users (email) VALUES (?)",
            ("alice@example.com",),
        )
        conn.commit()

        try:
            _ = cursor.execute(
                "INSERT INTO cookbook_error_users (email) VALUES (?)",
                ("alice@example.com",),
            )
            conn.commit()
        except driver.IntegrityError as error:
            conn.rollback()
            print("Unique constraint violation handled.")
            print(f"Caught: {type(error).__name__}: {error}")
    finally:
        _ = cursor.execute("DROP TABLE IF EXISTS cookbook_error_users")
        conn.commit()
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
