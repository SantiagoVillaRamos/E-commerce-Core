"""
Implementación del UserRepository usando SQLAlchemy.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.usuarios.domain.entities import User, Role, Permission
from src.modules.usuarios.domain.repositories import UserRepository
from src.modules.usuarios.infrastructure.models import UserModel, RoleModel, PermissionModel


class SQLAlchemyUserRepository(UserRepository):
    """
    Adaptador de repositorio para Usuarios usando SQLAlchemy.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: UserModel) -> User:
        """Mapea de modelo ORM a entidad de dominio."""
        roles = []
        
        # Acceder a relaciones solo si están cargadas para evitar MissingGreenlet
        if "roles" in model.__dict__:
            for role_model in model.roles:
                permissions = []
                if "permissions" in role_model.__dict__:
                    permissions = [
                        Permission(
                            permission_id=perm.permission_id,
                            name=perm.name,
                            description=perm.description
                        )
                        for perm in role_model.permissions
                    ]
                
                roles.append(
                    Role(
                        role_id=role_model.role_id,
                        name=role_model.name,
                        description=role_model.description,
                        permissions=permissions
                    )
                )
            
        return User(
            user_id=model.user_id,
            username=model.username,
            email=model.email,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            roles=roles,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def save(self, user: User) -> User:
        model = UserModel(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser
        )
        model.roles = []
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def update(self, user: User) -> User:
        stmt = select(UserModel).where(UserModel.user_id == user.user_id).options(
            selectinload(UserModel.roles).selectinload(RoleModel.permissions)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"Usuario con ID {user.user_id} no encontrado")
            
        model.username = user.username
        model.email = user.email
        model.hashed_password = user.hashed_password
        model.full_name = user.full_name
        model.is_active = user.is_active
        model.is_superuser = user.is_superuser
        
        # Nota: La gestión de roles compleja se puede añadir aquí si es necesario
        
        await self.session.flush()
        return self._to_domain(model)

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.user_id == user_id).options(
            selectinload(UserModel.roles).selectinload(RoleModel.permissions)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.username == username).options(
            selectinload(UserModel.roles).selectinload(RoleModel.permissions)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email).options(
            selectinload(UserModel.roles).selectinload(RoleModel.permissions)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        stmt = select(UserModel).options(
            selectinload(UserModel.roles).selectinload(RoleModel.permissions)
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]
