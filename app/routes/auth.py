from flask import Blueprint, request, jsonify
from app.db import get_db
from app.services.auth_service import register_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    # 1. HTTP Translation: Parse and extract JSON payload parameters
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # 2. HTTP Translation: Enforce structural presence constraints
    if not username or not email or not password:
        return jsonify({"error": "username, email, and password are required"}), 400

    # 3. HTTP Translation: Open active database channel for request lifecycle
    conn = get_db()

    # 4. Service Delegation: Invoke core business authorization logic rules
    user, error = register_user(conn, username, email, password)

    # 5. HTTP Translation: Map service layer errors to standard client responses
    if error == "user_exists":
        return jsonify({"error": "username or email already exists"}), 409

    return jsonify({"message": "User registered successfully"}), 201
