from app.models.product import Product

class ProductRepository:
    def __init__(self):
        self._products: dict[int, Product] = {}
        self._next_id = 1

    def create(self, product: Product) -> Product:
        self._products[product.id] = product
        self._next_id = max(self._next_id, product.id + 1)
        return product

    def next_id(self) -> int:
        product_id = self._next_id
        self._next_id += 1
        return product_id

    def get_by_id(self, product_id: int) -> Product | None:
        return self._products.get(product_id)

    def list(self, offset: int, limit: int) -> tuple[list[Product], int]:
        products = list(self._products.values())
        return products[offset:offset + limit], len(products)

    def update(self, product: Product) -> Product:
        self._products[product.id] = product
        return product

    def delete(self, product_id: int) -> bool:
        return self._products.pop(product_id, None) is not None

repository = ProductRepository()
