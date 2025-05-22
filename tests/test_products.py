import pytest
from fastapi import status
from app.models.product import Product
from app.models.user import User

@pytest.fixture
def admin_token(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "admin@test.com",
            "username": "admin_test",
            "password": "admin123",
            "is_admin": True
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def test_product(test_db):
    product = Product(
        name="Test Product",
        description="Test Description",
        price=99.99,
        stock=10
    )
    test_db.add(product)
    test_db.commit()
    return product  # Retorna o produto sem refresh

def test_create_product(client, admin_token):
    response = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "New Product",
            "description": "Product Description",
            "price": 29.99,
            "stock": 50
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "New Product"

def test_create_product_no_admin(client):
    user_response = client.post(
        "/auth/register",
        json={
            "email": "user@test.com",
            "username": "normal_user",
            "password": "test123"
        }
    )
    token = user_response.json()["access_token"]
    
    response = client.post(
        "/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "New Product",
            "price": 29.99,
            "stock": 50
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_list_products(client, test_product):
    response = client.get("/products/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0
    assert response.json()[0]["name"] == test_product.name

def test_get_product(client, test_product):
    response = client.get(f"/products/{test_product.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == test_product.name

def test_update_product(client, admin_token, test_db, test_product):
    # Adiciona produto à sessão atual
    product = test_db.merge(test_product)
    
    response = client.patch(
        f"/products/{product.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"price": 199.99}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["price"] == 199.99

def test_delete_product(client, admin_token, test_db, test_product):
    # Garantir que o produto está na sessão atual
    product_id = test_product.id
    
    # Deletar produto
    response = client.delete(
        f"/products/{product_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Buscar produto novamente e verificar se está inativo
    updated_product = test_db.query(Product).filter(Product.id == product_id).first()
    assert not updated_product.is_active

    # Confirmar que não aparece na listagem
    list_response = client.get("/products/")
    assert product_id not in [p["id"] for p in list_response.json()]
