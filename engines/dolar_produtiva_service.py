import asyncio
import base64
import re
import edge_tts
import httpx

HEDGE_GROUP_JID = "120363407103825707@g.us"
EVOLUTION_URL = "https://evolution.quantisia.com.br"
EVOLUTION_APIKEY = "6CBB7DCE6D50-4851-A607-F2EC2C1580C2"
EVOLUTION_INSTANCE = "01"

async def publish_informe_dolar_produtiva(cotacao: str, variacao: str, min_val: str, max_val: str, resumo_mercado: str, fontes: list[str]) -> dict:
    """
    Executa o fluxo completo do 'Informe de Dólar Produtiva':
    1. Publica Texto formatado com Cotação 4 casas no topo.
    2. Gera e envia Áudio via FranciscaNeural (tom jornalístico).
    """
    headers = {
        "apikey": EVOLUTION_APIKEY,
        "Content-Type": "application/json"
    }
    
    # 1. Monta Texto do WhatsApp
    fontes_str = ", ".join(fontes) if fontes else "UOL Economia, InfoMoney e Broadcast"
    text_msg = (
        f"*{cotacao} ({variacao})*\n"
        f"Mínima: {min_val} | Máxima: {max_val}\n\n"
        f"{resumo_mercado}\n\n"
        f"_Fontes: {fontes_str}_\n"
        f"_Projeto Brasil 2050_"
    )

    # 2. Monta Roteiro do Áudio (Francisca)
    audio_script = (
        f"Informe de Câmbio e Mercado Financeiro, Projeto Brasil 2050.\n\n"
        f"O dólar comercial opera cotado a {cotacao.replace('R$', '').strip()} reais, com variação de {variacao}.\n"
        f"A moeda registrou mínima de {min_val.replace('R$', '').strip()} e máxima de {max_val.replace('R$', '').strip()}.\n\n"
        f"{resumo_mercado}\n\n"
        f"Informações apuradas com base em dados de {fontes_str}.\n"
        f"Este é o informe executivo do Projeto Brasil 2050 para a Produtiva Sementes."
    )

    results = {}

    # Disparo do Texto
    async with httpx.AsyncClient(timeout=30.0) as client:
        text_url = f"{EVOLUTION_URL}/message/sendText/{EVOLUTION_INSTANCE}"
        text_payload = {"number": HEDGE_GROUP_JID, "text": text_msg}
        resp_text = await client.post(text_url, json=text_payload, headers=headers)
        results["text_status"] = resp_text.status_code in [200, 201]

    # Geração e Disparo do Áudio
    clean_audio_text = re.sub(r'[*_#`~>|-]', ' ', audio_script)
    clean_audio_text = re.sub(r'\s+', ' ', clean_audio_text).strip()
    
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
                "number": HEDGE_GROUP_JID,
                "audio": audio_base64,
                "encoding": True
            }
            resp_audio = await client.post(audio_url, json=audio_payload, headers=headers)
            results["audio_status"] = resp_audio.status_code in [200, 201]
    else:
        results["audio_status"] = False

    return results
