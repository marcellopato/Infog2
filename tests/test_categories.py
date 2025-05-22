import pytest
from fastapi import status
from app.models.category import Category

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
def test_category(test_db):
    category = Category(
        name="Test Category",
        description="Test Description"
    )
    test_db.add(category)
    test_db.commit()
    return category

def test_create_category(client, admin_token):
    response = client.post(
        "/categories/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Nova Categoria",
            "description": "Descrição da categoria"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "Nova Categoria"

def test_create_category_no_admin(client):
    # Criar usuário normal
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
        "/categories/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Nova Categoria",
            "description": "Descrição da categoria"
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_list_categories(client, test_category):
    response = client.get("/categories/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0
    assert response.json()[0]["name"] == test_category.name

def test_get_category(client, test_category):
    response = client.get(f"/categories/{test_category.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == test_category.name

def test_update_category(client, admin_token, test_category):
    response = client.patch(
        f"/categories/{test_category.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Categoria Atualizada"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Categoria Atualizada"

def test_delete_category(client, admin_token, test_db, test_category):
    category_id = test_category.id
    response = client.delete(
        f"/categories/{category_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verifica se categoria foi marcada como inativa
    updated_category = test_db.query(Category).filter(Category.id == category_id).first()
    assert not updated_category.is_active
