import asyncio
import sys
import os

sys.path.append("/root/agp-publisher")
from engines.ai_bulletin_service import publish_informe_ia, get_recent_ai_topics
from engines.ai_curator_engine import generate_daily_ai_bulletin

async def main():
    print("🚀 [AI Bulletin Runner] Iniciando curadoria autônoma ao vivo com busca web e deduplicação...")
    
    # 1. Recupera histórico das últimas 24 horas gravado no SQLite
    recent_topics = await get_recent_ai_topics()
    print(f"📋 [Histórico 24h] Tópicos já abordados para evitar duplicação ({len(recent_topics)} encontrados):")
    for t in recent_topics:
        print(f"   - {t}")

    # 2. Executa a curadoria inteligente com pesquisa ao vivo no Google Search e Gemini API
    # Salvaguarda: loop de execução síncrona/assíncrona protegida
    loop = asyncio.get_running_loop()
    curated = await loop.run_in_executor(None, generate_daily_ai_bulletin, recent_topics)
    
    date_str = curated["date_str"]
    edition_num = curated["edition_num"]
    article = curated["article_body"]
    audio_summary = curated["audio_script"]
    topics_to_record = curated["topics_to_record"]

    print(f"✨ [Curadoria Concluída] Edição {edition_num} ({date_str}) gerada com sucesso!")
    print(f"📝 Título: {curated.get('headline')}")

    # 3. Dispara para o grupo de WhatsApp I.A. - Nível 01 e grava no SQLite
    res = await publish_informe_ia(
        date_str=date_str,
        edition_num=edition_num,
        article_text=article,
        audio_summary_text=audio_summary,
        topics_to_record=topics_to_record
    )
    print("✅ [Disparo WhatsApp I.A. Concluído]:", res)

if __name__ == "__main__":
    asyncio.run(main())
