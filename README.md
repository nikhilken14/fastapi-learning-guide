# FastAPI Production Learning Guide 🚀

A comprehensive collection of production-ready FastAPI services, microservices patterns, and architectural implementations built with Python.

Each module in this repository is fully containerized and focuses on a specific production concern—ranging from ORM relationships and caching to event-driven architectures with Kafka and observability.

---

## 📂 Project Modules

| Module                       | Description                                                      | Core Tech Stack                            |
| :--------------------------- | :--------------------------------------------------------------- | :----------------------------------------- |
| **01-fastapi-basic**         | Basic FastAPI backend setup and containerization.                | FastAPI, Docker                            |
| **02-fastapi-restapi**       | Structured REST API ready for deployment.                        | FastAPI, Docker Compose                    |
| **03-fastapi-orm**           | Production-oriented Product & Order API with clean architecture. | FastAPI, SQLAlchemy, PostgreSQL, Docker    |
| **04-fastapi-jwt-auth**      | Secure authentication service with async DB support.             | FastAPI, SQLAlchemy (Async), PyJWT, Bcrypt |
| **05-fastapi-redis-caching** | Real-world Redis caching patterns and pooling.                   | FastAPI, Redis                             |
| **06-fastapi-rate-limiting** | Per-client request limiting using atomic Lua scripts.            | FastAPI, Redis (Lua)                       |
| **07-fastapi-graphql**       | Hybrid API layering Strawberry GraphQL side-by-side with REST.   | FastAPI, Strawberry GraphQL                |
| **08-event-driven-kafka**    | Asynchronous event streaming and message handling.               | FastAPI, Apache Kafka, aiokafka            |
| **09-fastapi-observability** | Real production-shaped metrics scraping and visualization.       | FastAPI, Prometheus, Grafana               |

---

## 🛠️ Running the Services

Navigate into any module directory to find its specific instructions and `docker-compose` setup:

```bash
cd 03-fastapi-orm
docker-compose up --build
```
