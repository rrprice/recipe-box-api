def find_user_by_username_or_email(conn, username, email):
    """
    Data Access Layer: Queries the database for a matching username or email.
    Returns the database row record if found, or None if it doesn't exist.
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (username, email),
    )
    return cursor.fetchone()


def insert_user(conn, username, email, password_hash):
    """
    Data Access Layer: Inserts a new user record safely into the users table.
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash),
    )
    conn.commit()
