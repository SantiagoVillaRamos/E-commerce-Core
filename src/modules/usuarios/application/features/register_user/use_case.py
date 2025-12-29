"""
Caso de uso para registrar nuevos usuarios.
"""
from dataclasses import dataclass
from uuid import UUID

from src.modules.usuarios.domain.entities import User
from src.modules.usuarios.domain.repositories import UserRepository
from src.modules.usuarios.application.services.auth_service import AuthService
from src.core.exceptions import BusinessRuleViolation


@dataclass
class RegisterUserCommand:
    username: str
    email: str
    password: str
    full_name: str = None


class RegisterUserUseCase:
    """
    Registra un nuevo usuario en el sistema.
    Valida SKU/Email únicos y hashea la contraseña.
    """
    
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def execute(self, command: RegisterUserCommand) -> User:
        # 1. Validar si ya existe el nombre de usuario
        existing_user = await self.repository.get_by_username(command.username)
        if existing_user:
            raise BusinessRuleViolation(f"El nombre de usuario '{command.username}' ya existe")
            
        # 2. Validar si ya existe el email
        existing_email = await self.repository.get_by_email(command.email)
        if existing_email:
            raise BusinessRuleViolation(f"El email '{command.email}' ya está registrado")
            
        # 3. Hashear la contraseña
        hashed_password = AuthService.get_password_hash(command.password)
        
        # 4. Crear entidad de dominio
        user = User(
            username=command.username,
            email=command.email,
            hashed_password=hashed_password,
            full_name=command.full_name
        )
        
        # 5. Persistir
        return await self.repository.save(user)
