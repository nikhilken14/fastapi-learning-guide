"""
app/schema/types.py
====================
Strawberry GraphQL type definitions.

These classes describe the *shape* of data that GraphQL clients can
query - they are the GraphQL equivalent of Pydantic response models in
REST/FastAPI. Each `@strawberry.type` becomes a `type` in the GraphQL
schema (visible at /graphql via GraphiQL introspection).

We keep these separate from app/models.py on purpose:
    app/models.py     -> internal domain objects (Product, Sells)
    app/schema/types.py -> external API contract (ProductType, SaleType, ...)

This separation means you can change internal representations without
breaking the public GraphQL schema, and vice versa.
"""

from __future__ import annotations

import strawberry

from app.models import Product, Sells


@strawberry.type
class ProductType:
    """GraphQL representation of a Product.

    Fields:
        id: Unique product identifier.
        name: Product display name.
        price: Unit price of the product.
    """

    id: str
    name: str
    price: float

    @staticmethod
    def from_model(product: Product) -> "ProductType":
        """Build a ProductType from an internal `Product` domain object.

        Args:
            product: The domain object to convert.

        Returns:
            An equivalent ProductType for use in GraphQL responses.
        """
        return ProductType(
            id=product.getId(),
            name=product.getName(),
            price=float(product.getPrice()),
        )


@strawberry.type
class SaleType:
    """GraphQL representation of a single sale (Sells) transaction.

    Fields:
        product: The product that was sold (nested ProductType).
        quantity: Number of units sold.
        total: Total value of this sale (price * quantity).
    """

    product: ProductType
    quantity: int
    total: float

    @staticmethod
    def from_model(sale: Sells) -> "SaleType":
        """Build a SaleType from an internal `Sells` domain object.

        Args:
            sale: The domain object to convert.

        Returns:
            An equivalent SaleType for use in GraphQL responses.
        """
        return SaleType(
            product=ProductType.from_model(sale.getProduct()),
            quantity=sale.getQuantity(),
            total=sale.getTotal(),
        )


@strawberry.type
class ProductSalesType:
    """Aggregated sales figures for one product.

    Used for the `salesByProduct` / `quantityByProduct` style queries,
    where results are grouped per product name rather than per
    individual transaction.

    Fields:
        productName: Name of the product these totals belong to.
        totalRevenue: Sum of all sale totals for this product.
        totalQuantity: Sum of all quantities sold for this product.
    """

    productName: str
    totalRevenue: float
    totalQuantity: int
