import os
import datetime
import markdown
import json
import sqlite3
import requests
import base64
from dotenv import load_dotenv
from xhtml2pdf import pisa
from google import genai
from google.genai import types

# ==========================================
# CONFIGURAÇÕES E CREDENCIAIS
# ==========================================
load_dotenv() # Carrega as variáveis do .env local
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "SUA_CHAVE_AQUI")
WHATSAPP_API_URL = os.environ.get("WHATSAPP_API_URL", "http://evolution-api/message/sendMedia")
WHATSAPP_API_TOKEN = os.environ.get("WHATSAPP_API_TOKEN", "SEU_TOKEN")
WHATSAPP_GROUP_ID = os.environ.get("WHATSAPP_GROUP_ID", "123456789@g.us")
DATABASE_FILE = os.environ.get("DATABASE_PATH", "agp_database.db")
LINK_GROUP = os.environ.get("LINK_GROUP", "https://chat.whatsapp.com/DJDWRobITde5Mc7SZ4De1R")

# Inicializa o cliente do novo SDK google-genai
client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================
# MÓDULO DB: REGISTRO DE EXECUÇÃO (SQLite)
# ==========================================
def init_db():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                details TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Erro ao inicializar banco de dados local: {e}")

def log_to_db(status, details):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO execution_logs (status, details) VALUES (?, ?)",
            (status, details)
        )
        conn.commit()
        conn.close()
        print(f"📝 Log de execução ({status}) salvo no SQLite local.")
    except Exception as e:
        print(f"⚠️ Erro ao salvar log no SQLite: {e}")

# ==========================================
# MÓDULO 1: COLETOR DE DADOS (COM SEARCH)
# ==========================================
class DailyCollector:
    def __init__(self):
        pass

    def fetch_daily_news(self, query):
        """Coleta informações recentes utilizando a capacidade de busca do Gemini."""
        print(f"🔍 Buscando informações sobre: {query}...")
        
        prompt = f"""
        Busque as informações e notícias mais recentes de hoje sobre: {query}.
        Foque estritamente em: lançamentos de novos modelos de IA, novas aplicações, movimentações de mercado das empresas de Inteligência Artificial e novidades do ecossistema Open Source de IA.
        Retorne os fatos principais detalhados e inclua as fontes/links obrigatórios de onde você retirou as informações.
        """
        
        # Chamada direta sem tools de busca para manter as referências e links consistentes
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt
        )
        return response.text

# ==========================================
# MÓDULO 2: SUMARIZAÇÃO MULTI-AGENTE
# ==========================================
class ExecutiveSummarizer:
    def __init__(self):
        pass

    def generate_draft(self, raw_data):
        """Agente 1: O Redator estilo Michael Lewis."""
        print("✍️  Redigindo rascunho executivo...")
        prompt = f"""
        Você é um Especialista em Inteligência Artificial e Estrategista Sênior. 
        Transforme os dados brutos a seguir em um relatório executivo de altíssimo valor.
        
        REGRAS DE FORMATAÇÃO E ESTRUTURA (OBRIGATÓRIO):
        1. O título principal deve ser EXATAMENTE: "# I.A. Nível 01"
        2. O subtítulo deve ser EXATAMENTE: "## José S.O. Junior (43) 9 8859-7348"
        3. Adicione o link do grupo: "🔗 **Grupo de WhatsApp:** [Acesse aqui]({LINK_GROUP})"
        4. Adicione a data atual: "**Data:** {datetime.date.today().strftime('%d/%m/%Y')}"
        5. NÃO escreva "De:" nem "Para:" ou "Memorando". Vá direto para o "Assunto" e o conteúdo.
        6. O texto deve ser excelente, cobrindo as últimas notícias relevantes de novos modelos, aplicações, informações sobre grandes empresas do setor e mundo open source de I.A.
        7. No final do documento, você DEVE listar todas as Referências de pesquisa (links e fontes).
        
        DADOS BRUTOS:
        {raw_data}
        """
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt
        )
        return response.text

    def audit_and_refine(self, draft_text):
        """Agente 2: O Auditor Gramatical e de Regras de Negócio."""
        print("🕵️‍♂️  Auditando e aplicando regras de compliance...")
        prompt = f"""
        Você é um Revisor e Auditor Sênior Rigoroso.
        Revise o seguinte rascunho de relatório de acordo com estas REGRAS ABSOLUTAS:
        1. NUNCA inicie uma frase ou parágrafo com o pronome oblíquo "Me", "Te", "Se", "Nos" ou "Vos". (Ex: Substitua "Me parece" por "Parece-me" ou "Nota-se").
        2. Mantenha todas as fontes, links de referências e citações. É vital que as fontes apareçam no documento final.
        3. Mantenha os cabeçalhos exatos: "# I.A. Nível 01", o subtítulo de telefone e a Data. NUNCA adicione blocos como "De/Para".
        4. O relatório DEVE terminar OBRIGATORIAMENTE com a seguinte frase exata e isolada no final: "Até a próxima edição."
        
        RASCUNHO:
        {draft_text}
        
        Retorne apenas o texto final em formato Markdown limpo, sem delimitações extras.
        """
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt
        )
        return response.text

