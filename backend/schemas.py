from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ==========================================
# AUTH SCHEMAS
# ==========================================

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"
    plan_type: Optional[str] = "free_trial"
    max_topics_limit: Optional[int] = 1
    max_tokens_monthly_limit: Optional[int] = 100000

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    theme_preference: str
    plan_type: str
    trial_ends_at: Optional[datetime] = None
    subscription_active: int
    max_topics_limit: int
    max_tokens_monthly_limit: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# ==========================================
# AI MODEL CONFIG SCHEMAS
# ==========================================

class AIModelConfigCreate(BaseModel):
    provider: str # 'gemini', 'openai', 'anthropic', 'deepseek', etc.
    model_name: str
    api_key: str
    base_url: Optional[str] = None

class AIModelConfigUpdate(BaseModel):
    provider: Optional[str] = None
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    is_active: Optional[bool] = None

class AIModelConfigResponse(BaseModel):
    id: int
    provider: str
    model_name: str
    base_url: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

# ==========================================
# EMAIL GROUP & CONTACT SCHEMAS
# ==========================================

class EmailContactCreate(BaseModel):
    name: str
    email: str

class EmailContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class EmailContactResponse(BaseModel):
    id: int
    group_id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class EmailGroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    contacts: Optional[List[EmailContactCreate]] = []

class EmailGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class EmailGroupResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    contacts: List[EmailContactResponse] = []

    class Config:
        from_attributes = True

# ==========================================
# TOPIC SUBSCRIPTION SCHEMAS
# ==========================================

class TopicSubscriptionCreate(BaseModel):
    topic_id: int
    delivery_type: str # 'whatsapp' ou 'email'
    target: str

class TopicSubscriptionResponse(BaseModel):
    id: int
    topic_id: int
    delivery_type: str
    target: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# TOPIC SCHEMAS
# ==========================================

class TopicCreate(BaseModel):
    topic_name: str
    search_query: str
    whatsapp_target: str
    schedule_type: str = "fixed" # 'fixed' ou 'random'
    fixed_time: Optional[str] = None # "HH:MM"
    random_range_start: Optional[str] = None # "HH:MM"
    random_range_end: Optional[str] = None # "HH:MM"
    days_of_week: Optional[str] = None # "1,2,3,4,5"
    schedule_interval: Optional[str] = "daily" # 'daily', 'weekly', 'biweekly', 'monthly'
    schedule_days: Optional[str] = None # "1,3,5" para Seg, Qua, Sex
    date_range_start: Optional[str] = None # YYYY-MM-DD
    date_range_end: Optional[str] = None # YYYY-MM-DD
    collector_model_id: Optional[int] = None
    writer_model_id: Optional[int] = None
    auditor_model_id: Optional[int] = None
    custom_gemini_key: Optional[str] = None
    preferred_model: Optional[str] = "gemini-2.5-pro"
    time_period: Optional[str] = "month"
    is_public: Optional[int] = 0
    email_group_ids: Optional[List[int]] = []

class TopicUpdate(BaseModel):
    topic_name: Optional[str] = None
    search_query: Optional[str] = None
    whatsapp_target: Optional[str] = None
    schedule_type: Optional[str] = None
    fixed_time: Optional[str] = None
    random_range_start: Optional[str] = None
    random_range_end: Optional[str] = None
    days_of_week: Optional[str] = None
    schedule_interval: Optional[str] = None
    schedule_days: Optional[str] = None
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    collector_model_id: Optional[int] = None
    writer_model_id: Optional[int] = None
    auditor_model_id: Optional[int] = None
    custom_gemini_key: Optional[str] = None
    preferred_model: Optional[str] = None
    is_active: Optional[int] = None
    is_public: Optional[int] = None
    time_period: Optional[str] = None
    email_group_ids: Optional[List[int]] = []

class TopicResponse(BaseModel):
    id: int
    user_id: int
    topic_name: str
    search_query: str
    whatsapp_target: str
    schedule_type: str
    fixed_time: Optional[str] = None
    random_range_start: Optional[str] = None
    random_range_end: Optional[str] = None
    days_of_week: Optional[str] = None
    schedule_interval: str
    schedule_days: Optional[str] = None
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    collector_model_id: Optional[int] = None
    writer_model_id: Optional[int] = None
    auditor_model_id: Optional[int] = None
    custom_gemini_key: Optional[str] = None
    preferred_model: str
    is_active: int
    is_public: int
    time_period: str
    created_at: datetime
    email_groups: List[EmailGroupResponse] = []

    class Config:
        from_attributes = True

# ==========================================
# CONFIG & UTILS SCHEMAS
# ==========================================

class SystemConfigUpdate(BaseModel):
    evolution_url: Optional[str] = None
    evolution_token: Optional[str] = None
    company_name: Optional[str] = None
    theme_color_primary: Optional[str] = None
    theme_color_secondary: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[str] = None
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    smtp_sender: Optional[str] = None

class SystemConfigResponse(BaseModel):
    company_name: str
    theme_color_primary: str
    theme_color_secondary: str
    logo_path: str
    evolution_url: Optional[str] = None
    evolution_token: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[str] = None
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    smtp_sender: Optional[str] = None

# ==========================================
# TOKEN & HISTORY SCHEMAS
# ==========================================

class TokenLogResponse(BaseModel):
    id: int
    user_id: int
    topic_id: Optional[int] = None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model_used: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class HistoryResponse(BaseModel):
    id: int
    topic_id: int
    topic_name: Optional[str] = None
    pdf_path: str
    sent_at: datetime
    status: str
    error_message: Optional[str] = None
    generated_markdown: Optional[str] = None

    class Config:
        from_attributes = True
