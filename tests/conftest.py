import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient
from sqlalchemy.pool import StaticPool

from src.main import app
from src.core.database import Base, get_db_session
from src.core.config import settings

# Usar SQLite en memoria para tests rápidos y aislados
# NOTA: En producción real con postgres-specifics, se usaría una DB de test en Postgres
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Crea una instancia del event loop para la sesión de tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Crea las tablas antes de los tests y las elimina al finalizar."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    """Fixture para obtener una sesión de base de datos limpia para cada test."""
    async with TestingSessionLocal() as session:
        yield session
        # Rollback para asegurar aislamiento entre tests
        await session.rollback()

@pytest.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Fixture para obtener un cliente HTTP que usa la base de datos de test."""
    
    async def override_get_db_session():
        yield session

    app.dependency_overrides[get_db_session] = override_get_db_session
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    del app.dependency_overrides[get_db_session]
