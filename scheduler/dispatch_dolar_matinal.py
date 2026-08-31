import asyncio
import sys
import os

sys.path.append("/root/agp-publisher")
from engines.market_data_engine import fetch_deterministic_usdbRL
from engines.dolar_produtiva_service import publish_informe_dolar_produtiva

async def run():
    market = await fetch_deterministic_usdbRL()
    cotacao = market["cotacao"]
    variacao = market["variacao"]
    min_val = market["min_val"]
    max_val = market["max_val"]
    is_alert = abs(market["pct_raw"]) >= 1.5

    resumo = (
        f"Na manhã desta segunda-feira, 31 de agosto de 2026, o dólar opera cotado a {cotacao} ({variacao}). "
        "O mercado de câmbio acompanha a dinâmica das taxas de juros globais e o fluxo de ajuste de posições no encerramento do mês."
    )
    fontes = ["Broadcast", "B3", "Yahoo Finance API"]
    cbot_info = "Soja na Bolsa de Chicago (CBOT) opera com estabilidade na sessão diurna."

    res = await publish_informe_dolar_produtiva(
        cotacao=cotacao,
        variacao=variacao,
        min_val=min_val,
        max_val=max_val,
        resumo_mercado=resumo,
        fontes=fontes,
        cbot_info=cbot_info,
        is_alert=is_alert
    )
    print("DOLAR_MATINAL_DISPATCH:", res)

if __name__ == "__main__":
    asyncio.run(run())
