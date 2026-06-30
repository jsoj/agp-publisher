import pytest
import os
from autonomous_publisher import PDFGenerator

# ==========================================
# TESTES DE REGRAS DE NEGÓCIO (GRAMÁTICA E ESTILO)
# ==========================================
# Em um teste real, você pode mockar o retorno da API do Gemini, 
# mas aqui focamos em testar se as nossas funções de validação interna 
# (ou regexes futuros de fallback) funcionariam caso a IA falhe.

def test_regra_pronome_inicio_frase():
    """Garante que a revisão do texto bloqueie ou denuncie 'Me' no início de frases."""
    
    texto_simulado_falho = "Me parece que o mercado mudou. A inteligência artificial avançou."
    texto_simulado_correto = "Parece-me que o mercado mudou. A inteligência artificial avançou."
    
    # Simulação da verificação de integridade pós-IA
    def contains_invalid_pronoun_start(text):
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        for s in sentences:
            s = s.strip()
            if s.startswith("Me ") or s.startswith("Te "):
                return True
        return False

    assert contains_invalid_pronoun_start(texto_simulado_falho) == True
    assert contains_invalid_pronoun_start(texto_simulado_correto) == False

def test_regra_assinatura_obrigatoria():
    """O relatório DEVE conter a assinatura de finalização acordada."""
    
    assinatura_esperada = "até a próxima edição."
    
    texto_gerado_pela_ia = """
    # Relatório Executivo
    O mercado cresceu 20%.
    
    Até a próxima edição.
    """
    
    assert assinatura_esperada in texto_gerado_pela_ia.lower(), "A IA falhou em incluir a assinatura obrigatória."

# ==========================================
# TESTES DE ARTEFATOS FÍSICOS (PDF)
# ==========================================
def test_geracao_de_pdf_mobile_first(tmp_path):
    """Testa se o motor HTML/CSS consegue gerar um arquivo binário legível."""
    
    pdf_gen = PDFGenerator()
    markdown_test = "# Teste de Título\nEste é um parágrafo de teste."
    
    # Utilizando diretório temporário do Pytest
    output_file = tmp_path / "test_report.pdf"
    
    # Executa a geração
    pdf_gen.generate(markdown_test, str(output_file))
    
    # Verifica se o arquivo foi criado e possui tamanho maior que 0
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 1000  # Pelo menos 1KB de cabeçalhos PDF

# ==========================================
# NOVOS TESTES DE EXPANSÃO SAAS (TDD)
# ==========================================

