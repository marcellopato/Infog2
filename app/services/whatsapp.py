import httpx
from fastapi import HTTPException
import logging
import json
from app.core.config import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.api_url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        logger.info(f"WhatsApp Service iniciado: {self.api_url}")

    async def send_message(self, phone: str, message: str) -> dict:
        try:
            if not phone.startswith("55"):
                phone = f"55{phone}"

            payload = {
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "text",
                "text": {"body": message}
            }

            logger.info(f"Enviando mensagem para {phone}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                )
                
                result = response.json()
                logger.info(f"Resposta WhatsApp: {json.dumps(result, indent=2)}")
                return result

        except Exception as e:
            logger.error(f"Erro no WhatsApp Service: {str(e)}")
            raise

    async def verify_token(self) -> bool:
        """Verifica se o token do WhatsApp está válido"""
        try:
            # Tentar obter informações do número
            phone_id = settings.WHATSAPP_PHONE_ID
            url = f"{settings.WHATSAPP_API_URL}/{phone_id}"
            
            logger.info(f"Verificando token para phone_id: {phone_id}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info("Token válido")
                    return True
                
                logger.error(f"Erro na verificação: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao verificar token: {str(e)}")
            return False
