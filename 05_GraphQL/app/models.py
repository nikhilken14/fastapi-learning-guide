"""
app/models.py
=============
Plain Python domain classes for the application.

These are intentionally kept *framework free* - they know nothing about
FastAPI or GraphQL. Strawberry-GraphQL types (see app/schema/types.py)
wrap these objects and expose only the fields we want in the API.

Keeping domain logic separate from the GraphQL layer means:
  * You can unit test `Product` / `Sells` without spinning up a server.
  * You could swap GraphQL for REST (or add both, as this project does)
    without touching the business logic.
"""

from __future__ import annotations


class Product:
    """
    Represents a single sellable product.

    This mirrors the original `product.py` class from the REST version,
    with the same getter/setter API so existing code (service.py, sells.py)
    keeps working unmodified.

    Attributes:
        PId (str): Unique product identifier (e.g. "101").
        PName (str): Human readable product name (e.g. "KeyBoard").
        Price (str | float): Unit price of the product.
    """

    def __init__(self, Id: str, Name: str, Price: str | float):
        """Create a new Product.

        Args:
            Id: Unique identifier for the product.
            Name: Display name of the product.
            Price: Unit price (stored as given; converted to float when needed).
        """
        self.PId = Id
        self.PName = Name
        self.Price = Price

    def getId(self) -> str:
        """Return the product's unique identifier."""
        return self.PId

    def getName(self) -> str:
        """Return the product's display name."""
        return self.PName

    def getPrice(self) -> str | float:
        """Return the product's unit price."""
        return self.Price

    def setId(self, Id: str) -> None:
        """Update the product's identifier."""
        self.PId = Id

    def setName(self, Name: str) -> None:
        """Update the product's display name."""
        self.PName = Name

    def setPrice(self, Price: str | float) -> None:
        """Update the product's unit price."""
        self.Price = Price


class Sells:
    """
    Represents a single sale transaction: one product sold in some quantity.

    The total price is computed automatically whenever the quantity is set
    (either at construction time or via `setQuantity`).

    Attributes:
        Product (Product): The product that was sold.
        Quantity (int): How many units were sold.
        Total (float): Quantity * unit price, computed automatically.
    """

    def __init__(self, product: Product, quantity: int):
        """Create a new Sells record.

        Args:
            product: The Product instance that was sold.
            quantity: Number of units sold.
        """
        self.Product = product
        self.Quantity = quantity
        self.Total = float(product.getPrice()) * quantity

    def getProduct(self) -> Product:
        """Return the Product associated with this sale."""
        return self.Product

    def getQuantity(self) -> int:
        """Return the quantity sold in this transaction."""
        return self.Quantity

    def getTotal(self) -> float:
        """Return the total value (price * quantity) of this sale."""
        return self.Total

    def setQuantity(self, quantity: int) -> None:
        """Update the quantity sold and recompute the total automatically.

        Args:
            quantity: The new quantity for this sale.
        """
        self.Quantity = quantity
        self.Total = float(self.Product.getPrice()) * quantity
