import json
from app import create_app

def run_test_client():
    # 1. Instantiate the application factory explicitly using the isolated testing configuration mapping
    app = create_app("testing")
    
    print("--- Starting In-Process Test Client Execution ---")
    
    # 2. Open the thread-safe context gateway test client
    with app.test_client() as client:
        
        # Test Case A: User Registration
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
        
        # Test Case B: Fetching Recipes Dataset
        print("\n[Action] Sending GET /recipes...")
        recipes_response = client.get("/recipes")
        print(f"[Status Code] {recipes_response.status_code}")
        print(f"[Body] {recipes_response.get_data(as_text=True)}")

if __name__ == "__main__":
    run_test_client()
