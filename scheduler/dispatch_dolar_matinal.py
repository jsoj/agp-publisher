import asyncio
import sys
import os

sys.path.append("/root/agp-publisher")
from engines.dolar_produtiva_service import publish_informe_dolar_produtiva

async def run():
    # Cotação e dados matinais do mercado
    cotacao = "R$ 5,2180"
    variacao = "+0,35%"
    min_val = "R$ 5,2010"
    max_val = "R$ 5,2240"
    resumo = (
        "O dólar comercial opera em leve alta na manhã desta segunda-feira, 31 de agosto de 2026, "
        "com o mercado reagindo aos desdobramentos de política monetária nos EUA e fluxo cambial de encerramento do mês."
    )
    fontes = ["Broadcast", "UOL Economia", "InfoMoney"]
    cbot_info = "Soja em Chicago opera em estabilidade com leve viés positivo na abertura dos negócios."

    res = await publish_informe_dolar_produtiva(
        cotacao=cotacao,
        variacao=variacao,
        min_val=min_val,
        max_val=max_val,
        resumo_mercado=resumo,
        fontes=fontes,
        cbot_info=cbot_info,
        is_alert=False
    )
    print("DOLAR_MATINAL_DISPATCH:", res)

if __name__ == "__main__":
    asyncio.run(run())
