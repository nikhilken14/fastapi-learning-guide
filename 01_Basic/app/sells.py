from app.product import Product


class Sells:

    def __init__(self, product, quantity):
        self.Product = product
        self.Quantity = quantity
        self.Total = float(product.getPrice()) * quantity

    def getProduct(self):
        return self.Product

    def getQuantity(self):
        return self.Quantity

    def getTotal(self):
        return self.Total

    def setQuantity(self, quantity):
        self.Quantity = quantity
        self.Total = float(self.Product.getPrice()) * quantity