import asyncio
import base64
import re
import edge_tts
import httpx
import os
import aiosqlite
from datetime import datetime

AI_GROUP_JID = "120363410789564152@g.us"
EVOLUTION_URL = os.getenv("EVOLUTION_URL", "https://evolution.quantisia.com.br")
EVOLUTION_APIKEY = os.getenv("EVOLUTION_APIKEY", "6CBB7DCE6D50-4851-A607-F2EC2C1580C2")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "01")
DB_PATH = "/root/agp-publisher/data/agp_publisher.db"

_last_dispatch_time = 0

async def record_ai_history(topic_title: str, summary: str, url: str):
    """Salva os tópicos já publicados nas últimas 48h para evitar repetição."""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ai_bulletin_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_title TEXT NOT NULL,
                    summary TEXT,
                    url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await db.execute("""
                INSERT INTO ai_bulletin_history (topic_title, summary, url)
                VALUES (?, ?, ?)
            """, (topic_title, summary, url))
            await db.commit()
    except Exception as e:
        print(f"⚠️ [AI DB History Error]: {e}")

async def get_recent_ai_topics() -> list[str]:
    """Retorna os títulos publicados nas últimas 48 horas."""
    try:
        if not os.path.exists(DB_PATH):
            return []
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ai_bulletin_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_title TEXT NOT NULL,
                    summary TEXT,
                    url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            async with db.execute("""
                SELECT topic_title FROM ai_bulletin_history 
                WHERE created_at >= datetime('now', '-1 day')
            """) as cursor:
                rows = await cursor.fetchall()
                return [r[0] for r in rows]
    except Exception as e:
        print(f"⚠️ [Get AI History Error]: {e}")
        return []

async def publish_informe_ia(
    date_str: str,
    edition_num: str,
    article_text: str,
    audio_summary_text: str,
    topics_to_record: list[dict]
) -> dict:
    """
    Executa o fluxo completo do 'Boletim I.A. - Nível 01':
    1. Salvaguarda anti-loop (debounce).
    2. Publica o Artigo Detalhado com links no grupo de WhatsApp.
    3. Gera e envia o Áudio Resumo via FranciscaNeural (tom jornalístico/executivo).
    4. Grava no banco SQLite para deduplicação em 48h.
    """
    global _last_dispatch_time
    import time
    now = time.time()
    if now - _last_dispatch_time < 30:
        return {"status": "debounced", "message": "Disparo ignorado para evitar duplicação."}
    _last_dispatch_time = now

    headers = {
        "apikey": EVOLUTION_APIKEY,
        "Content-Type": "application/json"
    }

    # Cabeçalho Oficial do Artigo
    full_text_message = (
        f"🤖 *BOLETIM I.A. — NÍVEL 01* | Edição #{edition_num}\n"
        f"📅 _{date_str}_\n\n"
        f"{article_text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"_Projeto Brasil 2050 | Inteligência e Automação_"
    )

    results = {}

    # 1. Envio do Texto Longo / Detalhado (com linkPreview desativado para evitar banner gráfico)
    async with httpx.AsyncClient(timeout=30.0) as client:
        text_url = f"{EVOLUTION_URL}/message/sendText/{EVOLUTION_INSTANCE}"
        payload = {
            "number": AI_GROUP_JID, 
            "text": full_text_message,
            "linkPreview": False,
            "options": {
                "linkPreview": False
            }
        }
        resp_text = await client.post(text_url, json=payload, headers=headers)
        results["text_status"] = resp_text.status_code in [200, 201]

    # 2. Geração e Envio do Áudio Resumo
    clean_audio_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', audio_summary_text)
    clean_audio_text = re.sub(r'[*_#`~>|-]', ' ', clean_audio_text)
    clean_audio_text = re.sub(r'https?://\S+', '', clean_audio_text)
    clean_audio_text = re.sub(r'\s+', ' ', clean_audio_text).strip()

    try:
        communicate = edge_tts.Communicate(clean_audio_text, "pt-BR-FranciscaNeural")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        if audio_data:
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")
            async with httpx.AsyncClient(timeout=30.0) as client:
                audio_url = f"{EVOLUTION_URL}/message/sendWhatsAppAudio/{EVOLUTION_INSTANCE}"
                audio_payload = {
                    "number": AI_GROUP_JID,
                    "audio": audio_base64,
                    "encoding": True
                }
                resp_audio = await client.post(audio_url, json=audio_payload, headers=headers)
                results["audio_status"] = resp_audio.status_code in [200, 201]
        else:
            results["audio_status"] = False
    except Exception as e:
        print(f"⚠️ [AI Audio Error]: {e}")
        results["audio_status"] = False

    # 3. Gravação no Histórico SQLite (Deduplicação 48h)
    for topic in topics_to_record:
        await record_ai_history(topic.get("title", ""), topic.get("summary", ""), topic.get("url", ""))

    return results
