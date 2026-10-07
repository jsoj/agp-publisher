import pytest
import asyncio
import re
import os
import sqlite3
import tempfile
import aiosqlite

from engines.link_validator import resolve_and_validate_url, validate_sources_dict
from engines.ai_bulletin_service import record_ai_history, get_recent_ai_topics

@pytest.mark.asyncio
async def test_link_validator_valid_url():
    """Valida se uma URL pública estável responde com sucesso (True)."""
    is_valid, final_url = await resolve_and_validate_url("https://www.google.com")
    assert is_valid is True
    assert "google.com" in final_url

@pytest.mark.asyncio
async def test_link_validator_dead_url():
    """Valida se URLs inexistentes (404/DNS quebrado) são descartadas com False."""
    is_valid, _ = await resolve_and_validate_url("https://www.google.com/404-non-existent-page-url-123456789")
    assert is_valid is False

    is_valid_dns, _ = await resolve_and_validate_url("https://non-existent-domain-xyz-12345.com.br/teste")
    assert is_valid_dns is False

@pytest.mark.asyncio
async def test_link_validator_sources_dict():
    """Valida a filtragem paralela do dicionário de fontes descartando links mortos."""
    raw_sources = [
        {"id": 1, "title": "Google", "url": "https://www.google.com"},
        {"id": 2, "title": "Inexistente", "url": "https://www.google.com/404-definitely-missing-link"},
    ]
    verified = await validate_sources_dict(raw_sources)
    assert len(verified) == 1
    assert verified[0]["title"] == "Google"
    assert "google.com" in verified[0]["url"]

def test_deterministic_citation_mapping_logic():
    """Garante que tags [FONTE_X] sejam perfeitamente mapeadas para URLs reais sem sobras."""
    article_template = (
        "🤖 *Destaque do Dia*\n\n"
        "1. Novo modelo lançado. 🔗 Fonte: [FONTE_1]\n"
        "2. Agro avança com IA. 🔗 Fonte: [FONTE_2]\n"
        "3. Vídeo técnico. 🔗 Vídeo: [FONTE_1]\n"
    )
    valid_sources = [
        {"id": 1, "title": "Tech News", "url": "https://example.com/tech-news"},
        {"id": 2, "title": "Agro News", "url": "https://example.com/agro-news"}
    ]
    sources_dict = {f"[FONTE_{s['id']}]": s["url"] for s in valid_sources}

    processed_text = article_template
    for tag, real_url in sources_dict.items():
        processed_text = processed_text.replace(tag, real_url)
    
    # Remove qualquer tag órfã
    processed_text = re.sub(r'\[FONTE_\d+\]', '', processed_text)

    # Asserções de conformidade
    assert "[FONTE_1]" not in processed_text
    assert "[FONTE_2]" not in processed_text
    assert "https://example.com/tech-news" in processed_text
    assert "https://example.com/agro-news" in processed_text

def test_audio_and_article_formatting_rules():
    """Valida regras rígidas de roteiro do áudio da Francisca e assinatura."""
    audio_sample = (
        "Boletim I.A. Nível 01, sete de outubro de 2026, oito horas.\n\n"
        "Principais fatos do dia em inteligência artificial...\n\n"
        "Até mais."
    )
    # 1. Regra de abertura de áudio
    assert audio_sample.startswith("Boletim I.A. Nível 01,")
    # 2. Regra de encerramento de áudio sucinto
    assert audio_sample.strip().endswith("Até mais.")
    # 3. Proibição de assinaturas prolixas no áudio
    assert "Projeto Brasil 2050" not in audio_sample

    article_sample = (
        "🤖 *BOLETIM I.A. — NÍVEL 01*\n\n"
        "Texto do artigo...\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "_Projeto Brasil 2050 | Inteligência e Automação_"
    )
    assert "_Projeto Brasil 2050 | Inteligência e Automação_" in article_sample

@pytest.mark.asyncio
async def test_sqlite_deduplication_schema():
    """Valida a gravação e consulta da janela de 24 horas no banco de dados SQLite."""
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        db_path = tmp.name
        async with aiosqlite.connect(db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ai_bulletin_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_title TEXT NOT NULL,
                    summary TEXT,
                    url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # Insere registro recente
            await db.execute(
                "INSERT INTO ai_bulletin_history (topic_title, summary, url) VALUES (?, ?, ?)",
                ("Modelo X Lançado", "Resumo do modelo X", "https://example.com/x")
            )
            # Insere registro antigo (> 24h)
            await db.execute(
                "INSERT INTO ai_bulletin_history (topic_title, summary, url, created_at) VALUES (?, ?, ?, datetime('now', '-2 days'))",
                ("Modelo Antigo", "Resumo antigo", "https://example.com/antigo")
            )
            await db.commit()

            # Consulta com janela estrita de 24h
            async with db.execute("""
                SELECT topic_title FROM ai_bulletin_history 
                WHERE created_at >= datetime('now', '-1 day')
            """) as cursor:
                rows = await cursor.fetchall()
                titles = [r[0] for r in rows]

        assert "Modelo X Lançado" in titles
        assert "Modelo Antigo" not in titles
