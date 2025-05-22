import pytest
from fastapi import status
from app.models.order import Order, OrderStatus
from app.models.product import Product

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
    test_db.refresh(product)
    return product

def test_create_order(client, admin_token, test_product):
    response = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "items": [
                {
                    "product_id": test_product.id,
                    "quantity": 2
                }
            ]
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["total"] == test_product.price * 2
    assert len(response.json()["items"]) == 1

def test_create_order_insufficient_stock(client, admin_token, test_product):
    response = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "items": [
                {
                    "product_id": test_product.id,
                    "quantity": 999
                }
            ]
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Estoque insuficiente" in response.json()["detail"]

def test_list_orders(client, admin_token):
    response = client.get(
        "/orders/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_cancel_order(client, admin_token, test_db, test_product):
    # Criar pedido
    order_response = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "items": [
                {
                    "product_id": test_product.id,
                    "quantity": 1
                }
            ]
        }
    )
    order_id = order_response.json()["id"]
    
    # Cancelar pedido
    response = client.patch(
        f"/orders/{order_id}/cancel",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Verificar estoque restaurado
    product = test_db.query(Product).filter(Product.id == test_product.id).first()
    assert product.stock == test_product.stock
