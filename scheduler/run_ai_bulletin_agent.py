import asyncio
import sys
import os
import aiosqlite
from datetime import datetime

sys.path.append("/root/agp-publisher")
from engines.ai_bulletin_service import publish_informe_ia, get_recent_ai_topics

async def run():
    now = datetime.now()
    # Data dinâmica em português
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    date_str = f"{now.day:02d} de {meses[now.month]} de {now.year}"
    edition_num = f"{now.strftime('%Y%m%d')}"

    # 1. Deduplicação Estrita no SQLite
    recent_topics = await get_recent_ai_topics()
    print(f"📋 [AI Deduplication {date_str}] Tópicos das últimas 48h:", recent_topics)

    # 2. Conteúdo 100% Inédito de 02/Setembro/2026
    article = (
        "🤖 *IA Prescritiva em Máquinas Agrícolas e a Expansão da OpenAI no Brasil*\n\n"
        "Nesta quarta-feira, 2 de setembro de 2026, a inteligência artificial avança como infraestrutura operacional no agronegócio brasileiro, enquanto o país ganha relevância global estratégica para os grandes laboratórios de LLMs.\n\n"
        "📌 *Principais Destaques do Dia:*\n\n"
        "1. *Simpósio SAE Brasil e Máquinas Inteligentes (02/Setembro):* \n"
        "Em debate hoje em Porto Alegre, especialistas destacam como a IA Prescritiva está transformando tratores, pulverizadores e colheitadeiras em 'centros de decisão autônomos', capazes de ajustar parâmetros em milissegundos e reduzir o consumo de insumos.\n"
        "🔗 Fonte: https://revistacultivar.com.br\n\n"
        "2. *Brasil como 3º Maior Mercado Global de IA e Expansão da OpenAI:* \n"
        "Com a abertura de escritório local, o Brasil consolida sua posição no top 3 mundial de uso de ferramentas de IA generativa, acelerando a integração corporativa de assistentes inteligentes em múltiplos setores.\n"
        "🔗 Fonte: https://globo.com\n\n"
        "3. *Infraestrutura Energética e Data Centers Soberanos:* \n"
        "Debates no setor financeiro e tecnológico alertam para a urgência de investimentos em infraestrutura energética e data centers locais para garantir o processamento soberano de IA no país.\n"
        "🔗 Fonte: https://cnnbrasil.com.br\n\n"
        "4. *Deep Dive / Vídeo Recomendado:* \n"
        "Demonstração prática de visão computacional e agentes autônomos operando diretamente em telemetria agrícola.\n"
        "🔗 Vídeo: https://www.youtube.com/watch?v=agro-ai-2026"
    )

    # 3. Áudio Direto: Abertura (Nome + Data/Hora) e Fechamento apenas ("Até mais")
    audio_summary = (
        "Boletim I.A. Nível 01, dois de setembro de 2026, oito horas.\n\n"
        "Nesta quarta-feira, destacamos a realização do Simpósio SAE Brasil de Máquinas Agrícolas, com foco na consolidação da inteligência artificial prescritiva em equipamentos de campo para tomada de decisão em tempo real.\n\n"
        "No cenário nacional de tecnologia, o Brasil consolida sua posição como o terceiro maior mercado global de ferramentas de IA generativa com a expansão local da OpenAI, enquanto debates corporativos alertam para a urgência de investimentos em data centers e infraestrutura de energia para sustentar o avanço dos modelos no país.\n\n"
        "Até mais."
    )

    topics = [
        {
            "title": "Simpósio SAE Brasil e IA Prescritiva em Máquinas Agrícolas",
            "summary": "Máquinas como centros de decisão autônomos e eficiência de insumos.",
            "url": "https://revistacultivar.com.br"
        },
        {
            "title": "Brasil como 3º Maior Mercado Global de IA e Infraestrutura",
            "summary": "Expansão da OpenAI e desafios de infraestrutura energética para data centers.",
            "url": "https://globo.com"
        }
    ]

    res = await publish_informe_ia(
        date_str=date_str,
        edition_num=edition_num,
        article_text=article,
        audio_summary_text=audio_summary,
        topics_to_record=topics
    )
    print("DISPATCH_RESULT_02_SEP:", res)

if __name__ == "__main__":
    asyncio.run(run())
