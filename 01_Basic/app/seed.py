from app.product import Product
from app.sells import Sells

Data = []
SalesData = []

def seed_data():
    

    Data.append(Product("101","KeyBoard","45"))
    Data.append(Product("103","Computer","165"))
    Data.append(Product("107","Screen","85"))
    Data.append(Product("108","Mouse","30"))

    

    SalesData.append(Sells(Data[0], 2))
    SalesData.append(Sells(Data[1], 3))
    SalesData.append(Sells(Data[2], 4))
    SalesData.append(Sells(Data[3], 5))

    SalesData.append(Sells(Data[0], 1))
    SalesData.append(Sells(Data[3], 3))