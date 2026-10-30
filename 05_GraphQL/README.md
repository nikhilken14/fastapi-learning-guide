# GraphQL + FastAPI Product/Sales Service

This is your original FastAPI REST service (`Basic.zip`) converted to also serve
**GraphQL**, using [Strawberry](https://strawberry.rocks/) the most common,
type-hint-native GraphQL library for FastAPI. The original REST endpoints are kept
working side by side, so nothing that depended on them breaks.

Both REST and GraphQL sit on top of **the same business logic** (`app/service.py`),
so they can never drift out of sync with each other.

---

## 1. Project structure

```
graphql_project/
├── main.py                  # FastAPI app: mounts GraphQL + keeps old REST routes
├── requirements.txt
└── app/
    ├── models.py             # Product, Sells — plain domain classes
    ├── seed.py                # In-memory "database" + seed_data()
    ├── service.py             # Business logic (read + new write operations)
    └── schema/
        ├── __init__.py        # Builds the final strawberry.Schema
        ├── types.py           # GraphQL types: ProductType, SaleType, ProductSalesType
        ├── queries.py         # GraphQL Query root (all reads)
        └── mutations.py       # GraphQL Mutation root (all writes)
```

**Why this layout?** GraphQL projects tend to grow a `schema/` package quickly
(types, queries, mutations, and eventually subscriptions). Separating them from
`service.py` means the business logic has zero knowledge of GraphQL, and could be
reused by REST, GraphQL, a CLI, or a background job equally.

---

## 2. Setup & running

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open:

| URL                             | What it is                                    |
|----------------------------------|------------------------------------------------|
| `http://127.0.0.1:8000/graphql`  | **GraphiQL** — interactive GraphQL IDE in the browser |
| `http://127.0.0.1:8000/docs`     | Swagger UI for the original REST endpoints (unchanged) |

---

## 3. Module-by-module reference

### `app/models.py`
Framework-free domain classes, unaware of FastAPI or GraphQL.

- **`Product`** — one sellable item. Getters/setters: `getId`, `getName`,
  `getPrice`, `setId`, `setName`, `setPrice`. Identical API to your original
  `product.py` so nothing calling it needs to change.
- **`Sells`** — one sale transaction (a `Product` + a quantity). Automatically
  computes `Total = price * quantity` in `__init__` and again in `setQuantity`.

### `app/seed.py`
The "database" — two module-level lists, `Data` (products) and `SalesData` (sales).

- **`seed_data()`** — populates `Data`/`SalesData` with the same sample rows as
  your original project. Called once at startup from `main.py`'s `lifespan`.

### `app/service.py`
All business logic. Neither REST routes nor GraphQL resolvers touch `Data`/
`SalesData` directly — they always go through this module.

Kept from the original project (same behavior):
- `getList()` — all product names.
- `getTotalSales()` — sum of every sale's total.
- `getSalesByProduct()` — `{product_name: total_revenue}`.
- `getQuantityByProduct()` — `{product_name: total_quantity}`.

New, added to support GraphQL's richer query/mutation model:
- `getProducts()` — full `Product` objects (REST only ever exposed names).
- `getProductById(id)` — single product lookup, or `None`.
- `getAllSales()` — full `Sells` objects, each with its nested product.
- `addProduct(id, name, price)` — create a product; raises `ValueError` on duplicate id.
- `addSale(product_id, quantity)` — record a sale; raises `ValueError` if the
  product doesn't exist or quantity isn't positive.
- `updateProductPrice(product_id, new_price)` — change a product's price
  (does not retroactively change past sale totals).
- `deleteProduct(product_id)` — remove a product; returns `True`/`False`.

### `app/schema/types.py`
The public GraphQL "shape" of the data (separate from the internal domain classes
in `models.py`, so the API contract can evolve independently).

- **`ProductType`** — `id`, `name`, `price`. `from_model()` converts a `Product`.
- **`SaleType`** — `product` (nested `ProductType`), `quantity`, `total`.
  `from_model()` converts a `Sells`.
- **`ProductSalesType`** — `productName`, `totalRevenue`, `totalQuantity`. Used
  by the combined `salesByProduct` query described below.

### `app/schema/queries.py` — the `Query` root
Every field is read-only.

| GraphQL field       | Equivalent REST route     | Notes |
|----------------------|---------------------------|-------|
| `productNames`       | `GET /products/list`      | List of names only |
| `products`           | *(new)*                   | Full product objects |
| `product(id: "…")`   | *(new)*                   | Single product lookup |
| `sales`              | *(new)*                   | Every transaction, with nested product |
| `totalSales`         | `GET /sales/total`        | Grand total revenue |
| `salesByProduct`     | `GET /sales/by-product` + `GET /sales/quantity` | **Combines both** into one query — a client can get revenue *and* quantity per product in a single round trip, which is exactly the kind of over-fetching/under-fetching problem GraphQL is meant to solve. |

### `app/schema/mutations.py` — the `Mutation` root
The original project was 100% read-only. Mutations are the natural "next step"
for a GraphQL API:

- `addProduct(id, name, price)` → returns the new `ProductType`.
- `addSale(productId, quantity)` → returns the new `SaleType`.
- `updateProductPrice(productId, newPrice)` → returns the updated `ProductType`.
- `deleteProduct(productId)` → returns `Boolean`.

Validation errors from the service layer (e.g. unknown product id) are raised as
`GraphQLError`, which GraphQL surfaces cleanly in the response's `errors` array
instead of a raw 500.

### `app/schema/__init__.py`
Combines `Query` and `Mutation` into the single `strawberry.Schema` object that
`main.py` mounts.

### `main.py`
- `lifespan()` — unchanged from your original: seeds data on startup.
- `GraphQLRouter(schema, graphql_ide="graphiql")` mounted at `/graphql` —
  handles GraphQL queries & mutations over HTTP, and serves the GraphiQL IDE
  when opened in a browser.
- All original REST routes (`/`, `/products/list`, `/sales/total`,
  `/sales/by-product`, `/sales/quantity`, `/health`) kept exactly as-is.

---

## 4. Example GraphQL operations

**Query — products + combined sales stats:**
```graphql
query {
  products { id name price }
  salesByProduct {
    productName
    totalRevenue
    totalQuantity
  }
}
```

**Query — single product:**
```graphql
query {
  product(id: "101") { id name price }
}
```

**Mutation — add a product, then sell it:**
```graphql
mutation {
  addProduct(id: "110", name: "Webcam", price: 55.0) {
    id name price
  }
  addSale(productId: "110", quantity: 2) {
    quantity
    total
    product { name }
  }
}
```

---

## 5. Ideas to extend this further

- **Pagination** on `products`/`sales` (Strawberry has built-in Relay-style connections).
- **DataLoader** (via `strawberry.dataloader.DataLoader`) once you move to a real
  database, to batch/cache lookups and avoid N+1 queries on nested fields like
  `SaleType.product`.
- **A real database** (Postgres/SQLite + SQLAlchemy) in place of the `Data`/
  `SalesData` lists in `seed.py` — `service.py` is already the single choke point,
  so this becomes a fairly contained change.
- **Input types** (`@strawberry.input`) for mutations instead of many loose
  arguments, e.g. `addProduct(input: ProductInput!)`.
- **Subscriptions** for real-time updates, e.g. push a notification every time
  `addSale` is called — Strawberry's `GraphQLRouter` already supports the
  `graphql-ws` protocol needed for this.
- **Auth** — add a `context_getter` to `GraphQLRouter` to inject the current
  user into `info.context`, then guard mutations like `deleteProduct`.
