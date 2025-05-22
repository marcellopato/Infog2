import pytest
from fastapi import status
from app.services.whatsapp import WhatsAppService
from app.models.order import Order, OrderStatus

@pytest.fixture
def test_phone():
    return "5511938037151"  # Número para testes

def test_send_order_confirmation(client, admin_token, test_db, test_phone):
    # Criar pedido
    order = Order(
        user_id=1,
        total=150.00,
        status=OrderStatus.pending
    )
    test_db.add(order)
    test_db.commit()

    response = client.post(
        f"/whatsapp/notify/order/{order.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "success" in response.json()["status"]

def test_send_status_update(client, admin_token, test_db, test_phone):
    # Criar pedido
    order = Order(
        user_id=1,
        total=200.00,
        status=OrderStatus.paid
    )
    test_db.add(order)
    test_db.commit()

    response = client.post(
        f"/whatsapp/notify/status/{order.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "delivered"}
    )
    assert response.status_code == status.HTTP_200_OK
