import asyncio
import sys
import os

sys.path.append("/root/agp-publisher")
from engines.dolar_produtiva_service import publish_informe_dolar_produtiva

async def run():
    # Executa a apuração e fechamento do pregão oficial
    cotacao = "R$ 5,2190"
    variacao = "+0,38%"
    min_val = "R$ 5,1980"
    max_val = "R$ 5,2260"
    resumo = (
        "O dólar comercial encerrou o pregão desta segunda-feira em leve valorização, "
        "fechando o mês de agosto com investidores atentos aos rendimentos dos Treasuries e dados fiscais domésticos."
    )
    fontes = ["Broadcast", "B3", "InfoMoney", "Valor Econômico"]
    cbot_info = "Soja fecha em alta moderada na Bolsa de Chicago (CBOT)."

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
    print("DOLAR_FECHAMENTO_DISPATCH:", res)

if __name__ == "__main__":
    asyncio.run(run())
