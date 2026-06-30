import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from bcrypt import hashpw, gensalt, checkpw

# Configurações do JWT
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "agp_secret_key_super_secure_123456")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 horas

def get_password_hash(password: str) -> str:
    """Gera um hash Bcrypt a partir de uma senha de texto plano."""
    pwd_bytes = password.encode('utf-8')
    salt = gensalt()
    hashed = hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se uma senha de texto plano bate com o hash Bcrypt salvo."""
    try:
        return checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT com expiração."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica e valida um token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
