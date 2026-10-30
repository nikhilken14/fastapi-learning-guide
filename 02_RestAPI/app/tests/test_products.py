from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_product():
    response = client.post(
        "/api/v1/products",
        json={
            "name": "Keyboard",
            "description": "Mechanical keyboard",
            "price": 2500,
            "stock": 10,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Keyboard"
    assert body["price"] == 2500

def test_get_missing_product():
    response = client.get("/api/v1/products/99999")
    assert response.status_code == 404

def test_validation():
    response = client.post(
        "/api/v1/products",
        json={"name": "A", "price": -10, "stock": -1},
    )
    assert response.status_code == 422
