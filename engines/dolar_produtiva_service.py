import asyncio
import base64
import re
import edge_tts
import httpx
import os
import aiosqlite

HEDGE_GROUP_JID = "120363407103825707@g.us"
EVOLUTION_URL = os.getenv("EVOLUTION_URL", "https://evolution.quantisia.com.br")
EVOLUTION_APIKEY = os.getenv("EVOLUTION_APIKEY", "6CBB7DCE6D50-4851-A607-F2EC2C1580C2")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "01")
DB_PATH = "/root/agp-publisher/data/agp_publisher.db"

# Salvaguarda: Controle de trava contra disparo duplo (Debounce)
_last_dispatch_time = 0

async def record_dolar_history(cotacao: str, variacao: str, min_val: str, max_val: str, resumo: str, cbot_info: str = ""):
    """Salva a cotação no banco SQLite para histórico e gráficos."""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS dolar_produtiva_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cotacao TEXT NOT NULL,
                    variacao TEXT NOT NULL,
                    min_val TEXT,
                    max_val TEXT,
                    cbot_info TEXT,
                    resumo TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await db.execute("""
                INSERT INTO dolar_produtiva_history (cotacao, variacao, min_val, max_val, cbot_info, resumo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cotacao, variacao, min_val, max_val, cbot_info, resumo))
            await db.commit()
    except Exception as e:
        print(f"⚠️ [DB History Error]: {e}")

async def publish_informe_dolar_produtiva(
    cotacao: str, 
    variacao: str, 
    min_val: str, 
    max_val: str, 
    resumo_mercado: str, 
    fontes: list[str],
    cbot_info: str = "",
    is_alert: bool = False
) -> dict:
    """
    Executa o fluxo completo do 'Informe de Dólar Produtiva':
    1. Salvaguardas anti-loop e anti-trava.
    2. Publica Texto formatado com Cotação 4 casas no topo (+ CBOT / Alerta).
    3. Gera e envia Áudio via FranciscaNeural (tom jornalístico).
    4. Persiste no histórico SQLite.
    """
    global _last_dispatch_time
    import time
    now = time.time()
    
    # Debounce de 30 segundos contra loops acidentais
    if now - _last_dispatch_time < 30:
        return {"status": "debounced", "message": "Disparo ignorado para evitar loops/duplicações."}
    _last_dispatch_time = now

    headers = {
        "apikey": EVOLUTION_APIKEY,
        "Content-Type": "application/json"
    }
    
    fontes_str = ", ".join(fontes) if fontes else "UOL Economia, InfoMoney e Broadcast"
    
    # 1. Montagem do Texto com Emojis de Alerta se volatilidade forte
    header_tag = "🚨⚡ *ALERTA DE VOLATILIDADE* ⚡🚨\n\n" if is_alert else ""
    cbot_block = f"\n\n🌱 *Soja / Chicago (CBOT):* {cbot_info}" if cbot_info else ""

    text_msg = (
        f"{header_tag}*{cotacao} ({variacao})*\n"
        f"Mínima: {min_val} | Máxima: {max_val}"
        f"{cbot_block}\n\n"
        f"{resumo_mercado}\n\n"
        f"_Fontes: {fontes_str}_\n"
        f"_Projeto Brasil 2050_"
    )

    # 2. Roteiro do Áudio (Francisca)
    audio_cbot = f" No mercado de commodities, {cbot_info}." if cbot_info else ""
    audio_alert = "Atenção para alerta de forte oscilação no mercado de câmbio. " if is_alert else ""
    
    audio_script = (
        f"Informe de Câmbio e Mercado Financeiro, Projeto Brasil 2050.\n\n"
        f"{audio_alert}O dólar comercial opera cotado a {cotacao.replace('R$', '').strip()} reais, com variação de {variacao}.\n"
        f"A moeda registrou mínima de {min_val.replace('R$', '').strip()} e máxima de {max_val.replace('R$', '').strip()}."
        f"{audio_cbot}\n\n"
        f"{resumo_mercado}\n\n"
        f"Informações apuradas com base em dados de {fontes_str}.\n"
        f"Este é o informe executivo do Projeto Brasil 2050 para a Produtiva Sementes."
    )

    results = {}

    # Disparo do Texto
    async with httpx.AsyncClient(timeout=25.0) as client:
        text_url = f"{EVOLUTION_URL}/message/sendText/{EVOLUTION_INSTANCE}"
        text_payload = {"number": HEDGE_GROUP_JID, "text": text_msg}
        resp_text = await client.post(text_url, json=text_payload, headers=headers)
        results["text_status"] = resp_text.status_code in [200, 201]

    # Geração e Disparo do Áudio
    clean_audio_text = re.sub(r'[*_#`~>|-]', ' ', audio_script)
    clean_audio_text = re.sub(r'\s+', ' ', clean_audio_text).strip()
    
    # Limita texto do áudio para economizar processamento e manter concisão
    if len(clean_audio_text) > 1000:
        clean_audio_text = clean_audio_text[:1000] + "..."

    try:
        communicate = edge_tts.Communicate(clean_audio_text, "pt-BR-FranciscaNeural")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        if audio_data:
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")
            async with httpx.AsyncClient(timeout=25.0) as client:
                audio_url = f"{EVOLUTION_URL}/message/sendWhatsAppAudio/{EVOLUTION_INSTANCE}"
                audio_payload = {
                    "number": HEDGE_GROUP_JID,
                    "audio": audio_base64,
                    "encoding": True
                }
                resp_audio = await client.post(audio_url, json=audio_payload, headers=headers)
                results["audio_status"] = resp_audio.status_code in [200, 201]
        else:
            results["audio_status"] = False
    except Exception as err:
        print(f"⚠️ [Audio Error]: {err}")
        results["audio_status"] = False

    # Persistência em Banco
    await record_dolar_history(cotacao, variacao, min_val, max_val, resumo_mercado, cbot_info)

    return results
