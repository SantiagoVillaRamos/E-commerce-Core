"""
Servicio de aplicación para autenticación y seguridad.
"""
from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
from passlib.context import CryptContext

from src.core.config import settings


class AuthService:
    """
    Servicio encargado de la seguridad:
    1. Hashing y verificación de contraseñas.
    2. Generación y validación de tokens JWT.
    """
    
    # Contexto de hashing
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verifica si una contraseña en texto plano coincide con su hash."""
        return cls.pwd_context.verify(plain_password, hashed_password)
    
    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """Genera un hash bcrypt a partir de una contraseña."""
        return cls.pwd_context.hash(password)
    
    @classmethod
    def create_access_token(
        cls, 
        data: dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crea un token JWT de acceso.
        
        Args:
            data: Información a incluir en el payload (ej: sub: user_id)
            expires_delta: Tiempo de expiración personalizado
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
            
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.secret_key, 
            algorithm=settings.algorithm
        )
        
        return encoded_jwt

    @classmethod
    def decode_token(cls, token: str) -> Optional[dict]:
        """
        Decodifica y valida un token JWT.
        """
        try:
            payload = jwt.decode(
                token, 
                settings.secret_key, 
                algorithms=[settings.algorithm]
            )
            return payload
        except jwt.JWTError:
            return None
