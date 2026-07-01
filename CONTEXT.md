# Autonomous Group Publisher (AGP) - Contexto do Projeto

Sistema autônomo projetado para VPS (Arch Linux/Ubuntu) com Docker e Coolify. Originalmente concebido como um pipeline de ETL diário, o sistema está evoluindo para se tornar uma publicadora de relatórios multiplataforma (WhatsApp, Instagram, Facebook, LinkedIn, YouTube, Telegram, SMS, Email, etc.), iniciando pela **Fase 1: WhatsApp**.

O sistema pesquisa notícias/tópicos utilizando a API do Gemini, processa o conteúdo com um fluxo de 2 agentes (Redator Sênior + Auditor Factual) para evitar alucinações e erros gramaticais, gera um PDF responsivo (Mobile-First) via `xhtml2pdf` e envia para grupos/números de WhatsApp usando a **Evolution API**.

---

## 🚀 Tecnologias e Stack Implementada (Fase 1)

*   **Backend**: Python 3.11+ / FastAPI (Porta `8080` para evitar conflito com portas comuns), banco SQLite (`agp_database.db`), e motor de agendamento em segundo plano com `APScheduler`. Autenticação por tokens JWT (criptografia com `bcrypt`).
*   **Frontend**: Single-Page Application (SPA) em HTML5, Vanilla CSS e Javascript moderno (suporte a temas escuro/claro, paletas dinâmicas no local storage e marked.js para renderização de relatórios em tempo real).
*   **IA & Agentes**: Google Gemini API (modelo `gemini-2.5-pro` via SDK `google-genai`).
*   **Publicação**: Evolution API (WhatsApp) e `xhtml2pdf` para geração de relatórios físicos.
*   **Testes (Harness)**: 12 testes integrados em Pytest garantindo o cumprimento estrito das regras de compliance sintático-gramatical, plano SaaS e persistência de dados.

---

## 📦 Estrutura do Projeto

*   `backend/`:
    *   `main.py`: Orquestrador FastAPI, rotas HTTP e lógica do pipeline de agentes.
    *   `database.py`: Modelos relacionais do SQLAlchemy (User, ResearchTopic, TokenLog, PublicationHistory, SystemConfig) e migrações automatizadas no startup.
    *   `auth.py`: Utilidades de segurança, hash de senhas e JWT.
    *   `schemas.py`: Schemas Pydantic de validação de dados de entrada/saída.
    *   `scheduler_service.py`: Lógica para cálculo de intervalos e agendamentos aleatórios diários.
*   `static/`:
    *   `index.html`: Layout da interface administrativa e de usuário.
    *   `style.css`: Design system responsivo com temas de cores dinâmicos.
    *   `app.js`: Roteamento interno, requisições AJAX e controle de modais.
*   `autonomous_publisher.py`: Core do pipeline de ETL diário original (mantido intocado para o grupo principal de IA).
*   `test_suite.py`: Suíte com 12 testes automatizados.
*   `requirements.txt`: Dependências do sistema.

---

## 👮 Regras de Negócio e Compliance Estritas
1.  **Pronomes Oblíquos**: Proibido iniciar sentenças ou parágrafos com "Me", "Te", "Se", "Nos", "Vos".
2.  **Cabeçalho Obrigatório**:
    ```markdown
    # I.A. Nível 01 - {Nome do Tópico}
    ## José S.O. Junior (43) 9 8859-7348
    🔗 **Grupo de WhatsApp:** [Acesse aqui]({LINK_GROUP})
    **Data:** {current_date}
    ```
3.  **Assinatura Obrigatória**: O documento deve terminar exatamente com a frase isolada `"Até a próxima edição."`
4.  **Cores do PDF**: Fundo branco, texto em `#333333` (Graphite), títulos em `#1E3A8A` (Deep Blue), links em `#2563EB` (Blue).

---

## 🛠️ Novas Funcionalidades e Ajustes Implementados (01/07/2026)

1.  **Grounding Híbrido (Banco Central do Brasil)**:
    *   Quando um tópico envolve Dólar/PTAX, o backend consome as APIs oficiais do BCB buscando a cotação PTAX diária real e as projeções consensuais do Relatório Focus (Dólar Futuro). Esses dados são injetados como fatos irrefutáveis na memória dos agentes para eliminar qualquer risco de alucinação de taxas cambiais.
2.  **Matriz de Envio & Sanitização**:
    *   Suporte a múltiplos destinatários de WhatsApp separados por vírgula.
    *   Sanitização de destinos: formata números diretos para `@s.whatsapp.net` e grupos para `@g.us` automaticamente.
3.  **Filtros de Período Temporal**:
    *   Configuração de escopo de pesquisa (Últimas 24h, Última Semana, Último Mês, Ano Atual) na criação/edição do tópico para evitar dados históricos obsoletos.
4.  **Análise de Qualidade do Relatório**:
    *   Armazenamento do Markdown gerado no histórico e botão "🔍 Ver Conteúdo" na tabela do painel do usuário para visualização e revisão HTML instantânea antes de baixar o PDF.
5.  **Ajuste de Conectividade**:
    *   Porta do servidor alterada de `8000` para `8080` para evitar conflito com servidores de Django ou outras APIs locais.
    *   Timeout estendido para 90 segundos para prevenir falhas de leitura (Read Timeout) ao enviar PDFs pesados pela Evolution API.
