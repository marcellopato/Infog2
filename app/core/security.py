from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.models.user import User
from sqlalchemy.orm import Session
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Não foi possível validar as credenciais")

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    logger.info(f"Verificando status do usuário: {current_user.username}")
    if not current_user.is_active:
        logger.warning(f"Tentativa de acesso com usuário inativo: {current_user.username}")
        raise HTTPException(status_code=400, detail="Usuário inativo")
    logger.info(f"Usuário {current_user.username} está ativo")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    logger.info(f"Verificando permissões admin: {current_user.username}")
    if not current_user.is_admin:
        logger.warning(f"Acesso negado para: {current_user.username}")
        raise HTTPException(
            status_code=403,
            detail="Sem permissão de administrador"
        )
    logger.info(f"Acesso admin confirmado para: {current_user.username}")
    return current_user
