import json
from app import create_app
from app.extensions import db

def run_test_client():
    app = create_app("testing")
    print("--- Starting In-Process Test Client Execution ---")
    
    with app.test_client() as client:
        print("\n[Action] Sending POST /register...")
        reg_payload = {
            "username": "test_runner_user",
            "email": "test_runner@example.test",
            "password": "secure_test_password"
        }
        reg_response = client.post(
            "/register",
            data=json.dumps(reg_payload),
            content_type="application/json"
        )
        print(f"[Status Code] {reg_response.status_code}")
        print(f"[Body] {reg_response.get_data(as_text=True)}")
        
        print("\n[Action] Sending GET /recipes...")
        recipes_response = client.get("/recipes")
        print(f"[Status Code] {recipes_response.status_code}")
        print(f"[Body] {recipes_response.get_data(as_text=True)}")

if __name__ == "__main__":
    run_test_client()
