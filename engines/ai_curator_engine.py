import asyncio
import os
import json
import re
from datetime import datetime
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    from dotenv import load_dotenv
    load_dotenv("/root/whatsapp-ai-assistant/.env")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_daily_ai_bulletin(recent_topics_history: list[str]) -> dict:
    """
    Gera de forma 100% autônoma, verdadeira e fundamentada em pesquisa ao vivo (Google Search Grounding)
    o Boletim Diário de I.A., cobrindo estritamente as últimas 24 horas e abordando obrigatoriamente
    novos lançamentos de modelos de LLMs, ferramentas e aplicações no agronegócio/Brasil.
    """
    now = datetime.now()
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    date_str = f"{now.day:02d} de {meses[now.month]} de {now.year}"
    edition_num = f"{now.strftime('%Y%m%d')}"

    client = genai.Client(api_key=GEMINI_API_KEY)

    history_str = "\n".join([f"- {t}" for t in recent_topics_history]) if recent_topics_history else "Nenhum tópico nas últimas 24h."

    # ETAPA 1: Pesquisa fundamentada com Google Search Grounding (Texto Livre para evitar quebras)
    research_prompt = f"""Você é o analista sênior de inteligência artificial do Projeto Brasil 2050.
Hoje é exatamente {date_str}.

Pesquise e sintetize os principais lançamentos e fatos mundiais e brasileiros de IA ocorridos ESTRITAMENTE NAS ÚLTIMAS 24 HORAS.

REGRAS:
1. DEDUPLICAÇÃO ESTRITA: Ignore totalmente e não cite estes tópicos recentes:
{history_str}
2. OBRIGATÓRIO: Pelo menos um lançamento de modelo ou ferramenta de ponta (Google Gemini, OpenAI, Anthropic Claude, Meta, Qwen, Mistral ou open-source de fronteira).
3. CONTEXTO BRASIL / AGRO: Inclua casos práticos relevantes no Brasil ou agronegócio.
4. Forneça os links e fatos verificados.
"""

    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    research_response = chat.send_message(research_prompt)
    research_text = research_response.text

    # ETAPA 2: Formatação estruturada em JSON sem Search Tool (100% à prova de falhas de parsing)
    format_prompt = f"""Com base na pesquisa factual abaixo realizada hoje ({date_str}), monte o Boletim I.A. oficial.

PESQUISA COLETADA:
{research_text}

DIRETRIZES DE FORMATAÇÃO:
1. Artigo de WhatsApp (article_body):
   - Título em negrito com emoji no topo.
   - Parágrafo de abertura executivo sobre as últimas 24h.
   - 3 tópicos numerados com título, síntese analítica e URL real da fonte.
   - Recomendação de vídeo técnico do YouTube se aplicável.
   - Assinatura no final: '_Projeto Brasil 2050 | Inteligência e Automação_'
   - ATENÇÃO: Desative preview de links no texto.
2. Roteiro do Áudio da Francisca (audio_script):
   - Inicie EXATAMENTE com: "Boletim I.A. Nível 01, {date_str.lower()}, oito horas."
   - Notícias diretas e tom profissional.
   - Termine APENAS com: "Até mais." (SEM assinatura institucional ou créditos).

Retorne em formato JSON estruturado com os campos:
- headline (string)
- article_body (string)
- audio_script (string)
- topics_to_record (lista de objetos com 'title', 'summary', 'url')
"""

    struct_resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=format_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    clean_text = struct_resp.text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()

    data = json.loads(clean_text)
    data["date_str"] = date_str
    data["edition_num"] = edition_num
    return data
