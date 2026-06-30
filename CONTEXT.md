# Autonomous Group Publisher (AGP)

Sistema autônomo projetado para VPS (Arch Linux/Ubuntu) com Docker e Coolify. Originalmente concebido como um pipeline de ETL diário, o sistema está evoluindo para se tornar uma publicadora multiplataforma (WhatsApp, Instagram, Facebook, LinkedIn, YouTube, Telegram, SMS, Email, etc.), iniciando pela **Fase 1: WhatsApp**.

O sistema pesquisa notícias/tópicos utilizando a API do Gemini, processa o conteúdo com um fluxo multi-agentes (Pesquisa + Redação + Auditoria Factual) para evitar alucinações e erros gramaticais, gera um PDF responsivo (Mobile-First) via `xhtml2pdf` e envia para grupos/números de WhatsApp usando a **Evolution API**.

---

## 🚀 Tecnologias e Stack Proposta (Fase 1)

*   **Backend**: Python 3.11+ / FastAPI (API REST, autenticação JWT, agendamento em segundo plano com `APScheduler`).
*   **Frontend**: Vite + React + Vanilla CSS (Interface administrativa e do usuário com suporte a temas e White-Label).
*   **Banco de Dados**: SQLite (`agp_database.db`) expandido para armazenar usuários, tópicos de pesquisa, logs de tokens e histórico de execuções.
*   **IA & Agentes**: Google Gemini API (modelo `gemini-2.5-pro` via SDK `google-genai`).
*   **Publicação**: Evolution API (WhatsApp) e `xhtml2pdf` para geração de relatórios físicos.
*   **Infraestrutura**: Docker & Docker Compose para deployment simplificado em VPS (Coolify).
*   **Testes (Harness)**: Pytest para garantir o cumprimento estrito das regras de compliance sintático-gramatical e integridade estrutural.

---

## 📦 Estrutura do Projeto

*   `autonomous_publisher.py`: Core do pipeline de ETL diário e publicação. **Esta funcionalidade existente deve ser preservada intocada para o grupo principal de I.A.**
*   `scheduler.py`: Agendador original que roda o script principal diariamente às 08:00 (America/Sao_Paulo).
*   `test_suite.py`: Suíte de testes automatizados com Pytest.
*   `run_daily.bat`: Script de lote para execução em ambiente Windows.
*   `agp_database.db`: Banco SQLite local com histórico e logs.
*   `requirements.txt`: Dependências do ecossistema.

---

## 🧪 Ambiente de Teste Local (Windows)

Para fins de teste no notebook Windows, o envio do WhatsApp será direcionado para o grupo de notas pessoal:
*   **Grupo de Notas Pessoal**: `554391308954-1606733601`

---

## 👮 Regras de Negócio e Compliance Estritas
1.  **Pronomes Oblíquos**: Proibido iniciar sentenças ou parágrafos com "Me", "Te", "Se", "Nos", "Vos".
2.  **Cabeçalho Obrigatório**:
    ```markdown
    # I.A. Nível 01
    ## José S.O. Junior (43) 9 8859-7348
    🔗 **Grupo de WhatsApp:** [Acesse aqui]({LINK_GROUP})
    **Data:** {current_date}
    ```
3.  **Assinatura Obrigatória**: O documento deve terminar exatamente com a frase isolada `"Até a próxima edição."`
4.  **Cores do PDF**: Fundo branco, texto em `#333333` (Graphite), títulos em `#1E3A8A` (Deep Blue), links em `#2563EB` (Blue).
