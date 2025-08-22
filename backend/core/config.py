from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path

# --- CAMBIO CLAVE: Importar la ruta desde el módulo centralizado ---
from core.paths import BACKEND_ROOT

import os
from dotenv import load_dotenv

# Cargar archivo .env si existe
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# --- CAMBIO CLAVE: Definir la raíz del backend para construir rutas ---
# BACKEND_ROOT = Path(__file__).resolve().parent.parent



class Settings(BaseSettings):
    
    # --- CAMBIO CLAVE: Añadir la nueva variable de configuración ---
    # Define la ruta a la carpeta donde Alembic guardará los scripts de migración.
    # TODO: COMMENT:
    # ALEMBIC_VERSIONS_DIR: Path = BACKEND_ROOT / "alembic" / "versions" 
    # --- ESTA LÍNEA DEBE USAR BACKEND_ROOT ---
    ALEMBIC_VERSIONS_DIR: Path = BACKEND_ROOT / "alembic" / "versions"
    
    ENV: str                = Field("development", description="Entorno actual: development | production")
    DEBUG: bool             = Field(True, description="Modo debug")
    DATABASE_URL: str       = Field(description="URL de conexión a base de datos")
    POSTGRES_USER: str      = Field(description="Usuario de PostgreSQL")
    POSTGRES_PASSWORD: str  = Field(description="Contraseña de PostgreSQL")
    POSTGRES_DB: str        = Field(description="Base de datos de PostgreSQL")
    POSTGRES_HOST: str      = Field(description="Host de PostgreSQL")
    POSTGRES_PORT: str      = Field(description="Puerto de PostgreSQL")

    DATABASE_POOL_SIZE: int    = Field(description="Tamaño del pool de conexiones a la base de datos")
    DATABASE_MAX_OVERFLOW: int = Field(description="Número máximo de conexiones adicionales al pool")
    DATABASE_POOL_TIMEOUT: int = Field(description="Tiempo de espera del pool")

    MONGO_USER: str       = Field(description="Usuario de MongoDB")
    MONGO_PASSWORD: str   = Field(description="Contraseña de MongoDB")
    MONGO_HOST: str       = Field(description="Host de MongoDB")
    MONGO_PORT: str       = Field(description="Puerto de MongoDB")
    MONGO_DB: str         = Field(description="Base de datos de MongoDB")  # Ya existe, asegurarse que se usa para el nombre de la BD
    MONGO_URI: str        = Field(description="URI de conexión completa para MongoDB")  # Nueva adición

    LOG_LEVEL: str          = Field("INFO", description="Nivel de logs: DEBUG, INFO, WARNING, ERROR")
    EXECUTION_BASE_DIR: str = Field(description="Directorio base de las ejecuciones de las tareas")
    SELENIUM_HUB_URL: str   = Field(description="Endpoint del hub de Selenium")
    
    # class Config:
    #     env_file = ".env"
    #     case_sensitive = True
    model_config = SettingsConfigDict(
        env_file=f"{BACKEND_ROOT}/.env",
        env_file_encoding='utf-8',
        case_sensitive=True
    )    


settings = Settings()
