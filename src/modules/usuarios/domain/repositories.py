"""
Interfaz de repositorio para la persistencia de usuarios.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from src.modules.usuarios.domain.entities import User


class UserRepository(ABC):
    """
    Puerto (Interface) para el repositorio de usuarios.
    """
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """Guarda un nuevo usuario."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Actualiza un usuario existente."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Busca un usuario por su ID."""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Busca un usuario por su nombre de usuario."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Busca un usuario por su email."""
        pass
    
    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Lista todos los usuarios."""
        pass
