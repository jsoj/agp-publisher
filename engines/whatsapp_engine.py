import asyncio
import httpx
import os
import re

class WhatsAppEngine:
    """Motor de envio WhatsApp via Evolution API com suporte a PTT (Voz), Texto e Mídia."""
    def __init__(self, base_url: str = None, api_key: str = None, instance: str = None):
        self.base_url = base_url or os.getenv("EVOLUTION_URL", "https://evolution.quantisia.com.br")
        self.api_key = api_key or os.getenv("EVOLUTION_APIKEY", "6CBB7DCE6D50-4851-A607-F2EC2C1580C2")
        self.instance = instance or os.getenv("EVOLUTION_INSTANCE", "01")
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

    async def send_text(self, recipient: str, text: str) -> bool:
        cleaned = "".join(filter(str.isdigit, recipient))
        url = f"{self.base_url}/message/sendText/{self.instance}"
        payload = {"number": cleaned, "text": text}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=self.headers)
                return resp.status_code in [200, 201]
        except Exception as e:
            print(f"❌ [WhatsAppEngine Text Error]: {e}")
            return False

    async def send_voice(self, recipient: str, audio_base64: str) -> bool:
        cleaned = "".join(filter(str.isdigit, recipient))
        url = f"{self.base_url}/message/sendWhatsAppAudio/{self.instance}"
        payload = {"number": cleaned, "audio": audio_base64, "encoding": True}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=self.headers)
                return resp.status_code in [200, 201]
        except Exception as e:
            print(f"❌ [WhatsAppEngine Voice Error]: {e}")
            return False
