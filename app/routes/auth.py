import sqlite3
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from sqlalchemy import or_
from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    # 1. HTTP Translation: Parse request payload parameters
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # 2. HTTP Translation: Enforce structural presence constraints
    if not username or not email or not password:
        return jsonify({"error": "username, email, and password are required"}), 400

    # 3. ORM Integration: Check for an existing account matching username OR email
    existing_user = User.query.filter(
        or_(
            User.username == username,
            User.email == email
        )
    ).first()
    
    if existing_user:
        return jsonify({"error": "username or email already exists"}), 409

    # 4. Cryptographic Security Policy: Securely hash credentials before saving
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
    
    # 5. ORM Integration: Instantiate a fresh User model object instance
    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )

    try:
        # 6. Session Tracking: Stage and save the new account permanently
        db.session.add(new_user)
        db.session.commit()
    except sqlite3.IntegrityError:
        # Rollback the session transaction block to restore a stable state on conflict
        db.session.rollback()
        return jsonify({"error": "username or email already exists"}), 409

    return jsonify({"message": "User registered successfully"}), 201
