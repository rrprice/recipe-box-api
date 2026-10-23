import sqlite3
from flask import Blueprint, g, jsonify, request
from app.db import get_db
from app.auth import is_owner_or_admin, login_required
from app.services.recipe_service import list_recipes_for_user, get_total_recipes

recipes_bp = Blueprint("recipes", __name__)


def recipe_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "ingredients": row["ingredients"],
        "instructions": row["instructions"],
        "is_public": bool(row["is_public"]),
        "user_id": row["user_id"],
    }


@recipes_bp.get("")
def list_recipes():
    rows = list_recipes_for_user(g.current_user)
    return jsonify([recipe_to_dict(r) for r in rows])


@recipes_bp.route("/count", methods=["GET"])
def get_recipe_metrics_count():
    """
    HTTP Translation Layer: Receives the metrics collection request, 
    invokes the backend statistics service, and serializes the 
    resulting data structure into a standard JSON response.
    """
    count = get_total_recipes()
    return jsonify({"count": count}), 200


@recipes_bp.get("/<int:recipe_id>")
def get_recipe(recipe_id):
    row = get_db().execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()
    if row is None:
        return jsonify({"error": "recipe not found"}), 404
    if not row["is_public"]:
        if g.current_user is None:
            return jsonify({"error": "authentication required"}), 401
        if not is_owner_or_admin(row):
            return jsonify({"error": "this recipe is private"}), 403
    return jsonify(recipe_to_dict(row))


@recipes_bp.post("")
@login_required
def create_recipe():
    data = request.get_json(silent=True)
    if not data or not data.get("title") or not data.get("ingredients"):
        return jsonify({"error": "title and ingredients are required"}), 400
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO recipes (title, ingredients, instructions, is_public, user_id)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                data["title"],
                data["ingredients"],
                data.get("instructions", ""),
                1 if data.get("is_public", True) else 0,
                g.current_user["id"],
            ),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "a recipe with that title already exists"}), 409
    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (cur.lastrowid,)
    ).fetchone()
    return jsonify(recipe_to_dict(row)), 201


@recipes_bp.patch("/<int:recipe_id>")
@login_required
def update_recipe(recipe_id):
    db = get_db()
    row = db.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    if row is None:
        return jsonify({"error": "recipe not found"}), 404
    if not is_owner_or_admin(row):
        return jsonify({"error": "you can only edit your own recipes"}), 403
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "a JSON body is required"}), 400
    fields, values = [], []
    for column in ("title", "ingredients", "instructions"):
        if column in data:
            fields.append(f"{column} = ?")
            values.append(data[column])
    if "is_public" in data:
        fields.append("is_public = ?")
        values.append(1 if data["is_public"] else 0)
    if not fields:
        return jsonify({"error": "nothing to update"}), 400
    values.append(recipe_id)
    try:
        db.execute(f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?", values)
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "a recipe with that title already exists"}), 409
    row = db.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    return jsonify(recipe_to_dict(row))


@recipes_bp.delete("/<int:recipe_id>")
@login_required
def delete_recipe(recipe_id):
    db = get_db()
    row = db.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    if row is None:
        return jsonify({"error": "recipe not found"}), 404
    if not is_owner_or_admin(row):
        return jsonify({"error": "you can only delete your own recipes"}), 403
    db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    db.commit()
    return "", 204
