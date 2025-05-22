import httpx
from fastapi import HTTPException
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.base_url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_ID}"
        self.headers = {"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"}
    
    async def send_message(self, phone: str, content: dict):
        try:
            payload = {
                "messaging_product": "whatsapp",
                "to": phone,
                "type": content.get("type", "text"),
                "text": {"body": content.get("message", "")}
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro ao enviar mensagem")
