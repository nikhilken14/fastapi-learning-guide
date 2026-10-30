# Module 2 — Production-Oriented FastAPI REST API

## Goal

Build a small Product Management REST API while learning the structure and engineering practices used in larger FastAPI applications.

## Architecture

Client
  -> FastAPI Router
  -> Service Layer
  -> Repository Layer
  -> In-memory data store

This first project intentionally avoids PostgreSQL. The ORM/database layer is introduced in Mini Project 2.

## Features

- FastAPI
- REST API
- API versioning
- Pydantic request/response validation
- Service layer
- Repository layer
- Pagination
- Centralized exception handling
- Health endpoint
- Environment-based configuration
- Logging
- Unit/API tests
- Docker

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:
- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health: http://127.0.0.1:8000/health

## Run tests

```bash
pytest
```

## Run with Docker

```bash
docker compose up --build
```

## Endpoints

POST   /api/v1/products
GET    /api/v1/products
GET    /api/v1/products/{product_id}
PUT    /api/v1/products/{product_id}
DELETE /api/v1/products/{product_id}
GET    /health

## Example create request

```json
{
  "name": "Keyboard",
  "description": "Mechanical keyboard",
  "price": 2500,
  "stock": 10
}
```

## Production lessons

1. Keep HTTP concerns in routers.
2. Keep business rules in services.
3. Keep persistence concerns in repositories.
4. Validate input at the API boundary.
5. Never return unbounded database results in a real application.
6. Have a health endpoint.
7. Separate configuration from source code.
8. Test failure cases, not only successful requests.
9. Version public APIs.
10. Add observability before the system becomes difficult to debug.

