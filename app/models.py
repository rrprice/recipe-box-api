from app.extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    
    # NEW SCALAR COLUMN: Nullable string field to track registration origin
    signup_source = db.Column(db.String, nullable=True)

    recipes = db.relationship("Recipe", back_populates="owner", cascade="all, delete-orphan")


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    ingredients = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False, default="")
    is_public = db.Column(db.Integer, nullable=False, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    owner = db.relationship("User", back_populates="recipes")
