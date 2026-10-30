"""
app/schema/mutations.py
========================
GraphQL `Mutation` root type - every write operation exposed by the API.

The original REST project was entirely read-only (GET endpoints only).
A real GraphQL API is expected to support mutations too, so this module
adds the natural next step: creating products, recording sales, and
updating/removing products. Each mutation delegates to app/service.py
and simply translates errors into a `GraphQLError`.

Example client usage:

    mutation {
      addProduct(id: "110", name: "Webcam", price: 55.0) {
        id
        name
        price
      }
    }
"""

from __future__ import annotations

import strawberry
from strawberry.exceptions import GraphQLError

from app import service
from app.schema.types import ProductType, SaleType


@strawberry.type
class Mutation:
    """Root GraphQL Mutation type. All fields here perform a write."""

    @strawberry.mutation(description="Add a new product to the catalogue.")
    def add_product(self, id: str, name: str, price: float) -> ProductType:
        """Resolver for `addProduct(id, name, price)`.

        Args:
            id: Unique id for the new product.
            name: Display name for the new product.
            price: Unit price for the new product.

        Returns:
            The newly created product, as a ProductType.

        Raises:
            GraphQLError: If a product with this id already exists.
        """
        try:
            product = service.addProduct(id, name, price)
        except ValueError as exc:
            raise GraphQLError(str(exc))
        return ProductType.from_model(product)

    @strawberry.mutation(description="Record a new sale of an existing product.")
    def add_sale(self, product_id: str, quantity: int) -> SaleType:
        """Resolver for `addSale(productId, quantity)`.

        Args:
            product_id: Id of the product being sold.
            quantity: Number of units sold (must be positive).

        Returns:
            The newly created sale, as a SaleType.

        Raises:
            GraphQLError: If the product doesn't exist or quantity is invalid.
        """
        try:
            sale = service.addSale(product_id, quantity)
        except ValueError as exc:
            raise GraphQLError(str(exc))
        return SaleType.from_model(sale)

    @strawberry.mutation(description="Update the unit price of an existing product.")
    def update_product_price(self, product_id: str, new_price: float) -> ProductType:
        """Resolver for `updateProductPrice(productId, newPrice)`.

        Args:
            product_id: Id of the product to update.
            new_price: The new unit price to set.

        Returns:
            The updated product, as a ProductType.

        Raises:
            GraphQLError: If no product with `product_id` exists.
        """
        try:
            product = service.updateProductPrice(product_id, new_price)
        except ValueError as exc:
            raise GraphQLError(str(exc))
        return ProductType.from_model(product)

    @strawberry.mutation(description="Delete a product from the catalogue by id.")
    def delete_product(self, product_id: str) -> bool:
        """Resolver for `deleteProduct(productId)`.

        Args:
            product_id: Id of the product to delete.

        Returns:
            True if the product existed and was deleted, False otherwise.
        """
        return service.deleteProduct(product_id)
