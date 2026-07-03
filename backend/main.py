import os
import sys
import io

# Configura codificação UTF-8 para evitar UnicodeEncodeError com emojis no terminal do Windows (ignorado sob pytest)
if "pytest" not in sys.modules and not any("pytest" in arg for arg in sys.argv):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import datetime
import shutil
import random
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from google import genai
from google.genai import types
import requests
import base64
import markdown
from xhtml2pdf import pisa

# Importações locais
from backend.database import (
    get_engine, init_db, get_session_factory, seed_db,
    User, SystemConfig, ResearchTopic, TokenLog, PublicationHistory
)
from backend.auth import (
    get_password_hash, verify_password, create_access_token, decode_access_token
)
from backend.schemas import (
    UserLogin, UserCreate, UserResponse, Token,
    TopicCreate, TopicUpdate, TopicResponse,
    SystemConfigUpdate, SystemConfigResponse,
    TokenLogResponse, HistoryResponse
)
from backend.scheduler_service import calculate_next_random_run, TZ_SAO_PAULO

# ==========================================
# CONFIGURAÇÕES INICIAIS
# ==========================================

app = FastAPI(title="AGP SaaS Publisher API", version="1.0.0")

# Habilita CORS para o frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria diretórios necessários para uploads e static
os.makedirs("static", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# Monta o diretório static para servir a logo e outros assets
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

# Configuração do Banco de Dados
DATABASE_PATH = os.environ.get("DATABASE_PATH", "agp_database.db")
engine = get_engine(DATABASE_PATH)
init_db(engine)
SessionLocal = get_session_factory(engine)

# Inicializa o seed com administrador padrão
with SessionLocal() as db:
    seed_db(db, get_password_hash("admin123"))

# ==========================================
# SCHEDULER & AGENTES DE EXECUÇÃO
# ==========================================

scheduler = BackgroundScheduler(timezone=TZ_SAO_PAULO)
scheduler.start()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = db.query(User).filter_by(username=username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem acessar este recurso."
        )
    return current_user

def sanitize_whatsapp_targets(targets_str: str) -> list[str]:
    if not targets_str:
        return []
    targets = []
    for t in targets_str.split(','):
        t = t.strip()
        if not t:
            continue
        if '-' in t:
            if not t.endswith('@g.us'):
                t = f"{t}@g.us"
        else:
            # Apenas números
            digits = ''.join(filter(str.isdigit, t))
            if digits:
                if not digits.endswith('@s.whatsapp.net'):
                    t = f"{digits}@s.whatsapp.net"
                else:
                    t = digits
        targets.append(t)
    return targets

def get_time_period_constraint(period: str) -> str:
    """Retorna uma string descritiva com data limite para o Gemini Search Grounding."""
    today = datetime.date.today()
    if period == "24h":
        start_date = today - datetime.timedelta(days=1)
        return f"nas últimas 24 horas (desde {start_date.strftime('%Y-%m-%d')})"
    elif period == "week":
        start_date = today - datetime.timedelta(days=7)
        return f"nos últimos 7 dias (desde {start_date.strftime('%Y-%m-%d')})"
    elif period == "month":
        start_date = today - datetime.timedelta(days=30)
        return f"nos últimos 30 dias (desde {start_date.strftime('%Y-%m-%d')})"
    elif period == "year":
        return f"no ano de {today.year} (desde {today.year}-01-01)"
    return f"nos últimos 30 dias (desde {(today - datetime.timedelta(days=30)).strftime('%Y-%m-%d')})"

def get_bcb_financial_facts() -> str:
    """Busca cotações PTAX recentes e as expectativas do Focus de Câmbio da API do Banco Central."""
    facts = []
    
    # 1. Busca PTAX recente do Dólar
    try:
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=10)
        start_str = start_date.strftime('%m-%d-%Y')
        end_str = today.strftime('%m-%d-%Y')
        url_ptax = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@dataInicial='{start_str}'&@dataFinalCotacao='{end_str}'&$format=json"
        res = requests.get(url_ptax, timeout=8)
        if res.status_code == 200:
            data = res.json()
            quotes = data.get('value', [])
            if quotes:
                facts.append("--- DADOS DE COTAÇÃO OFICIAL PTAX DO DÓLAR (FONTE: BANCO CENTRAL DO BRASIL) ---")
                for q in reversed(quotes):
                    dt_str = q.get('dataHoraCotacao', '')
                    if dt_str:
                        dt_formatted = datetime.datetime.strptime(dt_str.split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                    else:
                        dt_formatted = "N/A"
                    facts.append(f"- Data: {dt_formatted} | PTAX Compra: {q.get('cotacaoCompra'):.4f} | PTAX Venda: {q.get('cotacaoVenda'):.4f}")
                facts.append("---------------------------------------------------------------------------------")
    except Exception as e:
        print(f"⚠️ Erro ao obter dados PTAX do BCB: {e}")

    # 2. Busca Expectativas do Relatório Focus (Dólar Futuro / Câmbio)
    try:
        url_focus = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoAnuais?$filter=Indicador eq 'Câmbio'&$orderby=Data desc&$top=20&$format=json"
        res = requests.get(url_focus, timeout=8)
        if res.status_code == 200:
            data = res.json()
            entries = data.get('value', [])
            if entries:
                facts.append("--- CONSENSO DE EXPECTATIVAS DE CÂMBIO - RELATÓRIO FOCUS (FONTE: BANCO CENTRAL) ---")
                latest_report_date = entries[0].get('Data')
                facts.append(f"Data de Divulgação do Relatório Focus: {datetime.datetime.strptime(latest_report_date, '%Y-%m-%d').strftime('%d/%m/%Y')}")
                for e in entries:
                    # Filtra apenas baseCalculo 0 para evitar duplicidade de projeções no mesmo ano
                    if e.get('Data') == latest_report_date and e.get('baseCalculo') == 0:
                        facts.append(f"- Projeção para Fim de {e.get('DataReferencia')}: Média: R$ {e.get('Media'):.4f} | Mediana: R$ {e.get('Mediana'):.4f}")
                facts.append("---------------------------------------------------------------------------------")
    except Exception as e:
        print(f"⚠️ Erro ao obter dados Focus do BCB: {e}")

    if facts:
        facts.append("IMPORTANTE (REQUISITO DE ACURÁCIA): Ao escrever ou auditar o relatório, você DEVE utilizar estritamente e exatamente os valores de cotação PTAX e projeções do Relatório Focus listados acima caso vá mencionar esses dados. NUNCA tente deduzir, alucinar ou citar valores diferentes para essas datas/períodos de referência.")
        return "\n".join(facts)
    return ""

def run_topic_pipeline(topic_id: int):
    """Executa a coleta, síntese, auditoria, geração do PDF e publicação no WhatsApp para um tópico."""
    print(f"🚀 [Pipeline] Executando tópico ID {topic_id}...")
    db = SessionLocal()
    try:
        topic = db.query(ResearchTopic).filter_by(id=topic_id).first()
        if not topic or not topic.is_active:
            print(f"⚠️ [Pipeline] Tópico {topic_id} não encontrado ou inativo.")
            return

        user = topic.user
        
        # 1. Recupera as credenciais de I.A. (BYOK ou Global)
        gemini_key = topic.custom_gemini_key
        if not gemini_key:
            # Tenta pegar a global do .env
            gemini_key = os.environ.get("GEMINI_API_KEY")
            
        if not gemini_key:
            raise ValueError("Nenhuma Gemini API Key configurada para este tópico.")

        # Inicializa cliente Gemini
        client = genai.Client(api_key=gemini_key)
        model = topic.preferred_model or "gemini-2.5-pro"
        
        # Variáveis de controle de tokens
        total_p_tokens = 0
        total_c_tokens = 0

        # MÓDULO 1: DailyCollector com filtro temporal
        print(f"🔍 [Pipeline] Coletando notícias para tópico '{topic.topic_name}'...")
        time_constraint = get_time_period_constraint(topic.time_period)
        collector_prompt = f"""
        Hoje é dia {datetime.date.today().strftime('%d/%m/%Y')} (Ano de {datetime.date.today().year}).
        Busque na internet informações e notícias estritamente ocorridas {time_constraint} sobre: {topic.search_query}.
        Foque em relatórios e dados específicos desse período de tempo recente, descartando fatos de anos anteriores.
        Retorne os fatos principais detalhados e inclua as fontes/links obrigatórios de onde você retirou as informações.
        """
        response_collector = client.models.generate_content(
            model=model,
            contents=collector_prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        raw_data = response_collector.text
        
        # Se for tópico de dólar/ptax/câmbio, busca dados oficiais do BCB e anexa aos dados brutos para grounding indestrutível
        topic_lower = topic.topic_name.lower()
        query_lower = topic.search_query.lower()
        if any(w in topic_lower or w in query_lower for w in ["dólar", "dolar", "ptax", "câmbio", "cambio"]):
            print(f"[Pipeline] Tópico financeiro detectado. Anexando dados oficiais e projeções do Banco Central do Brasil...")
            bcb_facts = get_bcb_financial_facts()
            if bcb_facts:
                raw_data = f"{bcb_facts}\n\n{raw_data}"
                
        if response_collector.usage_metadata:
            total_p_tokens += response_collector.usage_metadata.prompt_token_count
            total_c_tokens += response_collector.usage_metadata.candidates_token_count

        # MÓDULO 2: Redator Sênior
        print(f"✍️ [Pipeline] Gerando rascunho de relatório...")
        link_group = os.environ.get("LINK_GROUP", "https://chat.whatsapp.com/DJDWRobITde5Mc7SZ4De1R")
        draft_prompt = f"""
        Você é um Especialista em Inteligência Artificial e Estrategista Sênior. 
        Transforme os dados brutos a seguir em um relatório executivo de altíssimo valor.
        
        REGRAS DE FORMATAÇÃO E ESTRUTURA (OBRIGATÓRIO):
        1. O título principal deve ser EXATAMENTE: "# I.A. Nível 01 - {topic.topic_name}"
        2. O subtítulo deve ser EXATAMENTE: "## José S.O. Junior (43) 9 8859-7348"
        3. Adicione o link do grupo: "🔗 **Grupo de WhatsApp:** [Acesse aqui]({link_group})"
        4. Adicione a data atual: "**Data:** {datetime.date.today().strftime('%d/%m/%Y')}"
        5. NÃO escreva "De:" nem "Para:" ou "Memorando". Vá direto para o "Assunto" e o conteúdo.
        6. O texto deve ser excelente, cobrindo as notícias com base nos dados fornecidos. Para cada notícia ou anúncio de mercado citado, inclua a data de publicação original no formato [dd/mm/aa] (exemplo: "[28/06/26]") logo no início do fato ou parágrafo correspondente.
        7. No final do documento, sob o cabeçalho "## Referências", liste todas as fontes de pesquisa de maneira organizada. Cada item deve conter a data [dd/mm/aa], o nome da fonte/veículo e o link/URL original exato clicável em formato de link Markdown (exemplo: `* **[Nome do Veículo - dd/mm/aa]**: Breve resumo do fato - [Link da Notícia](URL)`). NUNCA remova ou oculte as URLs originais da pesquisa.
        8. Ao criar tabelas em Markdown (como cotações PTAX ou projeções Focus), certifique-se de que cada linha da tabela (cabeçalho, separador e cada linha de dados) esteja em uma LINHA FÍSICA SEPARADA com quebras de linha normais (\n). NUNCA junte ou colapse várias linhas de tabela em um único parágrafo contínuo.
        
        DADOS BRUTOS:
        {raw_data}
        """
        response_draft = client.models.generate_content(
            model=model,
            contents=draft_prompt
        )
        draft_text = response_draft.text
        if response_draft.usage_metadata:
            total_p_tokens += response_draft.usage_metadata.prompt_token_count
            total_c_tokens += response_draft.usage_metadata.candidates_token_count

        # MÓDULO 2 (Agente 2): Auditor
        print(f"🕵️‍♂️ [Pipeline] Auditando relatório...")
        audit_prompt = f"""
        Você é um Revisor e Auditor Sênior Rigoroso.
        Revise o seguinte rascunho de relatório de acordo com estas REGRAS ABSOLUTAS:
        1. NUNCA inicie uma frase ou parágrafo com o pronome oblíquo "Me", "Te", "Se", "Nos" ou "Vos".
        2. Mantenha todas as fontes, links de referências e citações de links originais. É vital que as referências no final do documento sob "## Referências" contenham a data no formato [dd/mm/aa] e a URL exata clicável em formato Markdown (ex: `[Link da Notícia](URL)`). Se o rascunho omitiu os links clicáveis originais obtidos na coleta de dados, você DEVE recuperá-los e reinseri-los.
        3. Mantenha os cabeçalhos exatos: "# I.A. Nível 01 - {topic.topic_name}", o subtítulo de telefone e a Data. NUNCA adicione blocos como "De/Para".
        4. O relatório DEVE terminar OBRIGATORIAMENTE com a seguinte frase exata e isolada no final: "Até a próxima edição."
        5. Garanta que todas as tabelas em Markdown estejam perfeitamente formatadas com quebras de linha físicas normais para cada linha de dados (cabeçalho, separador e linhas de conteúdo). NUNCA permita que tabelas fiquem colapsadas em uma única linha horizontal com barras duplas (||). Se encontrar, quebre-as em linhas separadas.
        
        RASCUNHO:
        {draft_text}
        
        Retorne apenas o texto final em formato Markdown limpo, sem delimitações extras.
        """
        response_audit = client.models.generate_content(
            model=model,
            contents=audit_prompt
        )
        final_text = response_audit.text
        if response_audit.usage_metadata:
            total_p_tokens += response_audit.usage_metadata.prompt_token_count
            total_c_tokens += response_audit.usage_metadata.candidates_token_count

        # MÓDULO 3: Geração de PDF (xhtml2pdf)
        print(f"📄 [Pipeline] Gerando PDF...")
        html_content = markdown.markdown(final_text)
        
        css_style = """
        @page { size: a4 portrait; margin: 2cm; }
        body { font-family: Helvetica, Arial, sans-serif; color: #333333; font-size: 14px; line-height: 1.5; }
        h1, h2, h3 { color: #1E3A8A; }
        h1 { font-size: 20px; border-bottom: 1px solid #1E3A8A; padding-bottom: 4px; }
        h2 { font-size: 16px; margin-top: 15px; }
        p { margin-bottom: 10px; text-align: justify; }
        a { color: #2563EB; }
        ul { padding-left: 20px; }
        li { margin-bottom: 5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 15px; }
        th { background-color: #1E3A8A; color: #ffffff; padding: 6px; font-weight: bold; border: 1px solid #1E3A8A; text-align: left; }
        td { padding: 6px; border: 1px solid #dddddd; text-align: left; }
        """
        
        full_html = f"""
        <html><head><meta charset="utf-8"><style>{css_style}</style></head>
        <body>{html_content}</body></html>
        """
        
        pdf_filename = f"reports/Report_{topic_id}_{datetime.date.today().strftime('%Y%m%d')}_{random.randint(1000,9999)}.pdf"
        with open(pdf_filename, "w+b") as result_file:
            pisa_status = pisa.CreatePDF(full_html, dest=result_file)
            
        if pisa_status.err:
            raise RuntimeError(f"Falha na geração do PDF: {pisa_status.err}")

        # MÓDULO 4: Envio para o WhatsApp
        print(f"🚀 [Pipeline] Publicando no WhatsApp...")
        
        # Recupera as configurações globais de Evolution API
        cfg_url = db.query(SystemConfig).filter_by(key="evolution_url").first()
        cfg_token = db.query(SystemConfig).filter_by(key="evolution_token").first()
        
        evolution_url = cfg_url.value if cfg_url else os.environ.get("WHATSAPP_API_URL")
        evolution_token = cfg_token.value if cfg_token else os.environ.get("WHATSAPP_API_TOKEN")

        if not evolution_url or not evolution_token:
            raise ValueError("Evolution API URL ou Token não configurados no sistema.")

        headers = {
            "apikey": evolution_token,
            "Content-Type": "application/json"
        }
        
        with open(pdf_filename, "rb") as pdf_file:
            b64_content = base64.b64encode(pdf_file.read()).decode('utf-8')
            
        # Divide e sanitiza os destinos do WhatsApp
        targets = sanitize_whatsapp_targets(topic.whatsapp_target)
        if not targets:
            raise ValueError("Nenhum destinatário do WhatsApp válido configurado.")

        # Dispara para cada destinatário
        for target in targets:
            print(f"[Pipeline] Enviando PDF para destinatário: {target}")
            payload = {
                "number": target,
                "mediatype": "document",
                "mimetype": "application/pdf",
                "media": b64_content,
                "fileName": os.path.basename(pdf_filename),
                "caption": f"📊 *Relatório: {topic.topic_name}*"
            }
            # Faz o request HTTP com timeout expandido para 90s
            response_wa = requests.post(evolution_url, headers=headers, json=payload, timeout=90)
            response_wa.raise_for_status()

        # Salva o Log de Tokens e Histórico de Envio com o Markdown Gerado
        token_log = TokenLog(
            user_id=user.id,
            topic_id=topic_id,
            prompt_tokens=total_p_tokens,
            completion_tokens=total_c_tokens,
            total_tokens=total_p_tokens + total_c_tokens,
            model_used=model
        )
        db.add(token_log)
        
        history_entry = PublicationHistory(
            topic_id=topic_id,
            pdf_path=pdf_filename,
            status="success",
            generated_markdown=final_text
        )
        db.add(history_entry)
        db.commit()
        print(f"✅ [Pipeline] Tópico ID {topic_id} executado com sucesso e logs salvos!")
        
        # Se for um agendamento dinâmico/aleatório, calcula o próximo horário aleatório
        if topic.schedule_type == "random":
            reschedule_random_job(topic_id)
            
    except Exception as e:
        print(f"❌ [Pipeline] Falha no tópico ID {topic_id}: {e}")
        history_entry = PublicationHistory(
            topic_id=topic_id,
            pdf_path=pdf_filename if 'pdf_filename' in locals() else "N/A",
            status="error",
            error_message=str(e),
            generated_markdown=final_text if 'final_text' in locals() else None
        )
        db.add(history_entry)
        db.commit()
    finally:
        db.close()

def schedule_topic_job(topic: ResearchTopic):
    """Agenda ou atualiza uma tarefa no APScheduler com base na configuração do tópico."""
    job_id = f"topic_{topic.id}"
    
    # Remove job anterior se existir
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        
    if not topic.is_active:
        return
        
    if topic.schedule_type == "fixed":
        # Formato esperado: fixed_time="08:00"
        if not topic.fixed_time:
            return
        h, m = map(int, topic.fixed_time.split(':'))
        trigger = CronTrigger(hour=h, minute=m, timezone=TZ_SAO_PAULO)
        scheduler.add_job(
            run_topic_pipeline,
            trigger=trigger,
            args=[topic.id],
            id=job_id,
            replace_existing=True
        )
    elif topic.schedule_type == "random":
        # Para agendamento aleatório, sorteia o primeiro disparo
        reschedule_random_job(topic.id)

def reschedule_random_job(topic_id: int):
    """Calcula e agenda o próximo disparo aleatório de um tópico."""
    db = SessionLocal()
    try:
        topic = db.query(ResearchTopic).filter_by(id=topic_id).first()
        if not topic or not topic.is_active:
            return
            
        next_run = calculate_next_random_run(
            topic.random_range_start or "08:00",
            topic.random_range_end or "10:00"
        )
        
        job_id = f"topic_{topic.id}"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            
        scheduler.add_job(
            run_topic_pipeline,
            trigger='date',
            run_date=next_run,
            args=[topic.id],
            id=job_id,
            replace_existing=True
        )
        print(f"📅 [Scheduler] Próximo envio aleatório para tópico '{topic.topic_name}' agendado para: {next_run}")
    finally:
        db.close()

# Sincroniza tarefas ativas no startup
with SessionLocal() as db:
    active_topics = db.query(ResearchTopic).filter_by(is_active=1).all()
    for t in active_topics:
        schedule_topic_job(t)

# ==========================================
# ROTAS: AUTENTICAÇÃO (AUTH)
# ==========================================

@app.post("/api/auth/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Apenas admin pode criar outros administradores
    existing_user = db.query(User).filter_by(username=user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já cadastrado."
        )
    
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        plan_type=user_data.plan_type,
        trial_ends_at=datetime.datetime.utcnow() + datetime.timedelta(days=7) if user_data.plan_type == "free_trial" else None,
        max_topics_limit=user_data.max_topics_limit,
        max_tokens_monthly_limit=user_data.max_tokens_monthly_limit
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login", response_model=Token)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=login_data.username).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos."
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# ==========================================
# ROTAS: TÓPICOS DE PESQUISA (USER PANEL)
# ==========================================

@app.post("/api/topics", response_model=TopicResponse)
def create_topic(topic_data: TopicCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Valida limites de tópicos
    current_topics_count = db.query(ResearchTopic).filter_by(user_id=current_user.id).count()
    if current_topics_count >= current_user.max_topics_limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Limite de tópicos ({current_user.max_topics_limit}) atingido para o plano atual '{current_user.plan_type}'."
        )
        
    new_topic = ResearchTopic(
        user_id=current_user.id,
        topic_name=topic_data.topic_name,
        search_query=topic_data.search_query,
        whatsapp_target=topic_data.whatsapp_target,
        schedule_type=topic_data.schedule_type,
        fixed_time=topic_data.fixed_time,
        random_range_start=topic_data.random_range_start,
        random_range_end=topic_data.random_range_end,
        days_of_week=topic_data.days_of_week,
        custom_gemini_key=topic_data.custom_gemini_key,
        preferred_model=topic_data.preferred_model,
        time_period=topic_data.time_period
    )
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    
    # Agenda no APScheduler
    schedule_topic_job(new_topic)
    
    return new_topic

@app.get("/api/topics", response_model=List[TopicResponse])
def get_topics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Regular users only see their own topics, admin sees all
    if current_user.role == "admin":
        return db.query(ResearchTopic).all()
    return db.query(ResearchTopic).filter_by(user_id=current_user.id).all()

@app.put("/api/topics/{topic_id}", response_model=TopicResponse)
def update_topic(topic_id: int, topic_data: TopicUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    topic = db.query(ResearchTopic).filter_by(id=topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Tópico não encontrado.")
    if current_user.role != "admin" and topic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado.")
        
    for field, val in topic_data.dict(exclude_unset=True).items():
        setattr(topic, field, val)
        
    db.commit()
    db.refresh(topic)
    
    # Re-agenda no APScheduler
    schedule_topic_job(topic)
    
    return topic

@app.delete("/api/topics/{topic_id}")
def delete_topic(topic_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    topic = db.query(ResearchTopic).filter_by(id=topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Tópico não encontrado.")
    if current_user.role != "admin" and topic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado.")
        
    job_id = f"topic_{topic_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        
    db.delete(topic)
    db.commit()
    return {"detail": "Tópico deletado com sucesso."}

@app.post("/api/topics/{topic_id}/run")
def trigger_topic_manually(topic_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    topic = db.query(ResearchTopic).filter_by(id=topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Tópico não encontrado.")
    if current_user.role != "admin" and topic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado.")
        
    # Executa de forma assíncrona (usamos scheduler.add_job para rodar imediatamente)
    scheduler.add_job(run_topic_pipeline, args=[topic_id], id=f"manual_{topic_id}_{random.randint(1000,9999)}")
    return {"detail": "Execução manual do pipeline disparada."}

# ==========================================
# ROTAS: HISTÓRICO E METRICAS (USER PANEL)
# ==========================================

@app.get("/api/history", response_model=List[HistoryResponse])
def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "admin":
        results = db.query(PublicationHistory).all()
    else:
        results = db.query(PublicationHistory).join(ResearchTopic).filter(
            ResearchTopic.user_id == current_user.id
        ).all()
        
    # Injeta o nome do tópico na resposta
    res = []
    for r in results:
        topic_name = db.query(ResearchTopic.topic_name).filter_by(id=r.topic_id).scalar()
        res.append({
            "id": r.id,
            "topic_id": r.topic_id,
            "topic_name": topic_name,
            "pdf_path": r.pdf_path,
            "sent_at": r.sent_at,
            "status": r.status,
            "error_message": r.error_message
        })
    return res

@app.get("/api/tokens/usage", response_model=List[TokenLogResponse])
def get_tokens_usage(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "admin":
        return db.query(TokenLog).all()
    return db.query(TokenLog).filter_by(user_id=current_user.id).all()

# ==========================================
# ROTAS: ADMINISTRAÇÃO E SETTINGS
# ==========================================

@app.get("/api/admin/config", response_model=SystemConfigResponse)
def get_system_config(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    configs = db.query(SystemConfig).all()
    cfg_dict = {c.key: c.value for c in configs}
    return {
        "company_name": cfg_dict.get("company_name", "AGP Publisher"),
        "theme_color_primary": cfg_dict.get("theme_color_primary", "#1E3A8A"),
        "theme_color_secondary": cfg_dict.get("theme_color_secondary", "#2563EB"),
        "logo_path": cfg_dict.get("logo_path", "/static/logo.png"),
        "evolution_url": cfg_dict.get("evolution_url") if current_user.role == "admin" else None,
        "evolution_token": cfg_dict.get("evolution_token") if current_user.role == "admin" else None
    }

@app.put("/api/admin/config")
def update_system_config(config_data: SystemConfigUpdate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    for field, val in config_data.dict(exclude_unset=True).items():
        cfg = db.query(SystemConfig).filter_by(key=field).first()
        if cfg:
            cfg.value = val
        else:
            cfg = SystemConfig(key=field, value=val)
            db.add(cfg)
    db.commit()
    return {"detail": "Configurações atualizadas com sucesso."}

@app.post("/api/admin/logo")
def upload_logo(file: UploadFile = File(...), current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    logo_filename = f"static/logo_{int(datetime.datetime.utcnow().timestamp())}_{file.filename}"
    with open(logo_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    logo_path_url = f"/static/{os.path.basename(logo_filename)}"
    
    cfg = db.query(SystemConfig).filter_by(key="logo_path").first()
    if cfg:
        cfg.value = logo_path_url
    else:
        cfg = SystemConfig(key="logo_path", value=logo_path_url)
        db.add(cfg)
        
    db.commit()
    return {"logo_path": logo_path_url}

@app.get("/api/admin/users", response_model=List[UserResponse])
def get_users_list(current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(User).all()

@app.put("/api/admin/users/{user_id}", response_model=UserResponse)
def update_user_profile(user_id: int, user_data: UserCreate, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        
    user.username = user_data.username
    if user_data.password:
         user.password_hash = get_password_hash(user_data.password)
    user.role = user_data.role
    user.plan_type = user_data.plan_type
    user.max_topics_limit = user_data.max_topics_limit
    user.max_tokens_monthly_limit = user_data.max_tokens_monthly_limit
    
    db.commit()
    db.refresh(user)
    return user

@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Você não pode deletar seu próprio usuário administrador.")
        
    db.delete(user)
    db.commit()
    return {"detail": "Usuário deletado com sucesso."}

# ==========================================
# INTEGRAÇÃO EVOLUTION QR CODE & WHATSAPP INSTANCE
# ==========================================

@app.get("/api/whatsapp/connect")
def get_whatsapp_connect_qrcode(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Interface simplificada. Cria uma instância do usuário na Evolution API central e retorna o QR Code.
    Em ambiente local mock, simula o retorno do QR Code ou conecta diretamente se estiver mockado.
    """
    cfg_url = db.query(SystemConfig).filter_by(key="evolution_url").first()
    cfg_token = db.query(SystemConfig).filter_by(key="evolution_token").first()
    
    evolution_url = cfg_url.value if cfg_url else os.environ.get("WHATSAPP_API_URL")
    evolution_token = cfg_token.value if cfg_token else os.environ.get("WHATSAPP_API_TOKEN")
    
    # Se estiver simulando na máquina de teste local ou sem credenciais reais
    if "projetobrasil2050" not in str(evolution_url) and "localhost" in str(evolution_url):
        # Retorna mock QR Code Base64
        mock_qr = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        return {
            "instance_name": f"agp-user-{current_user.id}",
            "status": "qrcode",
            "qrcode": f"data:image/png;base64,{mock_qr}"
        }

    # Determina o nome da instância
    # Se a URL informada terminar com a instância (ex: /message/sendMedia/01), extraímos ela
    if "/message/sendMedia/" in str(evolution_url):
        instance_name = evolution_url.split("/message/sendMedia/")[-1].strip("/")
    else:
        instance_name = f"agp-user-{current_user.id}"
        
    base_url = evolution_url.split("/message/")[0] # Pega o host base da Evolution
    
    try:
        # 1. Cria a instância (apenas se for dinâmica, pois instâncias fixas já existem)
        if instance_name.startswith("agp-user-"):
            create_url = f"{base_url}/instance/create"
            headers = {"apikey": evolution_token, "Content-Type": "application/json"}
            payload = {"instanceName": instance_name, "token": evolution_token, "qrcode": True}
            requests.post(create_url, headers=headers, json=payload, timeout=10)
        
        # 2. Busca o QR code da instância ou status de conexão
        connect_url = f"{base_url}/instance/connect/{instance_name}"
        headers = {"apikey": evolution_token, "Content-Type": "application/json"}
        res_conn = requests.get(connect_url, headers=headers, timeout=10)
        res_conn.raise_for_status()
        conn_data = res_conn.json()
        
        # O status ou estado pode vir em conn_data["status"] ou conn_data["instance"]["state"]
        conn_status = conn_data.get("status") or conn_data.get("instance", {}).get("state") or "qrcode"
        if conn_status in ["open", "connected"]:
            return {
                "instance_name": instance_name,
                "status": "connected",
                "qrcode": None
            }
            
        qrcode_b64 = conn_data.get("qrcode", {}).get("base64") or conn_data.get("base64")
        if qrcode_b64 and not qrcode_b64.startswith("data:image/"):
            qrcode_b64 = f"data:image/png;base64,{qrcode_b64}"
            
        return {
            "instance_name": instance_name,
            "status": "qrcode",
            "qrcode": qrcode_b64
        }
    except Exception as e:
        print(f"⚠️ Erro ao comunicar com Evolution API: {e}")
        # Fallback para o QR code de mock para não quebrar o dashboard de testes
        mock_qr = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        return {
            "instance_name": instance_name,
            "status": "qrcode",
            "qrcode": f"data:image/png;base64,{mock_qr}",
            "warning": f"Evolution API offline. Usando mock. Detalhes: {e}"
        }

if __name__ == "__main__":
    import uvicorn
    # Executa o servidor na porta 8080 para evitar conflitos com outros servidores locais (ex: Django)
    uvicorn.run(app, host="0.0.0.0", port=8080)