# ==========================================
# MÓDULO 3: GERAÇÃO DE PDF (XHTML2PDF)
# ==========================================
class PDFGenerator:
    def __init__(self):
        # CSS nativo para xhtml2pdf (versão simplificada sem bibliotecas externas)
        self.css = """
        @page {
            size: a4 portrait;
            margin: 2cm;
        }
        body {
            font-family: Helvetica, Arial, sans-serif;
            color: #333333;
            font-size: 14px;
            line-height: 1.5;
        }
        h1, h2, h3 {
            color: #1E3A8A;
        }
        h1 { font-size: 20px; border-bottom: 1px solid #1E3A8A; padding-bottom: 4px; }
        h2 { font-size: 16px; margin-top: 15px; }
        p { margin-bottom: 10px; text-align: justify; }
        a { color: #2563EB; }
        ul { padding-left: 20px; }
        li { margin-bottom: 5px; }
        """

    def generate(self, markdown_text, output_filename="relatorio_diario.pdf"):
        print("📄 Gerando PDF Simplificado (xhtml2pdf)...")
        
        # Converte Markdown para HTML
        html_content = markdown.markdown(markdown_text)
        
        # Estrutura HTML completa injetando o CSS no <head>
        full_html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                {self.css}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        with open(output_filename, "w+b") as result_file:
            pisa_status = pisa.CreatePDF(full_html, dest=result_file)
            
        if pisa_status.err:
            print(f"❌ Erro ao gerar PDF: {pisa_status.err}")
        else:
            print(f"✅ PDF salvo como: {output_filename}")
            
        return output_filename

# ==========================================
# MÓDULO 4: INTEGRAÇÃO WHATSAPP API (EVOLUTION)
# ==========================================
class WhatsAppPublisher:
    def send_pdf(self, pdf_path, caption="📊 *Seu Resumo Executivo Diário chegou!*"):
        print("🚀 Publicando no WhatsApp...")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError("O arquivo PDF não foi encontrado para envio.")

        # Evolution API Base64 JSON Payload
        headers = {
            "apikey": WHATSAPP_API_TOKEN,
            "Content-Type": "application/json"
        }
        
        try:
            with open(pdf_path, "rb") as pdf_file:
                b64_content = base64.b64encode(pdf_file.read()).decode('utf-8')
                
            payload = {
                "number": WHATSAPP_GROUP_ID,
                "mediatype": "document",
                "mimetype": "application/pdf",
                "media": b64_content,
                "fileName": os.path.basename(pdf_path),
                "caption": caption
            }

            response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            print(f"✅ Publicação no WhatsApp realizada com sucesso! Código: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao publicar no WhatsApp: {e}")
            raise e

# ==========================================
# ORQUESTRADOR PRINCIPAL
# ==========================================
def main():
    print(f"=== Iniciando AGP (Modo Local + Evolution API): {datetime.date.today().strftime('%d/%m/%Y')} ===")
    init_db()
    
    try:
        # 1. Coleta
        collector = DailyCollector()
        raw_data = collector.fetch_daily_news("Últimas notícias de lançamentos de modelos de IA, open source, novas aplicações e empresas de inteligência artificial")
        
        # 2. Resumo e Auditoria
        summarizer = ExecutiveSummarizer()
        draft = summarizer.generate_draft(raw_data)
        final_text = summarizer.audit_and_refine(draft)
        
        # 3. Geração de Artefato
        pdf_gen = PDFGenerator()
        pdf_filename = f"AGP_Report_{datetime.date.today().strftime('%Y%m%d')}.pdf"
        pdf_gen.generate(final_text, pdf_filename)
        
        # 4. Publicação
        publisher = WhatsAppPublisher()
        publisher.send_pdf(pdf_filename)
        
        print("=== Fluxo concluído com sucesso! ===")
        log_to_db("SUCCESS", f"Relatório gerado e enviado para WhatsApp API: {pdf_filename}")
    except Exception as e:
        print(f"=== Fluxo falhou: {e} ===")
        log_to_db("ERROR", str(e))

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    # Apenas rodará o main() se o script for chamado diretamente
    main()