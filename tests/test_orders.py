import pytest
from fastapi import status
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.order_item import OrderItem

@pytest.fixture
def admin_token(client):
    # Criar usuário admin
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
def test_products(test_db):
    products = [
        Product(name="Produto 1", description="Desc 1", price=100.00, stock=10),
        Product(name="Produto 2", description="Desc 2", price=200.00, stock=5)
    ]
    for p in products:
        test_db.add(p)
    test_db.commit()
    return products

def test_create_order(client, admin_token, test_db, test_products):
    # Recarregar e armazenar preços antes do commit
    products = []
    prices = []
    for p in test_products:
        product = test_db.merge(p)
        products.append(product)
        prices.append(product.price)
    test_db.commit()
    
    expected_total = prices[0] * 2 + prices[1]
    
    response = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "items": [
                {"product_id": products[0].id, "quantity": 2},
                {"product_id": products[1].id, "quantity": 1}
            ]
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["total"] == expected_total
    assert len(response.json()["items"]) == 2

def test_create_order_invalid_product(client, admin_token):
    response = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "items": [{"product_id": 9999, "quantity": 1}]
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_order_invalid_product(client, admin_token):
    response = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "items": [
                {"product_id": 999, "quantity": 1}
            ]
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_order_insufficient_stock(client, admin_token, test_products):
    response = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "items": [{"product_id": test_products[0].id, "quantity": 999}]
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Estoque insuficiente" in response.json()["detail"]

def test_list_orders(client, admin_token, test_db, test_products):
    # Criar pedido para teste
    order = Order(user_id=1, total=100)
    item = OrderItem(product_id=test_products[0].id, quantity=1, price=test_products[0].price)
    order.items.append(item)
    test_db.add(order)
    test_db.commit()

    response = client.get("/orders/", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0

def test_list_orders_no_orders(client, admin_token):
    response = client.get("/orders/", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_get_order_not_found(client, admin_token):
    response = client.get("/orders/999", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_cancel_order(client, admin_token, test_db, test_products):
    # Criar novo produto para o teste
    product = Product(
        name="Test Product",
        description="Test Description",
        price=100.00,
        stock=10
    )
    test_db.add(product)
    test_db.commit()
    product_id = product.id
    initial_stock = product.stock
    
    # Criar pedido
    order_response = client.post(
        "/orders/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "items": [{"product_id": product_id, "quantity": 1}]
        }
    )
    order_id = order_response.json()["id"]
    
    # Cancelar pedido
    response = client.patch(
        f"/orders/{order_id}/cancel",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Buscar produto atualizado
    updated_product = test_db.query(Product).filter(Product.id == product_id).first()
    assert updated_product.stock == initial_stock

def test_cancel_non_pending_order(client, admin_token, test_db, test_products):
    # Criar pedido já pago
    order = Order(user_id=1, total=100, status=OrderStatus.paid)
    test_db.add(order)
    test_db.commit()

    response = client.patch(
        f"/orders/{order.id}/cancel",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_cancel_order_already_delivered(client, admin_token, test_db):
    order = Order(
        user_id=1,
        total=100.00,
        status=OrderStatus.delivered
    )
    test_db.add(order)
    test_db.commit()

    response = client.patch(
        f"/orders/{order.id}/cancel",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_cancel_nonexistent_order(client, admin_token):
    response = client.patch(
        "/orders/999/cancel",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
