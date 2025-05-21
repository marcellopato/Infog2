import pytest
from fastapi import HTTPException
from app.core.security import get_current_user, get_current_active_user, get_current_admin_user
from app.models.user import User

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client, test_db):
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("invalid_token", test_db)
    assert exc_info.value.status_code == 401
    assert "Não foi possível validar as credenciais" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_current_active_user_inactive(test_db):
    # Criar usuário inativo para teste
    inactive_user = User(
        email="inactive@test.com",
        username="inactive",
        hashed_password="hash",
        is_active=False
    )
    test_db.add(inactive_user)
    test_db.commit()

    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(inactive_user)
    assert exc_info.value.status_code == 400
    assert "Usuário inativo" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_verify_expired_token(client):
    from datetime import datetime, timedelta
    from app.core.security import create_access_token
    
    # Criar token expirado
    access_token = create_access_token(
        data={"sub": "test"},
        expires_delta=timedelta(minutes=-10)
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(access_token)
    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_verify_invalid_token_data(client):
    from app.core.security import create_access_token
    
    # Criar token sem 'sub'
    access_token = create_access_token(
        data={"invalid": "data"},
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(access_token)
    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_user_not_found(client, test_db):
    """Testa quando o usuário não é encontrado no banco"""
    from app.core.security import create_access_token
    
    access_token = create_access_token(
        data={"sub": "nonexistent_user"},
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(access_token, test_db)
    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_admin_user(test_db):
    """Testa verificação de permissão de admin"""
    # Criar usuário normal
    regular_user = User(
        email="regular@test.com",
        username="regular",
        hashed_password="hash",
        is_active=True,
        is_admin=False
    )
    test_db.add(regular_user)
    test_db.commit()

    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin_user(regular_user)
    assert exc_info.value.status_code == 403
    assert "Sem permissão de administrador" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_current_admin_user_success(test_db):
    """Testa acesso com usuário admin"""
    admin_user = User(
        email="admin@test.com",
        username="admin",
        hashed_password="hash",
        is_active=True,
        is_admin=True
    )
    test_db.add(admin_user)
    test_db.commit()

    result = await get_current_admin_user(admin_user)
    assert result == admin_user
    assert result.is_admin == True
