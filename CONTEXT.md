# Autonomous Group Publisher (AGP)
Sistema autônomo projetado para VPS (Arch Linux/Ubuntu) com Docker e Coolify. O sistema pesquisa notícias diariamente utilizando a API do Gemini com Google Search Grounding, processa o conteúdo com um fluxo multi-agentes (Redator Sênior + Auditor Factual) para evitar alucinações e erros gramaticais, gera um PDF responsivo (Mobile-First) e envia para um grupo de WhatsApp.
## 🚀 Tecnologias Utilizadas
Python 3.11+
Google Gemini API (Modelos: gemini-2.5-pro para busca com Search Grounding, redação e auditoria final utilizando o SDK google-genai)
xhtml2pdf & Markdown (Geração de PDFs formatados)
Pytest (Metodologia Harness para testes de regras de negócio)
Docker & Docker Compose (Infraestrutura isolada)
## 📦 Estrutura de Arquivos
README.md: Este manual.
architecture.md: Documentação de arquitetura, engenharia de prompts e design patterns.
docker-compose.yml: Receita de infraestrutura para subir o projeto e o banco de dados.
autonomous_publisher.py: O núcleo do sistema, contendo o pipeline ETL completo e integração com IA.
test_suite.py: Suíte de testes automatizados para garantir a qualidade do texto e geração do PDF.
## 🛠️ Como Executar
Instale as dependências locais ou utilize o Docker:
pip install google-genai xhtml2pdf markdown requests pytest


Configure as variáveis de ambiente (idealmente num arquivo .env):
export GEMINI_API_KEY="sua_chave_aqui"
export WHATSAPP_API_URL="[http://sua-instancia-evolution-api.local/message/sendMedia](http://sua-instancia-evolution-api.local/message/sendMedia)"
export WHATSAPP_API_TOKEN="seu_token_aqui"
export WHATSAPP_GROUP_ID="120363000000000000@g.us"


Execute o script principal:
python autonomous_publisher.py


Para rodar os testes da metodologia Harness:
pytest test_suite.py -v


