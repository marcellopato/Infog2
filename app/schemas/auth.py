from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

    @validator('password')
    def password_must_not_be_empty(cls, v):
        if not v or len(v.strip()) < 6:
            raise ValueError('Senha deve ter pelo menos 6 caracteres')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
