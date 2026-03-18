from __future__ import annotations

from importlib import import_module
from typing import Protocol, cast


class CursorProto(Protocol):
    def execute(self, sql: str, params: tuple[str, ...] | None = None) -> object: ...

    def close(self) -> None: ...


class ConnectionProto(Protocol):
    autocommit: bool

    def cursor(self) -> CursorProto: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def close(self) -> None: ...


class PycubridDriver(Protocol):
    OperationalError: type[Exception]

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


def connect(driver: PycubridDriver) -> ConnectionProto:
    return driver.connect(
        host="localhost",
        port=33000,
        database="testdb",
        user="dba",
        password="",
    )


def main() -> None:
    driver = pycubrid()

    writer_conn = connect(driver)
    blocked_conn = connect(driver)

    writer = writer_conn.cursor()
    blocked = blocked_conn.cursor()

    try:
        _ = writer.execute("DROP TABLE IF EXISTS cookbook_timeout_demo")
        _ = writer.execute(
            """
            CREATE TABLE cookbook_timeout_demo (
                id INT PRIMARY KEY,
                note VARCHAR(100)
            )
            """
        )
        _ = writer.execute("INSERT INTO cookbook_timeout_demo (id, note) VALUES (1, 'initial')")
        writer_conn.commit()

        writer_conn.autocommit = False
        blocked_conn.autocommit = False

        _ = writer.execute("UPDATE cookbook_timeout_demo SET note = 'locked' WHERE id = 1")
        _ = blocked.execute("SET SYSTEM PARAMETERS 'lock_timeout=1'")

        try:
            _ = blocked.execute("UPDATE cookbook_timeout_demo SET note = 'blocked' WHERE id = 1")
            blocked_conn.commit()
        except driver.OperationalError as error:
            blocked_conn.rollback()
            print("Lock/query timeout handled with rollback.")
            print(f"Caught: {type(error).__name__}: {error}")
        finally:
            writer_conn.rollback()
    finally:
        _ = writer.execute("DROP TABLE IF EXISTS cookbook_timeout_demo")
        writer_conn.commit()
        writer.close()
        blocked.close()
        writer_conn.close()
        blocked_conn.close()


if __name__ == "__main__":
    main()
