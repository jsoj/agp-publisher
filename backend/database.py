import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

# ==========================================
# MODELOS DE DADOS DO BANCO (SQLAlchemy)
# ==========================================

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default='user') # 'admin' ou 'user'
    theme_preference = Column(String, default='light')
    
    # SaaS & Planos
    plan_type = Column(String, default='free_trial') # 'free_trial', 'pro', 'enterprise'
    trial_ends_at = Column(DateTime, nullable=True)
    subscription_active = Column(Integer, default=1)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    
    # Limites
    max_topics_limit = Column(Integer, default=1)
    max_tokens_monthly_limit = Column(Integer, default=100000)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    topics = relationship("ResearchTopic", back_populates="user", cascade="all, delete-orphan")
    token_logs = relationship("TokenLog", back_populates="user", cascade="all, delete-orphan")

class SystemConfig(Base):
    __tablename__ = 'system_config'
    
    key = Column(String, primary_key=True)
    value = Column(String, nullable=True)

class ResearchTopic(Base):
    __tablename__ = 'research_topics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    topic_name = Column(String, nullable=False)
    search_query = Column(String, nullable=False)
    whatsapp_target = Column(String, nullable=False)
    
    # Agendamento
    schedule_type = Column(String, default='fixed') # 'fixed' ou 'random'
    fixed_time = Column(String, nullable=True) # "HH:MM"
    random_range_start = Column(String, nullable=True) # "HH:MM"
    random_range_end = Column(String, nullable=True) # "HH:MM"
    days_of_week = Column(String, nullable=True) # "1,2,3,4,5"
    
    # BYOK
    custom_gemini_key = Column(String, nullable=True)
    preferred_model = Column(String, default='gemini-2.5-pro')
    
    is_active = Column(Integer, default=1)
    time_period = Column(String, default='month') # '24h', 'week', 'month', 'year'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="topics")
    token_logs = relationship("TokenLog", back_populates="topic")
    history = relationship("PublicationHistory", back_populates="topic", cascade="all, delete-orphan")

class TokenLog(Base):
    __tablename__ = 'token_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    topic_id = Column(Integer, ForeignKey('research_topics.id'), nullable=True)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    model_used = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="token_logs")
    topic = relationship("ResearchTopic", back_populates="token_logs")

class PublicationHistory(Base):
    __tablename__ = 'publication_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('research_topics.id'), nullable=False)
    pdf_path = Column(String, nullable=False)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, nullable=False) # 'success' ou 'error'
    error_message = Column(String, nullable=True)
    generated_markdown = Column(String, nullable=True)
    
    topic = relationship("ResearchTopic", back_populates="history")

# ==========================================
# INICIALIZAÇÃO E CONEXÃO
# ==========================================

def get_engine(db_path=None):
    if not db_path:
        db_path = os.environ.get("DATABASE_PATH", "agp_database.db")
    
    # Se for SQLite em memória (para testes) ou arquivo local
    if db_path == ":memory:":
        engine_url = "sqlite:///:memory:"
    else:
        # Se for Windows, o path precisa de formatação correta
        # O SQLAlchemy usa sqlite:///path_completo
        engine_url = f"sqlite:///{db_path}"
        
    return create_engine(engine_url, connect_args={"check_same_thread": False} if "sqlite" in engine_url else {})

def init_db(engine):
    Base.metadata.create_all(bind=engine)
    
    # Executa a migração automática para adicionar a nova coluna se já existir a tabela
    from sqlalchemy import text
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE publication_history ADD COLUMN generated_markdown TEXT"))
        except Exception:
            pass
            
        try:
            conn.execute(text("ALTER TABLE research_topics ADD COLUMN time_period TEXT DEFAULT 'month'"))
        except Exception:
            pass

def get_session_factory(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_db(session, default_admin_password_hash):
    """Popula as tabelas com valores iniciais se estiverem vazias."""
    # Seed de Configurações do Sistema
    defaults = {
        "evolution_url": os.environ.get("WHATSAPP_API_URL", "https://evolution.projetobrasil2050.site/message/sendMedia/01"),
        "evolution_token": os.environ.get("WHATSAPP_API_TOKEN", "6CBB7DCE6D50-4851-A607-F2EC2C1580C2"),
        "company_name": "AGP Publisher",
        "theme_color_primary": "#1E3A8A",
        "theme_color_secondary": "#2563EB",
        "logo_path": "/static/logo.png"
    }
    
    for k, v in defaults.items():
        existing = session.query(SystemConfig).filter_by(key=k).first()
        if not existing:
            cfg = SystemConfig(key=k, value=v)
            session.add(cfg)
            
    # Seed de Usuário Administrador Padrão
    admin_user = session.query(User).filter_by(role="admin").first()
    if not admin_user:
        new_admin = User(
            username="admin",
            password_hash=default_admin_password_hash,
            role="admin",
            plan_type="enterprise",
            max_topics_limit=9999,
            max_tokens_monthly_limit=99999999
        )
        session.add(new_admin)
        
    session.commit()

