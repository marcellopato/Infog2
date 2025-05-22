import pytest
from fastapi import status
from datetime import datetime

@pytest.fixture
def test_products_for_search(test_db):
    from app.models.product import Product
    products = [
        Product(name="Camisa Azul", description="Camisa", price=50.00, stock=10),
        Product(name="Calça Jeans", description="Calça", price=100.00, stock=5),
        Product(name="Tênis Nike", description="Tênis", price=200.00, stock=3)
    ]
    for p in products:
        test_db.add(p)
    test_db.commit()
    return products

def test_search_products(client, test_products_for_search):
    response = client.get("/search/products?query=Camisa&min_price=40&max_price=60")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Camisa Azul"

def test_search_products_by_price_range(client, test_products_for_search):
    response = client.get("/search/products?min_price=150")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Tênis Nike"

def test_search_products_pagination(client, test_products_for_search):
    response = client.get("/search/products?per_page=2&page=1")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
