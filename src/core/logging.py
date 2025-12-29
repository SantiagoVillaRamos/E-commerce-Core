"""
Configuración centralizada de logging usando Loguru.
"""
import sys
import logging
from loguru import logger
from src.core.config import settings

def setup_logging():
    """
    Configura Loguru como el manejador de logs principal.
    Intercepta los logs estándar de Python para centralizar todo en Loguru.
    """
    # Eliminar manejadores por defecto
    logger.remove()
    
    # Configurar salida a consola
    log_level = "DEBUG" if settings.debug else "INFO"
    
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # Opcional: Log a archivo
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="10 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

    # Interceptar logs de librerías (Alembic, SQLAlchemy, FastAPI)
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Obtener el nivel correspondiente de loguru
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Encontrar el llamador original
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    # Aplicar el interceptor a las librerías comunes
    for name in ("uvicorn", "uvicorn.error", "fastapi", "sqlalchemy.engine", "alembic"):
        log = logging.getLogger(name)
        log.handlers = [InterceptHandler()]
        log.propagate = False

    return logger
