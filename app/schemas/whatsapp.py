from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union
from datetime import datetime

class MessageCreate(BaseModel):
    phone: str = Field(..., example="5511999999999")
    message: str = Field(..., example="Mensagem de teste")
    type: str = Field(default="text")

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
