# Mini Project 1 — FastAPI Production REST API

## 1. Real-world scenario

A company needs a Product Management API used by web applications, mobile applications, and internal services.

The API must expose stable endpoints, validate requests, handle errors consistently, support pagination, and be easy to test and deploy.

## 2. Request flow

POST /api/v1/products
        |
        v
FastAPI Router
        |
        v
Pydantic validation
        |
        v
Product Service
        |
        v
Product Repository
        |
        v
Data Store

The router should not contain business logic. The service owns business behavior. The repository owns persistence behavior.

## 3. Why these layers?

### Router
Responsible for HTTP concerns:
- URL
- HTTP method
- status code
- request/response models

### Service
Responsible for business rules:
- create product
- update product
- retrieve product
- delete product

### Repository
Responsible for data access:
- create
- read
- update
- delete

This separation makes the application easier to test and allows the persistence technology to change later.

## 4. API design

### Create
POST /api/v1/products

Returns HTTP 201.

### List
GET /api/v1/products?page=1&limit=20

Pagination prevents the API from attempting to return an unbounded amount of data.

### Get
GET /api/v1/products/{product_id}

Returns 404 when the product does not exist.

### Update
PUT /api/v1/products/{product_id}

### Delete
DELETE /api/v1/products/{product_id}

Returns HTTP 204 when deletion succeeds.

## 5. Validation

Pydantic rejects invalid input before it reaches business logic.

Examples:
- name shorter than 2 characters
- price <= 0
- stock < 0
- page < 1
- limit > 100

The API boundary should be strict because bad data becomes much harder to correct after it enters the system.

## 6. Error handling

Known business errors are converted into appropriate HTTP errors.

Unexpected errors are converted into a generic 500 response.

In a real production system, the detailed exception must be logged internally while the client should not receive stack traces or secrets.

## 7. Configuration

Configuration is loaded from environment variables.

Never hard-code:
- passwords
- API keys
- database credentials
- environment-specific URLs

Later projects will add database, Redis, Kafka, and security configuration.

## 8. Testing strategy

Tests included:
- successful product creation
- missing product
- request validation

A production application should add:
- update tests
- delete tests
- pagination tests
- repository tests
- service tests
- API integration tests
- authentication tests
- performance tests

## 9. Development vs production

Development:

uvicorn app.main:app --reload

Production:

Use multiple worker processes or multiple application instances behind a load balancer, depending on the deployment architecture.

Do not treat --reload as a production setting.

## 10. What is intentionally missing?

The application does not yet use PostgreSQL.

This is deliberate.

The learning progression is:

Project 1:
FastAPI + REST

Project 2:
FastAPI + PostgreSQL + SQLAlchemy

Project 3:
JWT + OAuth2

Project 4:
GraphQL

Project 5:
Redis

Project 6:
Rate limiting

Project 7:
Kafka

Project 8:
Prometheus + Grafana

Project 9:
Load balancing

Project 10:
Complete production system

## 11. New joiner checklist

- Understand FastAPI routing.
- Understand request validation.
- Understand response models.
- Understand HTTP status codes.
- Understand dependency/layer separation.
- Understand service vs repository responsibilities.
- Understand API versioning.
- Understand pagination.
- Understand centralized error handling.
- Understand health endpoints.
- Understand environment configuration.
- Run the API locally.
- Run tests.
- Run the API with Docker.
- Explain why this implementation is not yet production-complete.

## 12. Interview questions

1. Why should business logic not be placed directly in FastAPI routes?
2. What is Pydantic doing here?
3. Why use response models?
4. Why return 201 for creation?
5. When would you use 400 vs 404 vs 409 vs 422?
6. Why is pagination necessary?
7. What happens to the data when the application restarts?
8. Why is in-memory storage unsuitable for multiple API instances?
9. Why do we need environment variables?
10. What should a health endpoint check?
11. What is the difference between unit and integration testing?
12. Why should production APIs avoid returning internal exception details?
13. Why version an API?
14. What changes when PostgreSQL is introduced?
15. What changes when we run three FastAPI instances?

## 13. Expected outcome

After completing this project, a new joiner should be able to build a clean FastAPI REST API and explain the basic production structure.

They should also understand that the current implementation is intentionally incomplete.

The next problem is persistence.

That is exactly what Mini Project 2 solves:
FastAPI + PostgreSQL + SQLAlchemy ORM + migrations + transactions + connection pooling.
