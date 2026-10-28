import sqlite3
from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import IntegrityError
from app.auth import is_owner_or_admin, login_required
from app.extensions import db, cache
from app.models import Recipe
from app.services.recipe_service import list_recipes_for_user, get_total_recipes, get_recipe_by_id

recipes_bp = Blueprint("recipes", __name__)


def recipe_to_dict(recipe):
    """
    HTTP Translation Layer: Converts a declarative SQLAlchemy Recipe object 
    into a clean Python dictionary structure for standard JSON serialization.
    """
    return {
        "id": recipe.id,
        "title": recipe.title,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "is_public": bool(recipe.is_public),
        "user_id": recipe.user_id,
    }


@recipes_bp.get("")
@cache.cached()  # PERFORMANCE TUNING: Cache the full collection output for 60 seconds
def list_recipes():
    # Call the service layer to handle authorization business rules via the ORM
    rows = list_recipes_for_user(g.current_user)
    
    # HTTP Translation: Serialize the collection of objects into a JSON list
    return jsonify([recipe_to_dict(r) for r in rows])


@recipes_bp.route("/count", methods=["GET"])
def get_recipe_metrics_count():
    """
    HTTP Translation Layer: Receives the metrics collection request, 
    invokes the backend statistics service, and serializes the count.
    """
    count = get_total_recipes()
    return jsonify({"count": count}), 200


@recipes_bp.get("/<int:recipe_id>")
def get_recipe(recipe_id):
    # Service Invocation: Look up a single Recipe object instance using the ORM helper
    recipe = get_recipe_by_id(recipe_id)
    
    # HTTP Translation: Guard against non-existent resource paths with a standard 404
    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404
        
    # Business Rules Layer: Enforce visibility rules and authorization checks
    if not recipe.is_public:
        if g.current_user is None:
            return jsonify({"error": "authentication required"}), 401
        if not is_owner_or_admin(recipe):
            return jsonify({"error": "this recipe is private"}), 403
            
    # HTTP Translation: Serialize the single model object context into JSON output
    return jsonify(recipe_to_dict(recipe))


@recipes_bp.post("")
@login_required
def create_recipe():
    # 1. HTTP Translation: Parse request payload parameters
    data = request.get_json(silent=True)
    if not data or not data.get("title") or not data.get("ingredients"):
        return jsonify({"error": "title and ingredients are required"}), 400

    # 2. ORM Integration: Instantiate a fresh declarative Recipe model object
    new_recipe = Recipe(
        title=data["title"],
        ingredients=data["ingredients"],
        instructions=data.get("instructions", ""),
        is_public=1 if data.get("is_public", True) else 0,
        user_id=g.current_user["id"]
    )

    try:
        # 3. Session Tracking: Stage and save the model object instance permanently
        db.session.add(new_recipe)
        db.session.commit()
    except IntegrityError:
        # Rollback the session transaction block to restore stable state on conflict
        db.session.rollback()
        return jsonify({"error": "a recipe with that title already exists or user invalid"}), 409

    return jsonify(recipe_to_dict(new_recipe)), 201


@recipes_bp.patch("/<int:recipe_id>")
@login_required
def update_recipe(recipe_id):
    # 1. ORM Lookup: Extract the single Recipe model object instance from the database
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404
        
    # 2. Authorization Guard: Validate user/role permissions against the model instance
    if not is_owner_or_admin(recipe):
        return jsonify({"error": "you can only edit your own recipes"}), 403
        
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "a JSON body is required"}), 400
        
    # 3. Object Field Modification: Update properties directly on the object instance
    has_updates = False
    for field in ("title", "ingredients", "instructions"):
        if field in data:
            setattr(recipe, field, data[field])
            has_updates = True
            
    if "is_public" in data:
        recipe.is_public = 1 if data["is_public"] else 0
        has_updates = True
        
    if not has_updates:
        return jsonify({"error": "nothing to update"}), 400
        
    try:
        # 4. Session Flashing: Commit the modified state directly to the persistence layer
        db.session.commit()
    except IntegrityError:
        # Rollback the transaction to maintain a stable connection block on collision
        db.session.rollback()
        return jsonify({"error": "a recipe with that title already exists"}), 409
        
    # Return the updated object straight from current context memory
    return jsonify(recipe_to_dict(recipe))


@recipes_bp.delete("/<int:recipe_id>")
@login_required
def delete_recipe(recipe_id):
    # 1. ORM Lookup: Look up the single Recipe object directly by its unique id
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    
    # 2. HTTP Translation: Check for existence
    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404
        
    # 3. Business Rules Layer: Pass the model instance straight to the authorization check helper
    if not is_owner_or_admin(recipe):
        return jsonify({"error": "you can only delete your own recipes"}), 403
        
    # 4. Session Tracking: Delete the staged object instance from tracking memory and commit
    db.session.delete(recipe)
    db.session.commit()
    
    return "", 204
