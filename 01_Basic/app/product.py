class Product:

    def __init__(self,Id,Name,Price):
        self.PId = Id
        self.PName = Name
        self.Price = Price

    def getId(self):
        return self.PId

    def getName(self):
        return self.PName

    def getPrice(self):
        return self.Price

    def setId(self,Id):
        self.PId = Id

    def setName(self,Name):
        self.PName = Name

    def setPrice(self,Price):
        self.Price = Price