"""
Configuración de la base de datos con SQLAlchemy.
Motor y sesión compartidos por todos los módulos.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src.core.config import settings


# Convertir URL de PostgreSQL a async
async_database_url = settings.get_database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# Motor de base de datos (Singleton)
engine = create_async_engine(
    async_database_url,
    echo=settings.debug,
    future=True
)

# Factory de sesiones
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


from datetime import datetime
from sqlalchemy import Column, DateTime


class SoftDeleteMixin:
    """Mixin para agregar funcionalidad de borrado lógico."""
    deleted_at = Column(DateTime, nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()


class Base(DeclarativeBase):
    """Clase base para todos los modelos SQLAlchemy."""
    pass


async def get_db_session() -> AsyncSession:
    """
    Dependency para obtener una sesión de base de datos.
    Uso en FastAPI: Depends(get_db_session)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
