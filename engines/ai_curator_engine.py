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

    prompt = f"""Você é o editor-chefe executivo de Inteligência Artificial do Projeto Brasil 2050.
Hoje é exatamente {date_str}.

Sua missão é realizar uma curadoria aprofundada com pesquisa ao vivo das novidades MUNDIAIS e NACIONAIS de Inteligência Artificial ocorridas ESTRITAMENTE NAS ÚLTIMAS 24 HORAS.

REGRAS CRÍTICAS E OBRIGATÓRIAS:
1. DEDICAÇÃO A FATOS VERDADEIROS E FONTES: Apenas notícias reais e verificadas.
2. DEDUPLICAÇÃO ESTRITA: NÃO mencione nem repita nenhum destes tópicos já enviados nas últimas 24 horas:
{history_str}
3. LANÇAMENTO DE NOVOS MODELOS/LLMS (OBRIGATÓRIO): Pelo menos um item DEVE ser sobre lançamento recente de modelos (ex: novos LLMs do Google como Gemini 3.8 Flash, OpenAI, Anthropic, Qwen, Meta ou modelos open-source de fronteira).
4. CONTEXTO BRASIL / AGRO: Inclua casos práticos e relevantes de IA no Brasil ou no agronegócio.
5. FORMATAÇÃO DO TEXTO DO ARTIGO (WhatsApp):
   - Inicie com o título geral do dia em negrito com emoji.
   - Um parágrafo executivo introduzindo o panorama das últimas 24h.
   - 3 a 4 tópicos numerados com título em itálico/negrito, descrição analítica e link real da fonte.
   - Inclua uma recomendação de vídeo técnico do YouTube ao final se houver.
   - NÃO inclua assinatura corporativa longa dentro do texto além de '_Projeto Brasil 2050 | Inteligência e Automação_'.
6. FORMATAÇÃO DO ÁUDIO (Francisca):
   - DEVE INICIAR DIRETAMENTE com: "Boletim I.A. Nível 01, {date_str.lower()}, oito horas."
   - Seguir imediatamente para as notícias sem rodeios nem cumprimentos prolixos.
   - O encerramento DEVE SER APENAS: "Até mais." (SEM assinaturas ou créditos no áudio).

Retorne sua resposta EXCLUSIVAMENTE em formato JSON estruturado com esta chave:
{{
  "headline": "Título do artigo",
  "article_body": "Texto completo formatado para WhatsApp",
  "audio_script": "Texto exato a ser falado pela Francisca",
  "topics_to_record": [
     {{"title": "Título do tópico 1", "summary": "Resumo do tópico 1", "url": "URL da fonte"}},
     {{"title": "Título do tópico 2", "summary": "Resumo do tópico 2", "url": "URL da fonte"}}
  ]
}}
"""

    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    response = chat.send_message(prompt)

    try:
        data = json.loads(response.text)
    except Exception as err:
        # Extrai JSON de blocos markdown se necessário
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
        else:
            raise RuntimeError(f"Erro ao decodificar JSON gerado: {response.text[:300]}")

    data["date_str"] = date_str
    data["edition_num"] = edition_num
    return data
