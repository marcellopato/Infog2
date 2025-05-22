import pytest
from fastapi import status
from datetime import datetime
from app.models.product import Product
from app.models.category import Category

@pytest.fixture
def test_search_data(test_db):
    # Criar categoria
    category = Category(name="Roupas", description="Categoria de roupas")
    test_db.add(category)
    test_db.commit()
    
    # Criar produtos para teste
    products = [
        Product(name="Camisa Azul", price=79.90, stock=10, category_id=category.id),
        Product(name="Calça Jeans", price=159.90, stock=5, category_id=category.id),
        Product(name="Tênis Nike", price=299.90, stock=3, category_id=category.id)
    ]
    for p in products:
        test_db.add(p)
    test_db.commit()
    return {"products": products, "category": category}

def test_basic_search(client, test_search_data):
    response = client.get("/search/products")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3

@pytest.fixture
def test_search_products(test_db):
    # Criar categoria
    category = Category(name="Roupas", description="Categoria de roupas")
    test_db.add(category)
    test_db.commit()
    
    # Criar produtos para teste
    products = [
        Product(
            name="Camisa Azul",
            description="Camisa casual",
            price=79.90,
            stock=10,
            category_id=category.id
        ),
        Product(
            name="Calça Jeans",
            description="Calça casual",
            price=159.90,
            stock=5,
            category_id=category.id
        ),
        Product(
            name="Tênis Nike",
            description="Tênis esportivo",
            price=299.90,
            stock=3,
            category_id=category.id
        )
    ]
    for p in products:
        test_db.add(p)
    test_db.commit()
    return {"products": products, "category": category}

def test_search_by_name(client, test_search_products):
    response = client.get("/search/products?query=Camisa")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert "Camisa" in response.json()[0]["name"]

def test_search_by_price_range(client, test_search_products):
    response = client.get("/search/products?min_price=100&max_price=200")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Calça Jeans"

def test_search_with_pagination(client, test_search_products):
    response = client.get("/search/products?per_page=2&page=1")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2

def test_search_by_category(client, test_search_products):
    response = client.get(f"/search/products?category_id={test_search_products['category'].id}")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3

def test_search_with_sorting(client, test_search_products):
    # Ordenar por preço descendente
    response = client.get("/search/products?order_by=price&order=desc")
    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert results[0]["price"] > results[1]["price"]

def test_search_invalid_params(client):
    response = client.get("/search/products?page=0")  # página inválida
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
