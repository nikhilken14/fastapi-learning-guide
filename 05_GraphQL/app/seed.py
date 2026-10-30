"""
app/seed.py
===========
Very small "in-memory database".

`Data` holds every Product, `SalesData` holds every Sells transaction.
Both are plain Python lists that live in process memory - restarting
the server wipes them and `seed_data()` repopulates them from scratch.

In a real application you would replace this module with a proper
database (Postgres, SQLite, etc.) and an ORM/query layer. Because
service.py only talks to `Data` / `SalesData` (never to files/DB
directly), swapping this out later is a localized change.
"""

from app.models import Product, Sells

# Global, process-wide "tables".
Data: list[Product] = []
SalesData: list[Sells] = []


def seed_data() -> None:
    """
    Populate `Data` and `SalesData` with sample records.

    Called once from the FastAPI `lifespan` handler in main.py when the
    application starts up, so the API has something to return without
    requiring a real database.

    Side effects:
        Appends to the module-level `Data` and `SalesData` lists.
        Calling this more than once will duplicate the seed rows, so it
        is only ever invoked a single time at startup.
    """
    Data.append(Product("101", "KeyBoard", "45"))
    Data.append(Product("103", "Computer", "165"))
    Data.append(Product("107", "Screen", "85"))
    Data.append(Product("108", "Mouse", "30"))

    SalesData.append(Sells(Data[0], 2))
    SalesData.append(Sells(Data[1], 3))
    SalesData.append(Sells(Data[2], 4))
    SalesData.append(Sells(Data[3], 5))

    SalesData.append(Sells(Data[0], 1))
    SalesData.append(Sells(Data[3], 3))
