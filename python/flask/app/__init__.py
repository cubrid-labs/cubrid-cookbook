from __future__ import annotations

import importlib
import os
from typing import Any

from .models import db

flask = importlib.import_module("flask")
Flask = flask.Flask


def create_app() -> Any:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "cubrid+pycubrid://dba@localhost:33000/testdb"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from .routes import register_blueprints

    register_blueprints(app)

    @app.cli.command("init-db")
    def init_db_command() -> None:
        with app.app_context():
            db.create_all()
        print("Database tables created.")

    @app.get("/")
    def index() -> tuple[str, int, dict[str, str]]:
        return "", 302, {"Location": "/products"}

    with app.app_context():
        db.create_all()

    return app
