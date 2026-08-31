import asyncio
import sys
import os

sys.path.append("/root/agp-publisher")
from engines.ai_bulletin_service import publish_informe_ia

async def run():
    date_str = "31 de Agosto de 2026"
    edition_num = "02"

    article = (
        "🤖 *Novos LLMs, Assistentes de Campo e Regulação Global de IA*\n\n"
        "O ecossistema de Inteligência Artificial fecha agosto de 2026 com avanços expressivos em ferramentas práticas para o agronegócio nacional e novos marcos regulatórios internacionais para os grandes modelos de linguagem.\n\n"
        "📌 *Principais Destaques das Últimas 48 Horas:*\n\n"
        "1. *Lançamento do 'JoIA' (CNA) no Brasil:*\n"
        "A Confederação da Agricultura e Pecuária do Brasil oficializou o 'JoIA', um assistente de IA generativa via WhatsApp alimentado com a base de dados do projeto Campo Futuro, auxiliando produtores em decisões de custo operacional e gestão de safra.\n"
        "🔗 Fonte: https://www.cnabrasil.org.br\n\n"
        "2. *Pacto Global de Ciberdefesa em IA:*\n"
        "Mais de 100 gigantes da tecnologia (OpenAI, Anthropic, Google e Microsoft) assinaram um manifesto conjunto por defesas cibernéticas contra ataques automatizados de IA em infraestruturas críticas e serviços essenciais.\n"
        "🔗 Fonte: https://www.reuters.com\n\n"
        "3. *União Europeia Enquadra o ChatGPT em Novas Regras:*\n"
        "A Comissão Europeia classificou oficialmente o ChatGPT como 'Mecanismo de Busca Muito Grande' sob a Lei de Serviços Digitais (DSA), exigindo auditorias estritas contra riscos sistêmicos e desinformação.\n"
        "🔗 Fonte: https://ec.europa.eu\n\n"
        "4. *AgroTech 2026 e Agricultura Prescritiva:*\n"
        "Encerramento da AgroTech Brasília e debates da Embrapa Agricultura Digital reforçaram que 83% das agtechs brasileiras já utilizam IA, acelerando a transição da análise preditiva para a tomada de ação automatizada no campo.\n"
        "🔗 Fonte: https://www.embrapa.br"
    )

    audio_summary = (
        "Boletim I.A. Nível 01, Projeto Brasil 2050. Edição de 31 de agosto de 2026.\n\n"
        "Nesta edição, destacamos o lançamento do assistente de inteligência artificial JoIA pela CNA no Brasil, levando consultoria técnica de custos e safra aos produtores rurais via WhatsApp com dados do Campo Futuro.\n\n"
        "No cenário internacional, mais de cem grandes empresas de tecnologia, incluindo Google, OpenAI e Anthropic, firmaram um pacto global por ciberdefesa preventiva contra ataques autônomos de inteligência artificial.\n\n"
        "Ao mesmo tempo, a União Europeia enquadrou o ChatGPT em regras rigorosas de transparência da Lei de Serviços Digitais, enquanto a Embrapa reforça que mais de oitenta por cento das agtechs nacionais já operam com IA no campo.\n\n"
        "Informações apuradas com base em dados da CNA Brasil, Embrapa, Reuters e Comissão Europeia.\n\n"
        "Este é o boletim executivo do Projeto Brasil 2050."
    )

    topics = [
        {
            "title": "Lançamento do assistente JoIA pela CNA no WhatsApp",
            "summary": "IA generativa para produtores rurais com base de dados do Campo Futuro.",
            "url": "https://www.cnabrasil.org.br"
        },
        {
            "title": "Pacto Global de Ciberdefesa e Enquadramento do ChatGPT na UE",
            "summary": "Defesa cibernética em IA e regulação rigorosa da DSA europeia.",
            "url": "https://www.reuters.com"
        }
    ]

    res = await publish_informe_ia(
        date_str=date_str,
        edition_num=edition_num,
        article_text=article,
        audio_summary_text=audio_summary,
        topics_to_record=topics
    )
    print("DISPATCH_RESULT:", res)

if __name__ == "__main__":
    asyncio.run(run())
