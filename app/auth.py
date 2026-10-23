from functools import wraps
from flask import g, jsonify, request

def login_required(f):
    """
    Business Rules Layer: Reusable wrapper that checks for a verified, 
    authenticated user context before allowing a request to execute.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.get("current_user") is None:
            return jsonify({"error": "authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function


def is_owner_or_admin(recipe_row):
    """
    Business Rules Layer: Enforces structural role and resource ownership constraints.
    Returns True if the authenticated user is an administrator or owns the row.
    """
    if g.get("current_user") is None:
        return False
    if g.current_user.get("role") == "admin":
        return True
    return recipe_row["user_id"] == g.current_user["id"]
