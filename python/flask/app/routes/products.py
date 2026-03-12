from __future__ import annotations

import importlib
from decimal import Decimal, InvalidOperation

from sqlalchemy import select

from ..models import Product, db

flask = importlib.import_module("flask")
Blueprint = flask.Blueprint
flash = flask.flash
jsonify = flask.jsonify
redirect = flask.redirect
render_template = flask.render_template
request = flask.request
url_for = flask.url_for

products_bp = Blueprint("products", __name__)


def _parse_price(value: str) -> Decimal:
    try:
        return Decimal(value).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Price must be a valid decimal number.") from exc


def _parse_in_stock(value: object) -> int:
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, int):
        return 1 if value else 0
    if isinstance(value, str):
        return 1 if value.lower() in {"1", "true", "yes", "on"} else 0
    return 0


def _product_or_404(product_id: int) -> Product:
    product = db.session.get(Product, product_id)
    if product is None:
        raise LookupError("Product not found.")
    return product


@products_bp.get("/products")
def list_products():
    products = db.session.execute(select(Product).order_by(Product.id.desc())).scalars().all()
    return render_template("products/list.html", products=products)


@products_bp.get("/products/new")
def create_product_form():
    return render_template("products/form.html", product=None)


@products_bp.post("/products")
def create_product():
    form = request.form
    name = form.get("name", "").strip()
    description = form.get("description", "").strip() or None
    category = form.get("category", "").strip()

    if not name:
        flash("Name is required.", "danger")
        return render_template("products/form.html", product=None), 400
    if not category:
        flash("Category is required.", "danger")
        return render_template("products/form.html", product=None), 400

    try:
        price = _parse_price(form.get("price", ""))
    except ValueError as exc:
        flash(str(exc), "danger")
        return render_template("products/form.html", product=None), 400

    product = Product(
        name=name,
        description=description,
        price=price,
        category=category,
        in_stock=_parse_in_stock(form.get("in_stock")),
    )

    db.session.add(product)
    db.session.commit()
    flash("Product created successfully.", "success")
    return redirect(url_for("products.list_products"))


@products_bp.get("/products/<int:product_id>")
def get_product(product_id: int):
    try:
        product = _product_or_404(product_id)
    except LookupError:
        flash("Product not found.", "warning")
        return redirect(url_for("products.list_products"))
    return render_template("products/detail.html", product=product)


@products_bp.get("/products/<int:product_id>/edit")
def edit_product_form(product_id: int):
    try:
        product = _product_or_404(product_id)
    except LookupError:
        flash("Product not found.", "warning")
        return redirect(url_for("products.list_products"))
    return render_template("products/form.html", product=product)


@products_bp.post("/products/<int:product_id>/update")
def update_product(product_id: int):
    try:
        product = _product_or_404(product_id)
    except LookupError:
        flash("Product not found.", "warning")
        return redirect(url_for("products.list_products"))

    form = request.form
    name = form.get("name", "").strip()
    description = form.get("description", "").strip() or None
    category = form.get("category", "").strip()

    if not name:
        flash("Name is required.", "danger")
        return render_template("products/form.html", product=product), 400
    if not category:
        flash("Category is required.", "danger")
        return render_template("products/form.html", product=product), 400

    try:
        product.price = _parse_price(form.get("price", ""))
    except ValueError as exc:
        flash(str(exc), "danger")
        return render_template("products/form.html", product=product), 400

    product.name = name
    product.description = description
    product.category = category
    product.in_stock = _parse_in_stock(form.get("in_stock"))

    db.session.commit()
    flash("Product updated successfully.", "success")
    return redirect(url_for("products.get_product", product_id=product.id))


@products_bp.post("/products/<int:product_id>/delete")
def delete_product(product_id: int):
    try:
        product = _product_or_404(product_id)
    except LookupError:
        flash("Product not found.", "warning")
        return redirect(url_for("products.list_products"))

    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully.", "success")
    return redirect(url_for("products.list_products"))


@products_bp.get("/api/products")
def api_list_products():
    products = db.session.execute(select(Product).order_by(Product.id.desc())).scalars().all()
    return jsonify([product.to_dict() for product in products])


@products_bp.get("/api/products/<int:product_id>")
def api_get_product(product_id: int):
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Product not found."}), 404
    return jsonify(product.to_dict())


@products_bp.post("/api/products")
def api_create_product():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    description = str(payload.get("description", "")).strip() or None
    category = str(payload.get("category", "")).strip()

    if not name:
        return jsonify({"error": "name is required"}), 400
    if not category:
        return jsonify({"error": "category is required"}), 400

    try:
        price = _parse_price(str(payload.get("price", "")))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    product = Product(
        name=name,
        description=description,
        price=price,
        category=category,
        in_stock=_parse_in_stock(payload.get("in_stock", 1)),
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@products_bp.put("/api/products/<int:product_id>")
def api_update_product(product_id: int):
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Product not found."}), 404

    payload = request.get_json(silent=True) or {}

    if "name" in payload:
        name = str(payload.get("name", "")).strip()
        if not name:
            return jsonify({"error": "name cannot be empty"}), 400
        product.name = name

    if "description" in payload:
        description = str(payload.get("description", "")).strip()
        product.description = description or None

    if "category" in payload:
        category = str(payload.get("category", "")).strip()
        if not category:
            return jsonify({"error": "category cannot be empty"}), 400
        product.category = category

    if "price" in payload:
        try:
            product.price = _parse_price(str(payload.get("price", "")))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    if "in_stock" in payload:
        product.in_stock = _parse_in_stock(payload.get("in_stock"))

    db.session.commit()
    return jsonify(product.to_dict())


@products_bp.delete("/api/products/<int:product_id>")
def api_delete_product(product_id: int):
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Product not found."}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully."}), 200
