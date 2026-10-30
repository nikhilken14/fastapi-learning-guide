"""
app/schema/queries.py
======================
GraphQL `Query` root type - every read-only operation exposed by the API.

Each method below becomes a queryable field in GraphQL. For example,
`products` here can be called from a client like:

    query {
      products { id name price }
    }

Every resolver simply calls into app/service.py and converts the result
into a GraphQL type from app/schema/types.py - no business logic lives
here, only translation between the service layer and the GraphQL layer.
"""

from __future__ import annotations

import strawberry

from app import service
from app.schema.types import ProductType, SaleType, ProductSalesType


@strawberry.type
class Query:
    """Root GraphQL Query type. All fields here are read-only."""

    @strawberry.field(description="List the names of all products (matches the original REST /products/list).")
    def product_names(self) -> list[str]:
        """Resolver for `productNames`.

        Returns:
            A list of product name strings.
        """
        return service.getList()

    @strawberry.field(description="Return full details (id, name, price) for every product.")
    def products(self) -> list[ProductType]:
        """Resolver for `products`.

        Returns:
            A list of ProductType, one per product in the catalogue.
        """
        return [ProductType.from_model(p) for p in service.getProducts()]

    @strawberry.field(description="Look up a single product by its id. Returns null if not found.")
    def product(self, id: str) -> ProductType | None:
        """Resolver for `product(id: ...)`.

        Args:
            id: The product id to search for.

        Returns:
            The matching ProductType, or None if no such product exists.
        """
        product = service.getProductById(id)
        return ProductType.from_model(product) if product else None

    @strawberry.field(description="Return every individual sale transaction, with nested product details.")
    def sales(self) -> list[SaleType]:
        """Resolver for `sales`.

        Returns:
            A list of SaleType, one per recorded transaction.
        """
        return [SaleType.from_model(s) for s in service.getAllSales()]

    @strawberry.field(description="Sum of every sale's total value (matches the original REST /sales/total).")
    def total_sales(self) -> float:
        """Resolver for `totalSales`.

        Returns:
            The grand total revenue across all sales.
        """
        return service.getTotalSales()

    @strawberry.field(description="Revenue and quantity sold, grouped per product.")
    def sales_by_product(self) -> list[ProductSalesType]:
        """Resolver for `salesByProduct`.

        Combines the original `getSalesByProduct` and `getQuantityByProduct`
        service functions into a single, richer GraphQL query so clients
        can fetch both revenue and quantity per product in one round trip
        (a GraphQL-native improvement over the two separate REST endpoints).

        Returns:
            A list of ProductSalesType, one entry per product that has sales.
        """
        revenue_by_product = service.getSalesByProduct()
        quantity_by_product = service.getQuantityByProduct()

        return [
            ProductSalesType(
                productName=name,
                totalRevenue=revenue_by_product.get(name, 0.0),
                totalQuantity=quantity_by_product.get(name, 0),
            )
            for name in revenue_by_product.keys()
        ]
