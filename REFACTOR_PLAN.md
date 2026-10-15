# Refactor Plan

## Current responsibilities in app.py
- Handling user registration and hashing passwords
- Verifying user login credentials
- Decoding and verifying signed JWT tokens
- Enforcing the owner-or-admin authorization rule
- Executing parameterized SQL queries
- Processing recipe search queries

Total responsibilities: 6

## Target package layout
recipe-box-api/
  app.py              # Application initialization, configuration loading, and server startup

  auth/
    routes.py         # Authentication endpoints (POST /register, POST /login)
    services.py       # Business logic for password hashing, verification, and JWT generation
    data.py           # Database access layer for performing user account queries

  recipes/
    routes.py         # Recipe endpoints (GET /recipes/by-ingredient, PATCH, DELETE)
    services.py       # Business logic for recipe validation and enforcing owner-or-admin rules
    data.py           # Database access layer for querying, updating, and deleting recipe rows

## Acceptance list (public API contract)
- POST /register → 201 on success, 400 on missing/invalid data, 409 if username/email taken
- POST /login → 200 on valid credentials with JWT token, 401 on invalid credentials
- GET /recipes → 200 with list of recipes (requires valid JWT)
- POST /recipes → 201 on success with created recipe, 400 on invalid data (requires valid JWT)
- GET /recipes/by-ingredient?ingredient=… → 200 with recipes filtered by ingredient (requires valid JWT)
- PATCH /recipes/<id> → 200 on owner/admin update, 403 if not owner/admin, 404 if not found
- DELETE /recipes/<id> → 204 on owner/admin delete, 403 if not owner/admin, 404 if not found

Total acceptance items: 7
