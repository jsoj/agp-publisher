import urllib.request
import json
import httpx
import asyncio

async def fetch_deterministic_usdbRL() -> dict:
    """
    Busca a cotação oficial em tempo real através de APIs financeiras estruturadas (sem LLM ou texto solto).
    Retorna cotação exata de 4 casas decimais, variação percentual, mínima e máxima intradiária.
    """
    # 1. Provedor Primário: Yahoo Finance API Oficial (USDBRL=X)
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/USDBRL=X?interval=1m&range=1d"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                meta = data["chart"]["result"][0]["meta"]
                price = float(meta.get("regularMarketPrice", 0.0))
                prev = float(meta.get("previousClose", price))
                high = float(meta.get("regularMarketDayHigh", price))
                low = float(meta.get("regularMarketDayLow", price))
                pct = ((price - prev) / prev) * 100 if prev else 0.0
                
                if price > 0:
                    return {
                        "cotacao": f"R$ {price:.4f}",
                        "variacao": f"{pct:+.2f}%",
                        "min_val": f"R$ {low:.4f}",
                        "max_val": f"R$ {high:.4f}",
                        "price_raw": price,
                        "pct_raw": pct,
                        "source": "Mercado Interbancário B3 / Yahoo Finance API"
                    }
    except Exception as e:
        print(f"⚠️ [Yahoo Finance Error]: {e}")

    # 2. Provedor Secundário: HG Brasil Finance API
    try:
        url = "https://api.hgbrasil.com/finance?format=json"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                usd = data["results"]["currencies"]["USD"]
                price = float(usd["buy"])
                pct = float(usd["variation"])
                return {
                    "cotacao": f"R$ {price:.4f}",
                    "variacao": f"{pct:+.2f}%",
                    "min_val": f"R$ {price:.4f}",
                    "max_val": f"R$ {price:.4f}",
                    "price_raw": price,
                    "pct_raw": pct,
                    "source": "HG Brasil Finance API"
                }
    except Exception as e:
        print(f"⚠️ [HG Brasil Error]: {e}")

    raise RuntimeError("ERRO_FATAL: Nenhuma API determinística de câmbio respondeu.")
