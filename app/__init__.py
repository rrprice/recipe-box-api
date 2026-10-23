import os
from flask import Flask, g, jsonify, request
from functools import wraps
from .db import get_db, close_db, init_db

# =====================================================================
# 1. ENVIRONMENT VALIDATION UTILITIES
# =====================================================================
def require_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        raise RuntimeError(f"Required environment variable {name} is missing")
    return value

# =====================================================================
# 2. APPLICATION CONFIGURATION CLASSES
# =====================================================================
class Config:
    """Base configuration class for shared default settings."""
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development configuration that reads settings from the system environment."""
    DEBUG = True
    DATABASE = require_env("DATABASE_PATH")

class TestingConfig(Config):
    """Testing configuration running completely in memory or isolated local tracking files."""
    TESTING = True
    DATABASE = "recipes_test.db"

# Configuration Mapping Dictionary
CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}

# Aliasing get_db to get_db_connection for backwards compatibility with old endpoints
get_db_connection = get_db

# =====================================================================
# 3. AUTHENTICATION MIDDLEWARE STUBS
# =====================================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.get("current_user") is None:
            return jsonify({"error": "authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

def is_owner_or_admin(recipe_row):
    if g.get("current_user") is None:
        return False
    if g.current_user.get("role") == "admin":
        return True
    return recipe_row["user_id"] == g.current_user["id"]

# =====================================================================
# 4. APPLICATION FACTORY ENTRY POINT
# =====================================================================
def create_app(config_name="development"):
    app = Flask(__name__)

    # Select and apply the configuration class dynamically
    config_class = CONFIGS.get(config_name, DevelopmentConfig)
    app.config.from_object(config_class)

    # Automatically initialize your database tables on application boot
    init_db(app)

    # Register the database context teardown cleanup hook
    app.teardown_appcontext(close_db)

    # Mock user context loader injection for endpoint validation context
    @app.before_request
    def load_mock_user():
        # Injecting a mock ordinary user for structural application testing paths
        g.current_user = {"id": 1, "username": "robby", "role": "user"}

    # Import blueprints internally to prevent circular package imports
    from app.routes.auth import auth_bp
    from app.routes.recipes import recipes_bp
    
    # Register application route blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(recipes_bp, url_prefix="/recipes")

    return app
