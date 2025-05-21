from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password, get_current_user
from app.models.user import User
from app.schemas.auth import UserCreate, Token
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar email duplicado
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Verificar username duplicado
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username já está em uso")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Tentativa de login: {form_data.username}")
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login falhou para: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Login bem sucedido para usuário: {user.username}")
    
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh-token", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    access_token = create_access_token(
        data={"sub": current_user.username},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}
