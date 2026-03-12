from __future__ import annotations

from typing import Any

from .products import products_bp


def register_blueprints(app: Any) -> None:
    app.register_blueprint(products_bp)
