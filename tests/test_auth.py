import pytest
from fastapi import status
from app.core.security import verify_password
from app.models.user import User

def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@luestilo.com.br",
            "username": "testuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_register_existing_email(client):
    # Primeiro registro
    client.post(
        "/auth/register",
        json={
            "email": "test@luestilo.com.br",
            "username": "testuser1",
            "password": "testpass123"
        }
    )
    
    # Tentativa de registro com mesmo email
    response = client.post(
        "/auth/register",
        json={
            "email": "test@luestilo.com.br",
            "username": "testuser2",
            "password": "testpass123"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email já cadastrado"

def test_register_invalid_password(client):
    """Testa registro com senha inválida"""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@luestilo.com.br",
            "username": "testuser",
            "password": "12345"  # senha muito curta
        }
    )
    assert response.status_code == 422
    assert "Senha deve ter pelo menos 6 caracteres" in str(response.json()["detail"][0]["msg"])

def test_register_duplicate_username(client):
    """Testa registro com username duplicado"""
    # Primeiro registro
    client.post(
        "/auth/register",
        json={
            "email": "user1@test.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    
    # Tentativa com mesmo username
    response = client.post(
        "/auth/register",
        json={
            "email": "user2@test.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username já está em uso"

def test_login_success(client):
    # Registrar usuário
    client.post(
        "/auth/register",
        json={
            "email": "test@luestilo.com.br",
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    # Tentar login
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client):
    # Registrar usuário
    client.post(
        "/auth/register",
        json={
            "email": "test@luestilo.com.br",
            "username": "testuser",
            "password": "testpass123"
        }
    )
    
    # Tentar login com senha errada
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Usuário ou senha incorretos"

def test_login_invalid_user(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "nonexistent",
            "password": "wrong"
        }
    )
    assert response.status_code == 401

def test_login_email_instead_username(client, test_db):
    # Registrar usuário
    client.post(
        "/auth/register",
        json={
            "email": "test@email.com",
            "username": "testuser",
            "password": "test123"
        }
    )
    
    # Login com email
    response = client.post(
        "/auth/login",
        data={
            "username": "test@email.com",
            "password": "test123"
        }
    )
    assert response.status_code == 200

def test_refresh_token(client):
    # Registrar e fazer login
    register_response = client.post(
        "/auth/register",
        json={
            "email": "test@luestilo.com.br",
            "username": "testuser",
            "password": "testpass123"
        }
    )
    token = register_response.json()["access_token"]
    
    # Tentar refresh token
    response = client.post(
        "/auth/refresh-token",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_refresh_token_invalid(client):
    """Testa refresh token com token inválido"""
    response = client.post(
        "/auth/refresh-token",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais"

def test_refresh_token_inactive_user(client, test_db):
    # Registrar usuário
    register_response = client.post(
        "/auth/register",
        json={
            "email": "inactive@test.com",
            "username": "inactive",
            "password": "test123"
        }
    )
    token = register_response.json()["access_token"]
    
    # Desativar usuário
    user = test_db.query(User).filter(User.username == "inactive").first()
    user.is_active = False
    test_db.commit()
    
    # Tentar refresh token
    response = client.post(
        "/auth/refresh-token",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Usuário inativo"
