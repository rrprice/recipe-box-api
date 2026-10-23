from app.db import get_db, get_recipe_count

def list_recipes_for_user(user):
    """
    Business Rules & Data Access: Validates permissions based on user state
    and queries the database to return raw cursor rows.
    """
    db = get_db()
    
    if user is None:
        return db.execute(
            "SELECT * FROM recipes WHERE is_public = 1 ORDER BY id"
        ).fetchall()
        
    if user["role"] == "admin":
        return db.execute("SELECT * FROM recipes ORDER BY id").fetchall()
        
    return db.execute(
        "SELECT * FROM recipes WHERE is_public = 1 OR user_id = ? ORDER BY id",
        (user["id"],),
    ).fetchall()


def get_total_recipes():
    """
    Business Rules Layer: Connects to the database repository context 
    and handles the coordination for retrieving the total recipe metric.
    """
    conn = get_db()
    return get_recipe_count(conn)
