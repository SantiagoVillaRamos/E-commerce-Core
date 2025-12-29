"""
Dependencias de FastAPI para el módulo de Usuarios.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.core.database import get_db_session
from src.core.config import settings
from src.modules.usuarios.infrastructure.repositories import SQLAlchemyUserRepository
from src.modules.usuarios.application.features.register_user.use_case import RegisterUserUseCase
from src.modules.usuarios.application.features.login.use_case import LoginUseCase
from src.modules.usuarios.application.services.auth_service import AuthService
from src.modules.usuarios.domain.entities import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/usuarios/login")

def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)

def get_register_use_case(repo: SQLAlchemyUserRepository = Depends(get_user_repository)) -> RegisterUserUseCase:
    return RegisterUserUseCase(repo)

def get_login_use_case(repo: SQLAlchemyUserRepository = Depends(get_user_repository)) -> LoginUseCase:
    return LoginUseCase(repo)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    repo: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = AuthService.decode_token(token)
    if payload is None:
        raise credentials_exception
        
    username: str = payload.get("username")
    if username is None:
        raise credentials_exception
        
    user = await repo.get_by_username(username)
    if user is None:
        raise credentials_exception
        
    return user
