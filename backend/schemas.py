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
    custom_gemini_key: Optional[str] = None
    preferred_model: Optional[str] = "gemini-2.5-pro"

class TopicUpdate(BaseModel):
    topic_name: Optional[str] = None
    search_query: Optional[str] = None
    whatsapp_target: Optional[str] = None
    schedule_type: Optional[str] = None
    fixed_time: Optional[str] = None
    random_range_start: Optional[str] = None
    random_range_end: Optional[str] = None
    days_of_week: Optional[str] = None
    custom_gemini_key: Optional[str] = None
    preferred_model: Optional[str] = None
    is_active: Optional[int] = None

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
    custom_gemini_key: Optional[str] = None
    preferred_model: str
    is_active: int
    created_at: datetime

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

class SystemConfigResponse(BaseModel):
    company_name: str
    theme_color_primary: str
    theme_color_secondary: str
    logo_path: str
    evolution_url: Optional[str] = None
    evolution_token: Optional[str] = None

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

    class Config:
        from_attributes = True
