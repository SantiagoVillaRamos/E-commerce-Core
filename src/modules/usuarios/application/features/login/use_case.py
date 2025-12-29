"""
Caso de uso para el inicio de sesión de usuarios.
"""
from dataclasses import dataclass
from pydantic import BaseModel

from src.modules.usuarios.domain.repositories import UserRepository
from src.modules.usuarios.application.services.auth_service import AuthService
from src.core.exceptions import BusinessRuleViolation


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


class LoginUseCase:
    """
    Autentica un usuario y genera un token JWT.
    """
    
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def execute(self, username: str, password: str) -> LoginResponse:
        # 1. Buscar usuario
        user = await self.repository.get_by_username(username)
        if not user:
            raise BusinessRuleViolation("Credenciales inválidas")
            
        # 2. Verificar contraseña
        if not AuthService.verify_password(password, user.hashed_password):
            raise BusinessRuleViolation("Credenciales inválidas")
            
        # 3. Verificar si está activo
        if not user.is_active:
            raise BusinessRuleViolation("Usuario desactivado")
            
        # 4. Crear Token
        access_token = AuthService.create_access_token(
            data={"sub": str(user.user_id), "username": user.username}
        )
        
        return LoginResponse(
            access_token=access_token,
            username=user.username
        )
