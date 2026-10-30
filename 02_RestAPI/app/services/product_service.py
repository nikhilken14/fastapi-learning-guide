from app.models.product import Product
from app.repositories.product_repository import repository
from app.schemas.product import ProductCreate, ProductUpdate

class ProductNotFoundError(Exception):
    pass

class ProductService:
    def create(self, request: ProductCreate) -> Product:
        product = Product(
            id=repository.next_id(),
            name=request.name,
            description=request.description,
            price=request.price,
            stock=request.stock,
        )
        return repository.create(product)

    def get(self, product_id: int) -> Product:
        product = repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError()
        return product

    def list(self, page: int, limit: int):
        offset = (page - 1) * limit
        return repository.list(offset, limit)

    def update(self, product_id: int, request: ProductUpdate) -> Product:
        product = self.get(product_id)
        values = request.model_dump(exclude_unset=True)

        for field, value in values.items():
            setattr(product, field, value)

        return repository.update(product)

    def delete(self, product_id: int) -> None:
        self.get(product_id)
        repository.delete(product_id)

service = ProductService()
