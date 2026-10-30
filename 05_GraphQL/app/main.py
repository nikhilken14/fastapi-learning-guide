"""
This wires everything together:
    1. Seeds the in-memory data on startup (via `lifespan`, unchanged
       from the original project).
    2. Mounts the GraphQL API at POST/GET /graphql using Strawberry's
       `GraphQLRouter`. Visiting /graphql in a browser opens GraphiQL,
       an interactive in-browser client for exploring the schema.
    3. Keeps every original REST endpoint working exactly as before,
       so existing REST consumers are not broken by this change. This
       means the same business logic (app/service.py) is now reachable
       over BOTH REST and GraphQL at the same time.

    http://127.0.0.1:8000/graphql   -> GraphQL playground (GraphiQL)
    http://127.0.0.1:8000/docs      -> REST Swagger docs (unchanged)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app.schema import schema
from app.seed import seed_data
from app.service import (
    getList,
    getTotalSales,
    getSalesByProduct,
    getQuantityByProduct,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler.

    Runs once when the app starts (before the `yield`) and once when it
    shuts down (after the `yield`). Used here to populate the in-memory
    "database" so both REST and GraphQL have data to serve immediately.
    """
    print("Starting application...")
    print("Loading seed data...")

    seed_data()

    print("Seed data loaded successfully")

    yield

    print("Application shutting down...")


app = FastAPI(
    title="Simple Product Service",
    version="2.0.0",
    lifespan=lifespan,
)

graphql_app = GraphQLRouter(schema, graphql_ide="graphiql")
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def homepage():
    return {"status" : "backend is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "api-service"}