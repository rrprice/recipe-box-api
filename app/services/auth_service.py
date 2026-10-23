from werkzeug.security import generate_password_hash
from app.data import auth_data

def register_user(conn, username, email, password):
    """
    Business Rules Layer: Enforces uniqueness criteria, applies password 
    hashing protocols, and passes sanitized parameters to the data access layer.
    
    Returns a simple tuple pattern: (user_data_dict, error_string_flag)
    """
    # 1. Enforce validation constraint: Verify account uniqueness
    existing_user = auth_data.find_user_by_username_or_email(conn, username, email)
    if existing_user:
        return None, "user_exists"
        
    # 2. Enforce security policy: Hash plaintext credentials before storage
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
    
    # 3. Hand off the execution parameters to the isolated storage layer
    auth_data.insert_user(conn, username, email, hashed_password)
    
    return {"username": username, "email": email}, None
