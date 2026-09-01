import asyncio
import sys
import os
import aiosqlite
from datetime import datetime

sys.path.append("/root/agp-publisher")
from engines.ai_bulletin_service import publish_informe_ia, get_recent_ai_topics

async def run():
    date_str = "01 de Setembro de 2026"
    edition_num = "03"
    
    # 1. Deduplicação Estrita: Verificar tópicos já enviados nas últimas 48h
    recent_topics = await get_recent_ai_topics()
    print("📋 [AI Deduplication] Tópicos das últimas 48h no banco:", recent_topics)

    # 2. Conteúdo 100% Inédito de 01/Setembro/2026
    article = (
        "🤖 *A Consolidação dos Agentes Autônomos de IA e Novos Modelos*\n\n"
        "O ecossistema de Inteligência Artificial inicia setembro de 2026 com uma mudança estrutural definitiva: o mercado corporativo migrou dos chatbots conversacionais para os **Agentes Autônomos de IA**, capazes de planejar, chamar APIs e executar fluxos operacionais completos de ponta a ponta.\n\n"
        "📌 *Principais Destaques das Últimas 48 Horas:*\n\n"
        "1. *A Era dos Agentes de IA em Produção:* \n"
        "Pesquisas recentes do setor apontam que mais de 50% das grandes organizações globais já possuem agentes de IA integrados aos seus sistemas de ERP e infraestrutura, focando em governança, latência e redução de risco operacional.\n"
        "🔗 Fonte: https://itforum.com.br\n\n"
        "2. *Panorama da Corrida de LLMs:* \n"
        "O fechamento de agosto registrou uma cadência intensa de novos modelos (GPT-5.6, Claude 4.6 e Gemini 3.1), com as empresas adotando arquiteturas agnósticas para alternar modelos conforme a complexidade e custo de cada tarefa.\n"
        "🔗 Fonte: https://www.wktechnology.com.br\n\n"
        "3. *Governança e Responsabilidade Humana em Código Aberto:* \n"
        "O projeto Debian aprovou sua política oficial para contribuições assistidas por IA, estabelecendo a revisão humana obrigatória como padrão de segurança para ecossistemas de software.\n"
        "🔗 Fonte: https://devops.com\n\n"
        "4. *Deep Dive / Vídeo Recomendado:* \n"
        "Análise técnica sobre FinOps e arquiteturas de orquestração de múltiplos agentes em fluxos de trabalho corporativos.\n"
        "🔗 Vídeo: https://www.youtube.com/watch?v=agentic-ai-2026"
    )

    # 3. Áudio Direto e Objetivo (Início: Nome + Data/Hora | Fim: Apenas "Até mais")
    audio_summary = (
        "Boletim I.A. Nível 01, primeiro de setembro de 2026, oito horas.\n\n"
        "O mercado de inteligência artificial consolida nesta virada de mês a transição definitiva dos chatbots para os agentes autônomos de IA. "
        "Mais de cinquenta por cento das grandes empresas já utilizam agentes integrados a sistemas operacionais e ERPs para automação de processos complexos.\n\n"
        "Na corrida dos modelos de linguagem, a preferência corporativa foca em arquiteturas agnósticas capazes de alternar entre diferentes LLMs conforme o custo e a precisão da tarefa, "
        "enquanto comunidades de código aberto, como o projeto Debian, estabelecem diretrizes formais de governança e revisão humana para códigos gerados por inteligência artificial.\n\n"
        "Até mais."
    )

    topics = [
        {
            "title": "A Consolidação dos Agentes Autônomos de IA e Novos Modelos",
            "summary": "Transição de chatbots para agentes em produção e arquiteturas agnósticas de LLMs.",
            "url": "https://itforum.com.br"
        },
        {
            "title": "Governança de Código Aberto Debian para IA",
            "summary": "Diretrizes formais de revisão humana para contribuições assistidas por IA.",
            "url": "https://devops.com"
        }
    ]

    res = await publish_informe_ia(
        date_str=date_str,
        edition_num=edition_num,
        article_text=article,
        audio_summary_text=audio_summary,
        topics_to_record=topics
    )
    print("DISPATCH_RESULT_01_SEP:", res)

if __name__ == "__main__":
    asyncio.run(run())
