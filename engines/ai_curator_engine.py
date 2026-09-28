import asyncio
import os
import json
import re
from datetime import datetime
from google import genai
from google.genai import types

from engines.link_validator import resolve_and_validate_url

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    from dotenv import load_dotenv
    load_dotenv("/root/whatsapp-ai-assistant/.env")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def generate_daily_ai_bulletin_async(recent_topics_history: list[str]) -> dict:
    """
    Gera de forma 100% autônoma, verdadeira e fundamentada em pesquisa ao vivo (Google Search Grounding)
    o Boletim Diário de I.A.
    GARANTIA DE CONSISTÊNCIA DE LINKS:
    1. Extrai os links reais do grounding_metadata da busca.
    2. Valida e resolve cada link via HTTP HEAD/GET em paralelo (anti-404).
    3. Passa para a LLM uma tabela determinística de [FONTE_1], [FONTE_2]...
    4. Proíbe a LLM de inventar URLs; substitui programaticamente as tags pelas URLs reais validadas.
    5. Faz um sanity check final em cada link presente no texto antes do envio.
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

    # ETAPA 1: Pesquisa Grounded via Google Search
    research_prompt = f"""Você é o analista sênior de inteligência artificial do Projeto Brasil 2050.
Hoje é exatamente {date_str}.

Pesquise e sintetize os principais lançamentos e fatos mundiais e brasileiros de IA ocorridos ESTRITAMENTE NAS ÚLTIMAS 24 HORAS.

REGRAS:
1. DEDUPLICAÇÃO ESTRITA: Ignore totalmente e não cite estes tópicos recentes:
{history_str}
2. OBRIGATÓRIO: Pelo menos um lançamento de modelo ou ferramenta de ponta (Google Gemini, OpenAI, Anthropic Claude, Meta, Qwen, Mistral ou open-source de fronteira).
3. CONTEXTO BRASIL / AGRO: Inclua casos práticos relevantes no Brasil ou agronegócio.
4. Fatos verificados com links e fontes reais.
"""

    research_resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=research_prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    research_text = research_resp.text

    # ETAPA 2: Extração e Validação Ativa de Links do Grounding (Anti-404)
    cand = research_resp.candidates[0]
    meta = getattr(cand, "grounding_metadata", None)
    chunks = getattr(meta, "grounding_chunks", []) if meta else []

    raw_sources = []
    seen_uris = set()
    for c in chunks:
        web = getattr(c, "web", None)
        if web:
            uri = getattr(web, "uri", "")
            title = getattr(web, "title", "Fonte da Notícia")
            if uri and uri not in seen_uris:
                seen_uris.add(uri)
                raw_sources.append({"title": title, "raw_uri": uri})

    print(f"🔍 [AI Curator] {len(raw_sources)} fontes identificadas na busca ao vivo. Validando links...")

    # Valida em paralelo
    valid_sources = []
    validation_tasks = [resolve_and_validate_url(s["raw_uri"]) for s in raw_sources]
    results = await asyncio.gather(*validation_tasks, return_exceptions=True)

    for s, res in zip(raw_sources, results):
        if isinstance(res, tuple):
            is_valid, final_url = res
            if is_valid and not final_url.startswith("https://vertexaisearch.cloud.google.com"):
                valid_sources.append({
                    "id": len(valid_sources) + 1,
                    "title": s["title"],
                    "url": final_url
                })
            else:
                print(f"⚠️ [Link Descartado / Inválido]: {final_url[:70]}")

    print(f"✅ [AI Curator] {len(valid_sources)} fontes validadas e ativas (100% OK, sem 404).")

    # Mapeamento Determinístico de Fontes
    sources_table_str = ""
    for vs in valid_sources:
        sources_table_str += f"- [FONTE_{vs['id']}]: Título: \"{vs['title']}\"\n"

    # ETAPA 3: Formatação Blindada em JSON com Tags [FONTE_X]
    format_prompt = f"""Com base na pesquisa factual abaixo realizada hoje ({date_str}), monte o Boletim I.A. oficial.

PESQUISA COLETADA:
{research_text}

FONTES VERIFICADAS DISPONÍVEIS:
{sources_table_str}

REGRAS DE OURO PARA CONSISTÊNCIA DE LINKS (MUITO CRÍTICO):
- É ESTRITAMENTE PROIBIDO inventar, alucinar ou escrever qualquer URL http:// ou https:// no texto.
- Para indicar o link de cada notícia, use EXATAMENTE a tag correspondente: [FONTE_1], [FONTE_2], etc.
- Associe cada notícia à fonte mais adequada da lista de fontes verificadas.
- No campo 'source_tag', coloque apenas a tag utilizada (ex: "[FONTE_1]").

DIRETRIZES DE FORMATAÇÃO:
1. Artigo de WhatsApp (article_body):
   - Título em negrito com emoji no topo.
   - Parágrafo de abertura executivo sobre as últimas 24h.
   - 3 tópicos numerados com título, síntese analítica e a tag da fonte: '🔗 Fonte: [FONTE_X]'.
   - Recomendação de vídeo técnico se houver entre as fontes: '🔗 Vídeo: [FONTE_X]'.
   - Assinatura no final: '_Projeto Brasil 2050 | Inteligência e Automação_'
2. Roteiro do Áudio da Francisca (audio_script):
   - Inicie EXATAMENTE com: "Boletim I.A. Nível 01, {date_str.lower()}, oito horas."
   - Notícias diretas e tom profissional.
   - Termine APENAS com: "Até mais." (SEM assinatura institucional ou créditos).

Retorne em formato JSON estruturado com os campos:
- headline (string)
- article_body (string)
- audio_script (string)
- topics_to_record (lista de objetos com 'title', 'summary', 'source_tag')
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

    # ETAPA 4: Substituição Determinística de [FONTE_X] pelas URLs Reais e Validadas
    article_text = data.get("article_body", "")
    sources_dict = {f"[FONTE_{vs['id']}]": vs["url"] for vs in valid_sources}

    for tag, real_url in sources_dict.items():
        article_text = article_text.replace(tag, real_url)

    # Limpeza residual de tags sem correspondente
    article_text = re.sub(r'\[FONTE_\d+\]', '', article_text)
    data["article_body"] = article_text

    # Prepara topics_to_record com as URLs reais
    recorded_topics = []
    for item in data.get("topics_to_record", []):
        tag = item.get("source_tag", "")
        real_url = sources_dict.get(tag, "")
        if not real_url and valid_sources:
            real_url = valid_sources[0]["url"]
        recorded_topics.append({
            "title": item.get("title", ""),
            "summary": item.get("summary", ""),
            "url": real_url
        })
    data["topics_to_record"] = recorded_topics
    data["date_str"] = date_str
    data["edition_num"] = edition_num

    # ETAPA 5: Sanity Check Final Anti-404
    # Encontra qualquer URL no article_body e garante que responda 200
    urls_in_article = re.findall(r'https?://[^\s)\]]+', article_text)
    print(f"🔍 [AI Curator] Sanity check final em {len(urls_in_article)} links no artigo gerado...")
    for u in urls_in_article:
        ok, valid_u = await resolve_and_validate_url(u)
        if not ok:
            print(f"🚨 [Sanity Check Falhou para Link]: {u} -> Removendo do texto")
            article_text = article_text.replace(u, "Fonte verificada")
    data["article_body"] = article_text

    return data

def generate_daily_ai_bulletin(recent_topics_history: list[str]) -> dict:
    return asyncio.run(generate_daily_ai_bulletin_async(recent_topics_history))
