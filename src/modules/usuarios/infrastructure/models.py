"""
Modelos de SQLAlchemy para el módulo de Usuarios.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, Uuid
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database import Base


# Tabla intermedia para Relación Muchos-a-Muchos entre Usuarios y Roles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Uuid, ForeignKey("users.user_id"), primary_key=True),
    Column("role_id", Uuid, ForeignKey("roles.role_id"), primary_key=True),
)

# Tabla intermedia para Relación Muchos-a-Muchos entre Roles y Permisos
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Uuid, ForeignKey("roles.role_id"), primary_key=True),
    Column("permission_id", Uuid, ForeignKey("permissions.permission_id"), primary_key=True),
)


class PermissionModel(Base):
    """Modelo para permisos del sistema."""
    __tablename__ = "permissions"

    permission_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)


class RoleModel(Base):
    """Modelo para roles de usuario."""
    __tablename__ = "roles"

    role_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    permissions = relationship("PermissionModel", secondary=role_permissions, backref="roles")


class UserModel(Base):
    """Modelo para usuarios del sistema."""
    __tablename__ = "users"

    user_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles = relationship("RoleModel", secondary=user_roles, backref="users")

    def __repr__(self):
        return f"<UserModel(username='{self.username}', email='{self.email}')>"
