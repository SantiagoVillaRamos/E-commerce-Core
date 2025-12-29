"""
Configuración de la aplicación usando pydantic-settings.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Configuración global de la aplicación.
    
    Se utiliza la librería 'os' para obtener los valores de la base de datos,
    asegurando una conexión explícita con las variables definidas en .env o Docker.
    """
    
    # Database (uso explícito de os.getenv)
    db_user: str = Field(default_factory=lambda: os.getenv("DB_USER", "ecommerce"))
    db_password: str = Field(default_factory=lambda: os.getenv("DB_PASSWORD", "ecommerce123"))
    db_name: str = Field(default_factory=lambda: os.getenv("DB_NAME", "ecommerce"))
    db_host: str = Field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    db_port: int = Field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    
    # DATABASE_URL can still be provided directly to override everything
    database_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    
    # Security
    secret_key: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", "your-super-secret-key-for-dev-only"))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    app_name: str = Field(default_factory=lambda: os.getenv("APP_NAME", "E-commerce Core"))
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "True").lower() == "true")
    
    # API
    api_v1_prefix: str = "/api/v1"
    
    @property
    def get_database_url(self) -> str:
        """
        Retorna la URL de la base de datos.
        Si 'database_url' no está definida, la construye a partir de los campos individuales.
        """
        if self.database_url:
            return self.database_url
            
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Singleton de configuración
settings = Settings()
