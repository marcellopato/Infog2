from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_admin_user
from app.services.whatsapp import WhatsAppService
from app.models.whatsapp import WhatsAppMessage
from app.schemas.whatsapp import MessageCreate, Message
from typing import List

router = APIRouter()
whatsapp = WhatsAppService()

@router.post("/send", response_model=Message)
async def send_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Enviar mensagem WhatsApp para cliente"""
    result = await whatsapp.send_message(message.phone, message.content)
    
    db_message = WhatsAppMessage(
        user_id=current_user.id,
        phone=message.phone,
        message_type=message.type,
        content={"text": message.content},
        status="sent"
    )
    db.add(db_message)
    db.commit()
    
    return db_message
