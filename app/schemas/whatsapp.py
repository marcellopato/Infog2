from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, Union
from datetime import datetime
import re

class MessageCreate(BaseModel):
    phone: str = Field(..., example="11999999999")
    message: str
    type: str = "text"

    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^\d{10,11}$', v.replace('+', '')):
            raise ValueError('Número de telefone inválido')  # Exatamente esta mensagem
        return v

class Message(BaseModel):
    id: int
    user_id: int
    phone: str
    message_type: str 
    content: Dict[str, Any] = Field(default_factory=dict)
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

class MessageResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]

class MessageStatus(BaseModel):
    id: int
    whatsapp_message_id: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