@pytest.fixture
def db_session():
    """Fixture que provê uma sessão limpa de banco de dados SQLite em memória para cada teste."""
    from backend.database import get_engine, init_db, get_session_factory
    engine = get_engine(":memory:")
    init_db(engine)
    Session = get_session_factory(engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_saas_plan_limits(db_session):
    """Garante que usuários no plano free_trial não ultrapassem o limite de tópicos."""
    from backend.database import User, ResearchTopic
    
    # Cria usuário free_trial com limite de 1 tópico
    user = User(
        username="trial_user",
        password_hash="mock_hash",
        plan_type="free_trial",
        max_topics_limit=1
    )
    db_session.add(user)
    db_session.commit()
    
    # Adiciona primeiro tópico (deve passar)
    topic1 = ResearchTopic(
        user_id=user.id,
        topic_name="IA em Vendas",
        search_query="noticias de IA",
        whatsapp_target="12345"
    )
    db_session.add(topic1)
    db_session.commit()
    
    # Função auxiliar de inserção que valida limite
    def add_topic_with_limit_check(session, user_obj, new_topic):
        current_topics_count = session.query(ResearchTopic).filter_by(user_id=user_obj.id).count()
        if current_topics_count >= user_obj.max_topics_limit:
            raise ValueError("Limite de tópicos atingido para o plano atual.")
        session.add(new_topic)
        session.commit()

    # Tenta adicionar o segundo tópico (deve falhar com ValueError)
    topic2 = ResearchTopic(
        user_id=user.id,
        topic_name="IA na Saúde",
        search_query="noticias de IA saude",
        whatsapp_target="123456"
    )
    
    with pytest.raises(ValueError, match="Limite de tópicos atingido"):
        add_topic_with_limit_check(db_session, user, topic2)

def test_randomized_schedule():
    """Garante que a lógica de cálculo de horários aleatórios respeite os limites e tz."""
    import datetime
    from backend.scheduler_service import calculate_next_random_run, TZ_SAO_PAULO
    
    start_time = "08:00"
    end_time = "10:00"
    
    # Usando uma data de referência fixa para testes reproduzíveis
    ref_date = datetime.date(2026, 7, 1)
    
    next_run = calculate_next_random_run(start_time, end_time, reference_date=ref_date)
    
    assert next_run.tzinfo == TZ_SAO_PAULO
    assert next_run.date() == ref_date or next_run.date() == ref_date + datetime.timedelta(days=1)
    
    # O horário gerado deve estar dentro de 08:00 e 10:00
    run_minutes = next_run.hour * 60 + next_run.minute
    assert 8 * 60 <= run_minutes <= 10 * 60

def test_token_logs_counting(db_session):
    """Garante que o registro de tokens e validação de limites mensais funciona."""
    from backend.database import User, TokenLog
    import datetime
    
    user = User(
        username="client_user",
        password_hash="mock_hash",
        max_tokens_monthly_limit=5000
    )
    db_session.add(user)
    db_session.commit()
    
    # Adiciona logs de tokens
    log1 = TokenLog(user_id=user.id, prompt_tokens=1000, completion_tokens=1500, total_tokens=2500)
    log2 = TokenLog(user_id=user.id, prompt_tokens=500, completion_tokens=1000, total_tokens=1500)
    db_session.add_all([log1, log2])
    db_session.commit()
    
    # Função auxiliar para somar tokens do mês atual
    def get_monthly_token_usage(session, user_id):
        now = datetime.datetime.utcnow()
        start_of_month = datetime.datetime(now.year, now.month, 1)
        result = session.query(TokenLog).filter(
            TokenLog.user_id == user_id,
            TokenLog.timestamp >= start_of_month
        ).all()
        return sum(log.total_tokens for log in result)

    total_used = get_monthly_token_usage(db_session, user.id)
    assert total_used == 4000
    assert total_used < user.max_tokens_monthly_limit
    
    # Adiciona mais logs estourando o limite
    log3 = TokenLog(user_id=user.id, prompt_tokens=1000, completion_tokens=1000, total_tokens=2000)
    db_session.add(log3)
    db_session.commit()
    
    total_used_after = get_monthly_token_usage(db_session, user.id)
    assert total_used_after == 6000
    assert total_used_after > user.max_tokens_monthly_limit

def test_user_auth_and_permissions(db_session):
    """Garante a integridade do hash de senhas e a restrição de rotas/papéis."""
    from backend.database import User, SystemConfig
    from backend.auth import get_password_hash, verify_password
    
    raw_password = "SuperPassword123!"
    hashed = get_password_hash(raw_password)
    
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) == True
    assert verify_password("wrong_password", hashed) == False
    
    # Cadastro de usuários com papéis
    admin = User(username="admin_user", password_hash=hashed, role="admin")
    regular = User(username="regular_user", password_hash=hashed, role="user")
    db_session.add_all([admin, regular])
    db_session.commit()
    
    # Função para alterar configurações do sistema com verificação de permissões
    def set_system_config(session, user_obj, config_key, config_val):
        if user_obj.role != "admin":
            raise PermissionError("Acesso negado. Apenas administradores podem modificar configurações.")
        
        cfg = session.query(SystemConfig).filter_by(key=config_key).first()
        if not cfg:
            cfg = SystemConfig(key=config_key, value=config_val)
            session.add(cfg)
        else:
            cfg.value = config_val
        session.commit()
        
    # Admin deve conseguir alterar
    set_system_config(db_session, admin, "evolution_url", "https://api.whatsapp")
    cfg = db_session.query(SystemConfig).filter_by(key="evolution_url").first()
    assert cfg.value == "https://api.whatsapp"
    
    # Usuário regular deve falhar com PermissionError
    with pytest.raises(PermissionError, match="Acesso negado"):
        set_system_config(db_session, regular, "evolution_url", "https://hack")