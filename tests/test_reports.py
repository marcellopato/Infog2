import pytest
from fastapi import status
from datetime import datetime, timedelta
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product

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
def test_sales_data(test_db):
    # Criar produtos
    product = Product(name="Test Product", price=100.00, stock=10)
    test_db.add(product)
    
    # Criar pedido pago com data atual
    current_time = datetime.now()
    order = Order(
        user_id=1,
        status=OrderStatus.paid,
        total=200.00,
        created_at=current_time
    )
    order_item = OrderItem(
        product_id=1,
        quantity=2,
        price=100.00
    )
    order.items.append(order_item)
    test_db.add(order)
    test_db.commit()
    return {"product": product, "order": order, "created_at": current_time}

def test_generate_sales_report(client, admin_token, test_sales_data):
    start_date = test_sales_data["created_at"] - timedelta(hours=1)
    end_date = test_sales_data["created_at"] + timedelta(hours=1)
    
    response = client.post(
        "/reports/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "type": "sales",
            "period": "daily",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["type"] == "sales"
    assert response.json()["data"]["total_sales"] == 200.00

def test_generate_products_report(client, admin_token, test_sales_data):
    response = client.post(
        "/reports/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "type": "products",
            "period": "monthly",
            "start_date": datetime.now().isoformat()
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["data"]["products"]) > 0

def test_generate_report_invalid_type(client, admin_token):
    response = client.post(
        "/reports/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "type": "invalid",
            "period": "daily",
            "start_date": datetime.now().isoformat()
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_report(client, admin_token, test_db, test_sales_data):
    # Gerar relatório
    create_response = client.post(
        "/reports/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "type": "sales",
            "period": "daily",
            "start_date": datetime.now().isoformat()
        }
    )
    report_id = create_response.json()["id"]
    
    # Buscar relatório
    response = client.get(
        f"/reports/{report_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == report_id
