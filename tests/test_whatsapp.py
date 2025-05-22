import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from app.services.whatsapp import WhatsAppService
from app.models.order import Order, OrderStatus
from app.models.whatsapp import WhatsAppMessage
from datetime import datetime
from app.core.security import create_access_token

@pytest.fixture
def test_phone():
    return "5511938037151"  # Número para testes

@pytest.fixture
def mock_whatsapp_response():
    return {
        "messaging_product": "whatsapp",
        "contacts": [{"input": "5511999999999", "wa_id": "5511999999999"}],
        "messages": [{"id": "wamid.test123"}]
    }

@pytest.fixture
def whatsapp_message():
    return {
        "phone": "11999999999",
        "message": "Teste de mensagem",
        "type": "text"
    }

@pytest.fixture
def admin_token(test_db):
    """Cria um token de admin para testes"""
    from app.models.user import User
    admin = User(
        username="admin_test",
        email="admin@test.com",
        hashed_password="test123",
        is_admin=True
    )
    test_db.add(admin)
    test_db.commit()
    
    return create_access_token({"sub": admin.username})

@pytest.fixture
def test_message_data(test_db, admin_token):
    """Cria dados de teste para mensagens"""
    messages = [
        WhatsAppMessage(
            user_id=1,
            phone="11999999999",
            message_type="text",
            content={"message": f"Teste {i}"},
            status="sent"
        )
        for i in range(3)
    ]
    for msg in messages:
        test_db.add(msg)
    test_db.commit()
    return messages

def test_send_message(client, admin_token, test_db, mock_whatsapp_response, whatsapp_message):
    with patch.object(WhatsAppService, 'send_message', return_value=mock_whatsapp_response):
        response = client.post(
            "/whatsapp/send",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=whatsapp_message
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "success"

def test_list_messages(client, admin_token, test_db):
    # Criar algumas mensagens de teste
    messages = [
        WhatsAppMessage(
            user_id=1,
            phone="11999999999",
            message_type="text",
            content={"message": "Teste"},
            status="sent"
        )
        for _ in range(3)
    ]
    for msg in messages:
        test_db.add(msg)
    test_db.commit()

    response = client.get(
        "/whatsapp/messages",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3

def test_notify_order(client, admin_token, test_db, mock_whatsapp_response):
    # Criar pedido de teste
    order = Order(
        user_id=1,
        total=150.00,
        status=OrderStatus.pending
    )
    test_db.add(order)
    test_db.commit()

    with patch.object(WhatsAppService, 'send_message', return_value=mock_whatsapp_response):
        response = client.post(
            f"/whatsapp/notify/order/{order.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "success"

def test_test_connection(client, admin_token):
    with patch.object(WhatsAppService, 'verify_token', return_value=True):
        response = client.get(
            "/whatsapp/test-connection",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "success"

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

def test_send_status_update(client, admin_token, test_db, test_phone, mock_whatsapp_response):
    # Criar pedido
    order = Order(
        user_id=1,
        total=200.00,
        status=OrderStatus.paid
    )
    test_db.add(order)
    test_db.commit()

    with patch.object(WhatsAppService, 'send_message', return_value=mock_whatsapp_response):
        response = client.post(
            f"/whatsapp/notify/status/{order.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"status": "delivered"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "success"

def test_whatsapp_service_init():
    service = WhatsAppService()
    assert service.api_url is not None
    assert "Bearer" in service.headers["Authorization"]

def test_send_message_invalid_phone(client, admin_token):
    response = client.post(
        "/whatsapp/send",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "phone": "abc123",
            "message": "test"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    error_detail = response.json()["detail"][0]
    assert error_detail["msg"] == "Número de telefone inválido"

def test_notify_order_not_found(client, admin_token):
    response = client.post(
        "/whatsapp/notify/order/999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Pedido não encontrado"
