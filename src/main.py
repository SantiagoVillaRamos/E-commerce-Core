"""
Punto de entrada de la aplicación FastAPI.
Monta los routers de todos los módulos.
"""
from fastapi import FastAPI
from src.core.config import settings
from src.core.exception_handlers import register_exception_handlers
from src.modules.catalogo.api.router import router as catalogo_router
from src.modules.pedidos.api.router import router as pedidos_router


def create_app() -> FastAPI:
    """Factory para crear la aplicación FastAPI."""
    
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="1.0.0",
        description="API con manejo centralizado de excepciones"
    )
    
    # Registrar exception handlers globales
    register_exception_handlers(app)
    
    # Montar router del módulo Catálogo
    app.include_router(
        catalogo_router,
        prefix=f"{settings.api_v1_prefix}/catalogo",
        tags=["Catálogo"]
    )
    
    # Montar router del módulo Pedidos
    app.include_router(
        pedidos_router,
        prefix=f"{settings.api_v1_prefix}/pedidos",
        tags=["Pedidos"]
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "E-commerce Core API",
            "version": "1.0.0",
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
