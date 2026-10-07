import asyncio
import sys
import os
import logging

sys.path.append("/root/agp-publisher")
from engines.ai_bulletin_service import publish_informe_ia, get_recent_ai_topics
from engines.ai_curator_engine import generate_daily_ai_bulletin_async

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

async def main():
    logging.info("🚀 [AI Bulletin Runner] Iniciando curadoria autônoma com citações determinísticas e validação anti-404...")
    
    # 1. Recupera histórico das últimas 24 horas gravado no SQLite
    try:
        recent_topics = await get_recent_ai_topics()
        logging.info(f"📋 [Histórico 24h] {len(recent_topics)} tópicos já abordados encontrados.")
    except Exception as e:
        logging.error(f"⚠️ Erro ao consultar histórico no SQLite: {e}")
        recent_topics = []

    # 2. Executa a curadoria inteligente com busca ao vivo e validação nativa de links
    try:
        curated = await generate_daily_ai_bulletin_async(recent_topics)
    except Exception as e:
        logging.critical(f"🛑 [Abortando Disparo] Falha crítica durante a curadoria: {e}")
        sys.exit(1)

    # Salvaguarda de Sanidade: validação pré-disparo
    article = curated.get("article_body", "")
    audio_summary = curated.get("audio_script", "")
    date_str = curated.get("date_str", "")
    edition_num = curated.get("edition_num", "")
    topics_to_record = curated.get("topics_to_record", [])

    if not article or not audio_summary:
        logging.critical("🛑 [Abortando Disparo] Conteúdo do artigo ou áudio gerado está vazio. Prevenindo disparo corrompido.")
        sys.exit(1)

    if "[FONTE_" in article:
        logging.critical("🛑 [Abortando Disparo] Detectada tag órfã [FONTE_X] não mapeada no artigo. Abortando para evitar link corrompido.")
        sys.exit(1)

    logging.info(f"✨ [Curadoria Concluída] Edição {edition_num} ({date_str}) validada!")
    logging.info(f"📝 Título: {curated.get('headline')}")

    # 3. Dispara para o grupo de WhatsApp I.A. - Nível 01 e grava no SQLite
    try:
        res = await publish_informe_ia(
            date_str=date_str,
            edition_num=edition_num,
            article_text=article,
            audio_summary_text=audio_summary,
            topics_to_record=topics_to_record
        )
        logging.info(f"✅ [Disparo WhatsApp I.A. Concluído]: {res}")
    except Exception as e:
        logging.error(f"❌ Erro durante o disparo via Evolution API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
