import os
from flask import Flask, g
from app.extensions import db, migrate

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
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration that reads settings from the system environment."""
    DEBUG = True
    DATABASE = require_env("DATABASE_PATH")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{require_env('DATABASE_PATH')}"

class TestingConfig(Config):
    """Testing configuration running completely on isolated local files."""
    TESTING = True
    DATABASE = "recipes_test.db"
    SQLALCHEMY_DATABASE_URI = "sqlite:///recipes_test.db"

# Configuration Mapping Dictionary
CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}

# =====================================================================
# 3. APPLICATION FACTORY ENTRY POINT
# =====================================================================
def create_app(config_name="development"):
    app = Flask(__name__)

    # Select and apply the configuration class dynamically
    config_class = CONFIGS.get(config_name, DevelopmentConfig)
    app.config.from_object(config_class)

    # Bind the extensions to the app lifecycle context
    db.init_app(app)
    migrate.init_app(app, db)

    # REGISTER MODELS METADATA BEFORE INITIALIZATION
    from app import models

    # AUTOMATIC TABLE SETUP: Disabled for migration tracking baseline generation
    # with app.app_context():
    #     db.create_all()

    # Mock user context loader injection for endpoint validation context
    @app.before_request
    def load_mock_user():
        from app.models import User
        # Ensure a default mock user exists in the active test database
        user = User.query.filter_by(id=1).first()
        if not user:
            user = User(id=1, username="robby", email="robby@example.test", password_hash="mock_hash")
            db.session.add(user)
            db.session.commit()
        g.current_user = {"id": user.id, "username": user.username, "role": "user"}

    # Import blueprints internally to prevent circular package imports
    from app.routes.auth import auth_bp
    from app.routes.recipes import recipes_bp
    
    # Register application route blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(recipes_bp, url_prefix="/recipes")

    return app
