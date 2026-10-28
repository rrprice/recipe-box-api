from app.models import Recipe
from sqlalchemy import or_

def list_recipes_for_user(user):
    """
    Business Rules Layer: Validates permissions based on user state
    and queries the database using the SQLAlchemy ORM instead of raw SQL.
    """
    # 1. Anonymous users: see only public recipes ordered by ID
    if user is None:
        return Recipe.query.filter(Recipe.is_public == 1).order_by(Recipe.id).all()
        
    # 2. Admin users: see ALL recipes ordered by ID
    if user.get("role") == "admin":
        return Recipe.query.order_by(Recipe.id).all()
        
    # 3. Regular users: see public recipes OR private recipes they explicitly own
    return Recipe.query.filter(
        or_(
            Recipe.is_public == 1,
            Recipe.user_id == user.get("id")
        )
    ).order_by(Recipe.id).all()


def get_recipe_by_id(recipe_id):
    """
    Data Access & Business Layer: Looks up a single Recipe by its unique ID.
    Returns the Recipe object model instance, or None if it is not found.
    """
    return Recipe.query.get(recipe_id)


def get_total_recipes():
    """
    Business Rules Layer: Uses the ORM metadata context to count the 
    total number of recipe rows present in the tracking tables.
    """
    return Recipe.query.count()
