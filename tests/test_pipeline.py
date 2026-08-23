import pytest
import asyncio
import os
import sys

sys.path.append('/root/agp-publisher')

from engines.pdf_engine import PDFEngine
from templates.ai_bulletin_template import render_ai_bulletin_html
from templates.html_template import render_dolar_newsletter
from registry.db import init_db, get_db

@pytest.mark.asyncio
async def test_database_init_and_query():
    await init_db()
    db = await get_db()
    try:
        async with db.execute("SELECT COUNT(*) as total FROM bulletins") as cursor:
            row = await cursor.fetchone()
            assert row["total"] >= 2
    finally:
        await db.close()

def test_dolar_html_template_rendering():
    html = render_dolar_newsletter(
        date_str="21 de Agosto de 2026",
        cotacao="R$ 5,1440",
        variacao="-0,93%",
        min_val="R$ 5,1420",
        max_val="R$ 5,1451",
        items=[{"title": "Teste", "description": "Desc", "url": "https://teste.com", "source": "Fonte"}]
    )
    assert "PROJETO BRASIL 2050" in html
    assert "R$ 5,1440" in html
    assert "-0,93%" in html

def test_pdf_rendering_pipeline():
    html = render_ai_bulletin_html(
        date_str="23 de Agosto de 2026",
        edition_num="1",
        highlights=[{"category": "TESTE", "title": "Titulo", "summary": "Sumario", "url": "https://link.com"}],
        deep_dive={"title": "Deep Dive", "content": "Conteudo", "impact": "Impacto"}
    )
    pdf_bytes = PDFEngine.render_pdf(html)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 500
