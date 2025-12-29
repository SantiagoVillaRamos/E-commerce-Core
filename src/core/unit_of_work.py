"""
Unit of Work Pattern para gestión de transacciones.

El patrón Unit of Work mantiene una lista de objetos afectados por una transacción
de negocio y coordina la escritura de cambios y la resolución de problemas de concurrencia.
"""
from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionLocal


class IUnitOfWork(ABC):
    """
    Interfaz del patrón Unit of Work.
    
    Define el contrato para gestionar transacciones de base de datos
    de manera consistente a través de la aplicación.
    """
    
    @abstractmethod
    async def __aenter__(self):
        """Inicia el contexto de la transacción."""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Finaliza el contexto de la transacción.
        
        Si hubo una excepción, hace rollback.
        Si todo fue exitoso, hace commit.
        """
        pass
    
    @abstractmethod
    async def commit(self):
        """Confirma todos los cambios de la transacción."""
        pass
    
    @abstractmethod
    async def rollback(self):
        """Revierte todos los cambios de la transacción."""
        pass


class SQLAlchemyUnitOfWork(IUnitOfWork):
    """
    Implementación del Unit of Work usando SQLAlchemy.
    
    Esta clase gestiona transacciones de base de datos asegurando
    que todas las operaciones se completen exitosamente o se reviertan
    en caso de error.
    
    Uso:
        async with SQLAlchemyUnitOfWork() as uow:
            # Realizar operaciones
            await repository.save(entity)
            await uow.commit()
    """
    
    def __init__(self, session: Optional[AsyncSession] = None):
        """
        Constructor.
        
        Args:
            session: Sesión de SQLAlchemy opcional. Si no se proporciona,
                    se creará una nueva sesión.
        """
        self._session = session
        self._session_factory = AsyncSessionLocal
        self._should_close = session is None
    
    async def __aenter__(self):
        """
        Inicia el contexto de la transacción.
        
        Returns:
            La sesión de base de datos activa
        """
        if self._session is None:
            self._session = self._session_factory()
        
        return self._session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Finaliza el contexto de la transacción.
        
        Si hubo una excepción, hace rollback automáticamente.
        """
        if exc_type is not None:
            await self.rollback()
        
        if self._should_close and self._session:
            await self._session.close()
            self._session = None
    
    async def commit(self):
        """
        Confirma todos los cambios de la transacción.
        
        Raises:
            Exception: Si hay un error al hacer commit
        """
        if self._session:
            await self._session.commit()
    
    async def rollback(self):
        """
        Revierte todos los cambios de la transacción.
        """
        if self._session:
            await self._session.rollback()
    
    @property
    def session(self) -> Optional[AsyncSession]:
        """Retorna la sesión actual."""
        return self._session
