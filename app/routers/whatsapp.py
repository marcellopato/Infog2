from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, validator
import re
from app.core.database import get_db
from app.core.security import get_current_admin_user
from app.services.whatsapp import WhatsAppService
from app.schemas.whatsapp import Message, MessageResponse
from app.models.whatsapp import WhatsAppMessage
from app.models.order import Order, OrderStatus
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
whatsapp = WhatsAppService()

class MessageCreate(BaseModel):
    phone: str
    message: str
    type: str = "text"

    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^\d{10,11}$', v.replace('+', '')):
            raise ValueError('Número de telefone inválido')
        return v

@router.get("/test-connection")
async def test_connection():
    """Testa a conexão com a API do WhatsApp"""
    try:
        result = await whatsapp.verify_token()
        if result:
            return {"status": "success", "message": "Conexão estabelecida"}
        return {"status": "error", "message": "Falha na conexão"}
    except Exception as e:
        logger.error(f"Erro ao testar conexão: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/send", response_model=MessageResponse)
async def send_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Envia mensagem via WhatsApp"""
    try:
        # Formatar número
        formatted_phone = f"55{message.phone}" if not message.phone.startswith("55") else message.phone
        
        # Enviar mensagem
        result = await whatsapp.send_message(
            phone=formatted_phone,
            message=message.message
        )
        
        # Registrar mensagem
        db_message = WhatsAppMessage(
            user_id=current_user.id,
            phone=formatted_phone,
            message_type="text",
            content={"message": message.message},
            status="sent"
        )
        db.add(db_message)
        db.commit()
        
        logger.info(f"Mensagem enviada: {result}")
        return {
            "status": "success",
            "message": "Mensagem enviada com sucesso",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/notify/order/{order_id}")
async def notify_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Envia notificação sobre pedido via WhatsApp"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado"
            )

        # Formatar mensagem
        message = (
            f"✅ Pedido #{order.id}\n"
            f"Total: R$ {float(order.total):.2f}\n"
            f"Status: {order.status.value}\n\n"
            "Obrigado pela compra! 🛍️"
        )

        # Enviar mensagem
        result = await whatsapp.send_message(
            phone="5511938037151",  # Seu número
            message=message
        )

        # Registrar envio
        db_message = WhatsAppMessage(
            user_id=current_user.id,
            phone="5511938037151",
            content=message,
            status="sent",
            message_type="order_notification"
        )
        db.add(db_message)
        db.commit()

        return {
            "status": "success",
            "message": "Notificação enviada",
            "data": result
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao enviar notificação: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notify/status/{order_id}")
async def notify_order_status(
    order_id: int,
    status_update: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Envia notificação de atualização de status do pedido"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")

        # Formatar mensagem
        message = (
            f"📦 Atualização do Pedido #{order.id}\n"
            f"Status anterior: {order.status.value}\n"
            f"Novo status: {status_update['status']}\n\n"
            "Qualquer dúvida estamos à disposição!"
        )

        # Enviar mensagem
        result = await whatsapp.send_message(
            phone="5511938037151",  # Seu número
            message=message
        )

        # Registrar envio
        db_message = WhatsAppMessage(
            user_id=current_user.id,
            phone="5511938037151",
            content={"order_id": order.id, "message": message},
            status="sent",
            message_type="status_update"
        )
        db.add(db_message)
        db.commit()

        return {
            "status": "success",
            "message": "Notificação enviada",
            "data": result
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao enviar notificação: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages", response_model=List[Message])
async def list_messages(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user),
    limit: int = 10
):
    """Lista últimas mensagens enviadas"""
    messages = db.query(WhatsAppMessage).order_by(
        WhatsAppMessage.created_at.desc()
    ).limit(limit).all()
    
    # Garantir que content é um dicionário
    for message in messages:
        if not isinstance(message.content, dict):
            message.content = {"text": str(message.content)}
    
    return messages

@router.get("/messages/{message_id}/status")
async def get_message_status(
    message_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Verifica status de uma mensagem específica"""
    message = db.query(WhatsAppMessage).filter(WhatsAppMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    return {
        "id": message.id,
        "status": message.status,
        "sent_at": message.created_at
    }
