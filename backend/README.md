# HomiQ Backend

This backend provides the core API foundation for the HomiQ platform with modular FastAPI services, SQLAlchemy models, and JWT-based authentication.

## Structure

- app/api: REST routers
- app/core: application configuration and shared utilities
- app/crud: repository-style CRUD implementations
- app/models: SQLAlchemy entities
- app/schemas: request and response models
- app/security: authentication and password helpers
- app/services: business logic services

## Getting Started

1. Create a virtual environment
2. Install requirements: pip install -r requirements.txt
3. Start the app: uvicorn app.main:app --reload

## Notes

The initial module includes:
- FastAPI app bootstrap
- PostgreSQL/SQLAlchemy setup
- Auth registration and login endpoints
- JWT token generation and refresh flow
