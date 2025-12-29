"""
Entidades del dominio de Usuarios.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4


@dataclass
class Permission:
    """Entidad que representa un permiso en el sistema."""
    name: str
    permission_id: UUID = field(default_factory=uuid4)
    description: Optional[str] = None


@dataclass
class Role:
    """Entidad que representa un rol de usuario."""
    name: str
    role_id: UUID = field(default_factory=uuid4)
    description: Optional[str] = None
    permissions: List[Permission] = field(default_factory=list)

    def has_permission(self, permission_name: str) -> bool:
        """Verifica si el rol tiene un permiso específico."""
        return any(p.name == permission_name for p in self.permissions)


@dataclass
class User:
    """Entidad que representa un usuario del sistema."""
    username: str
    email: str
    hashed_password: str
    user_id: UUID = field(default_factory=uuid4)
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    roles: List[Role] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def has_role(self, role_name: str) -> bool:
        """Verifica si el usuario tiene un rol específico."""
        return any(r.name == role_name for r in self.roles)

    def has_permission(self, permission_name: str) -> bool:
        """Verifica si el usuario tiene un permiso específico a través de sus roles."""
        if self.is_superuser:
            return True
        return any(role.has_permission(permission_name) for role in self.roles)
