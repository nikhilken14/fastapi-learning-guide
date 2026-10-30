"""
app/service.py
==============
Business logic layer.

This module is the single place that reads/writes `Data` and
`SalesData` (from app/seed.py). Both the REST routes (main.py) and the
GraphQL resolvers (app/schema/queries.py, app/schema/mutations.py)
call into these functions - neither layer talks to the in-memory
"database" directly. That keeps GraphQL and REST perfectly in sync and
means business rules only need to be written once.

Functions kept from the original project:
    getList, getTotalSales, getSalesByProduct, getQuantityByProduct

New functions added to support GraphQL mutations / richer queries:
    getProducts, getProductById, getAllSales,
    addProduct, addSale, updateProductPrice, deleteProduct
"""

from __future__ import annotations

from app.models import Product, Sells
from app.seed import Data, SalesData


# ---------------------------------------------------------------------------
# Existing read-only queries (unchanged behaviour from the REST version)
# ---------------------------------------------------------------------------

def getList() -> list[str]:
    """Return the name of every product currently in stock.

    Returns:
        A list of product name strings, e.g. ["KeyBoard", "Computer"].
    """
    li = []
    for pro in Data:
        li.append(pro.getName())
    return li


def getTotalSales() -> float:
    """Sum the `Total` of every sale ever recorded.

    Returns:
        The grand total revenue across all sales, as a float.
    """
    total = 0
    for sale in SalesData:
        total += sale.getTotal()
    return total


def getSalesByProduct() -> dict[str, float]:
    """Aggregate total revenue, grouped by product name.

    Returns:
        A dict mapping product name -> summed revenue for that product,
        e.g. {"KeyBoard": 135.0, "Computer": 495.0}.
    """
    result: dict[str, float] = {}
    for sale in SalesData:
        productName = sale.getProduct().getName()
        total = sale.getTotal()
        if productName not in result:
            result[productName] = 0
        result[productName] += total
    return result


def getQuantityByProduct() -> dict[str, int]:
    """Aggregate total units sold, grouped by product name.

    Returns:
        A dict mapping product name -> summed quantity sold,
        e.g. {"KeyBoard": 3, "Computer": 3}.
    """
    result: dict[str, int] = {}
    for sale in SalesData:
        productName = sale.getProduct().getName()
        quantity = sale.getQuantity()
        if productName not in result:
            result[productName] = 0
        result[productName] += quantity
    return result


# ---------------------------------------------------------------------------
# New helper queries - useful once we expose full objects over GraphQL
# (the REST version only ever returned product *names*, never full records)
# ---------------------------------------------------------------------------

def getProducts() -> list[Product]:
    """Return every Product object (not just names).

    Returns:
        The full list of Product instances currently seeded/created.
    """
    return Data


def getProductById(product_id: str) -> Product | None:
    """Look up a single product by its id.

    Args:
        product_id: The Product id to search for (e.g. "101").

    Returns:
        The matching Product, or None if no product has that id.
    """
    for pro in Data:
        if pro.getId() == product_id:
            return pro
    return None


def getAllSales() -> list[Sells]:
    """Return every recorded sale as full Sells objects.

    Returns:
        The full list of Sells instances (product + quantity + total).
    """
    return SalesData


# ---------------------------------------------------------------------------
# New write operations - these back the GraphQL *mutations*.
# The original project was read-only; GraphQL APIs are expected to support
# mutations, so these are the natural "next things to add" the user asked for.
# ---------------------------------------------------------------------------

def addProduct(product_id: str, name: str, price: float) -> Product:
    """Create a new product and add it to the in-memory catalogue.

    Args:
        product_id: Unique id for the new product. Must not already exist.
        name: Display name for the product.
        price: Unit price for the product.

    Returns:
        The newly created Product instance.

    Raises:
        ValueError: If a product with `product_id` already exists.
    """
    if getProductById(product_id) is not None:
        raise ValueError(f"Product with id '{product_id}' already exists")

    product = Product(product_id, name, price)
    Data.append(product)
    return product


def addSale(product_id: str, quantity: int) -> Sells:
    """Record a new sale for an existing product.

    Args:
        product_id: Id of the product being sold.
        quantity: Number of units sold.

    Returns:
        The newly created Sells instance.

    Raises:
        ValueError: If no product with `product_id` exists, or quantity <= 0.
    """
    if quantity <= 0:
        raise ValueError("quantity must be a positive integer")

    product = getProductById(product_id)
    if product is None:
        raise ValueError(f"No product found with id '{product_id}'")

    sale = Sells(product, quantity)
    SalesData.append(sale)
    return sale


def updateProductPrice(product_id: str, new_price: float) -> Product:
    """Update the price of an existing product.

    Note: this does NOT retroactively change the `Total` of past sales -
    matching real-world behaviour where a price change only affects
    future transactions.

    Args:
        product_id: Id of the product to update.
        new_price: The new unit price.

    Returns:
        The updated Product instance.

    Raises:
        ValueError: If no product with `product_id` exists.
    """
    product = getProductById(product_id)
    if product is None:
        raise ValueError(f"No product found with id '{product_id}'")

    product.setPrice(new_price)
    return product


def deleteProduct(product_id: str) -> bool:
    """Remove a product from the catalogue.

    Args:
        product_id: Id of the product to delete.

    Returns:
        True if a product was found and removed, False otherwise.

    Note:
        Existing Sells records referencing this product are left as-is,
        so historical sales figures are preserved.
    """
    product = getProductById(product_id)
    if product is None:
        return False
    Data.remove(product)
    return True
