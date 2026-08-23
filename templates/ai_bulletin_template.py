def render_ai_bulletin_html(date_str: str, edition_num: str, highlights: list[dict], deep_dive: dict) -> str:
    """Gera HTML e CSS diagramado para o Boletim I.A. Nível 01 (Newsletter + PDF)."""
    
    highlights_html = ""
    for i, item in enumerate(highlights, 1):
        highlights_html += f"""
        <div style="margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #e2e8f0;">
            <div style="font-size: 11px; font-weight: 700; color: #0f5132; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 3px;">
                {item.get('category', 'RADAR I.A.')}
            </div>
            <h3 style="font-size: 15px; font-weight: 700; color: #061325; margin: 0 0 4px 0;">
                {i}. {item['title']}
            </h3>
            <p style="font-size: 13px; line-height: 1.5; color: #334155; margin: 0 0 4px 0;">
                {item['summary']}
            </p>
            <a href="{item['url']}" style="color: #0c2340; font-size: 12px; font-weight: 600; text-decoration: underline;">
                Ver detalhes &rarr;
            </a>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
    @page {{
        size: A4;
        margin: 1.5cm;
    }}
    body {{
        font-family: Helvetica, Arial, sans-serif;
        color: #1e293b;
        margin: 0;
        padding: 0;
        background-color: #ffffff;
    }}
    .header {{
        background-color: #061325;
        color: #ffffff;
        padding: 24px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 20px;
    }}
    .tagline {{
        color: #c99a2c;
        font-size: 10px;
        font-weight: bold;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }}
    .title {{
        font-size: 22px;
        font-weight: bold;
        margin: 0 0 6px 0;
        color: #ffffff;
    }}
    .subtitle {{
        font-size: 12px;
        color: #94a3b8;
    }}
    .section-title {{
        font-size: 15px;
        font-weight: bold;
        color: #0c2340;
        border-bottom: 2px solid #0f5132;
        padding-bottom: 4px;
        margin-top: 20px;
        margin-bottom: 12px;
    }}
    .deep-dive-card {{
        background-color: #f8fafc;
        border-left: 4px solid #c99a2c;
        padding: 16px;
        border-radius: 6px;
        margin-bottom: 20px;
    }}
    .footer {{
        margin-top: 25px;
        padding-top: 10px;
        border-top: 1px solid #e2e8f0;
        text-align: center;
        font-size: 11px;
        color: #64748b;
    }}
</style>
</head>
<body>
    <div class="header">
        <div class="tagline">INTELIGÊNCIA ARTIFICIAL &bull; BOLETIM EXECUTIVO</div>
        <div class="title">Boletim I.A. Nível 01</div>
        <div class="subtitle">Edição #{edition_num} &bull; {date_str}</div>
    </div>

    <div class="section-title">DESTAQUE DO DIA (DEEP DIVE)</div>
    <div class="deep-dive-card">
        <h2 style="font-size: 16px; color: #061325; margin: 0 0 6px 0;">{deep_dive['title']}</h2>
        <p style="font-size: 13px; line-height: 1.6; color: #334155; margin: 0 0 8px 0;">
            {deep_dive['content']}
        </p>
        <div style="font-size: 12px; color: #0f5132; font-weight: bold;">Impacto Prático: {deep_dive.get('impact', 'Otimização operacional e automação avançada.')}</div>
    </div>

    <div class="section-title">RADAR DE INOVAÇÕES & TENDÊNCIAS</div>
    {highlights_html}

    <div class="footer">
        <strong>Projeto Brasil 2050</strong> &bull; Centro de Inteligência e Automação Agêntica<br>
        Acesse: projetobrasil2050.site
    </div>
</body>
</html>"""
