from __future__ import annotations

from importlib import import_module
from typing import Protocol, cast


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
    ) -> object: ...


def pycubrid() -> PycubridDriver:
    module = import_module("pycubrid")
    return cast(PycubridDriver, cast(object, module))


def main() -> None:
    driver = pycubrid()

    try:
        _ = driver.connect(
            host="127.0.0.1",
            port=44444,
            database="testdb",
            user="dba",
            password="",
        )
    except driver.OperationalError as error:
        print("Connection failed as expected.")
        print(f"Caught: {type(error).__name__}: {error}")
        return

    raise RuntimeError("Expected connection failure but connection succeeded.")


if __name__ == "__main__":
    main()
