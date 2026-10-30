"""
app/schema/__init__.py
=======================
Builds the final Strawberry `Schema` object by combining the Query and
Mutation root types. This is the object main.py mounts onto FastAPI.

Import this module's `schema` wherever you need to reference the
GraphQL schema (e.g. in main.py, or in tests).
"""

import strawberry

from app.schema.queries import Query
from app.schema.mutations import Mutation

# The complete GraphQL schema: every readable field comes from Query,
# every writable operation comes from Mutation.
schema = strawberry.Schema(query=Query, mutation=Mutation)
