from dataclasses import dataclass

@dataclass
class Product:
    id: int
    name: str
    description: str | None
    price: float
    stock: int
