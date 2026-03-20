import sys
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, ValidationError
from pathlib import Path

# --- CAMBIO CLAVE: Importar la ruta desde el módulo centralizado ---
from core.paths import BACKEND_ROOT, PROJECT_ROOT

import os
from dotenv import load_dotenv

# Cargar archivo .env si existe
# env_path = Path(__file__).resolve().parent.parent / ".env"
env_path = BACKEND_ROOT / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path)

print(f"DEBUG: >>>>>>>> Cargando configuración desde {env_path}")
print(f"DEBUG: >>>>>>>> ENV = {os.getenv('ENV')}")
print(f"DEBUG: >>>>>>>> DEBUG = {os.getenv('DEBUG')}")
print(f"DEBUG: >>>>>>>> DATABASE_URL = {os.getenv('DATABASE_URL')}")
print(f"DEBUG: >>>>>>>> POSTGRES_USER = {os.getenv('POSTGRES_USER')}")
print(f"DEBUG: >>>>>>>> POSTGRES_PASSWORD = {os.getenv('POSTGRES_PASSWORD')}")
print(f"DEBUG: >>>>>>>> POSTGRES_DB = {os.getenv('POSTGRES_DB')}")
print(f"DEBUG: >>>>>>>> POSTGRES_HOST = {os.getenv('POSTGRES_HOST')}")
print(f"DEBUG: >>>>>>>> POSTGRES_PORT = {os.getenv('POSTGRES_PORT')}")
print(f"DEBUG: >>>>>>>> DATABASE_POOL_SIZE = {os.getenv('DATABASE_POOL_SIZE')}")
print(f"DEBUG: >>>>>>>> DATABASE_MAX_OVERFLOW = {os.getenv('DATABASE_MAX_OVERFLOW')}")
print(f"DEBUG: >>>>>>>> DATABASE_POOL_TIMEOUT = {os.getenv('DATABASE_POOL_TIMEOUT')}")
print(f"DEBUG: >>>>>>>> MONGO_USER = {os.getenv('MONGO_USER')}")
print(f"DEBUG: >>>>>>>> MONGO_PASSWORD = {os.getenv('MONGO_PASSWORD')}")
print(f"DEBUG: >>>>>>>> MONGO_HOST = {os.getenv('MONGO_HOST')}")
print(f"DEBUG: >>>>>>>> MONGO_PORT = {os.getenv('MONGO_PORT')}")
print(f"DEBUG: >>>>>>>> MONGO_DB = {os.getenv('MONGO_DB')}")
print(f"DEBUG: >>>>>>>> MONGO_URI = {os.getenv('MONGO_URI')}")
print(f"DEBUG: >>>>>>>> LOG_LEVEL = {os.getenv('LOG_LEVEL')}")
print(f"DEBUG: >>>>>>>> EXECUTION_BASE_DIR = {os.getenv('EXECUTION_BASE_DIR')}")
print(f"DEBUG: >>>>>>>> SELENIUM_HUB_URL = {os.getenv('SELENIUM_HUB_URL')}")
print(f"DEBUG: >>>>>>>> MAX_CONCURRENT_CLIENTS = {os.getenv('MAX_CONCURRENT_CLIENTS')}")
print(f"DEBUG: >>>>>>>> SUPPORT_EMAIL = {os.getenv('SUPPORT_EMAIL')}")
print(f"DEBUG: >>>>>>>>BACKEND_ROOT = {BACKEND_ROOT}")
print(f"DEBUG: >>>>>>>> PROJECT_ROOT = {PROJECT_ROOT}")

# --- CAMBIO CLAVE: Definir la raíz del backend para construir rutas ---
# BACKEND_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    # --- CAMBIO CLAVE: Añadir la nueva variable de configuración ---
    # Define la ruta a la carpeta donde Alembic guardará los scripts de migración.
    # TODO: COMMENT:
    # ALEMBIC_VERSIONS_DIR: Path = BACKEND_ROOT / "alembic" / "versions"
    # --- ESTA LÍNEA DEBE USAR BACKEND_ROOT ---
    ALEMBIC_VERSIONS_DIR: Path = BACKEND_ROOT / "alembic" / "versions"

    ENV: str = Field(
        "development", description="Entorno actual: development | production"
    )
    DEBUG: bool = Field(True, description="Modo debug")
    DATABASE_URL: str = Field(description="URL de conexión a base de datos")
    POSTGRES_USER: str = Field(description="Usuario de PostgreSQL")
    POSTGRES_PASSWORD: str = Field(description="Contraseña de PostgreSQL")
    POSTGRES_DB: str = Field(description="Base de datos de PostgreSQL")
    POSTGRES_HOST: str = Field(description="Host de PostgreSQL")
    POSTGRES_PORT: str = Field(description="Puerto de PostgreSQL")

    DATABASE_POOL_SIZE: int = Field(
        description="Tamaño del pool de conexiones a la base de datos"
    )
    DATABASE_MAX_OVERFLOW: int = Field(
        description="Número máximo de conexiones adicionales al pool"
    )
    DATABASE_POOL_TIMEOUT: int = Field(description="Tiempo de espera del pool")

    MONGO_USER: str = Field(description="Usuario de MongoDB")
    MONGO_PASSWORD: str = Field(description="Contraseña de MongoDB")
    MONGO_HOST: str = Field(description="Host de MongoDB")
    MONGO_PORT: str = Field(description="Puerto de MongoDB")
    MONGO_DB: str = Field(
        description="Base de datos de MongoDB"
    )  # Ya existe, asegurarse que se usa para el nombre de la BD
    MONGO_URI: str = Field(
        description="URI de conexión completa para MongoDB"
    )  # Nueva adición

    LOG_LEVEL: str = Field(
        "INFO", description="Nivel de logs: DEBUG, INFO, WARNING, ERROR"
    )
    EXECUTION_BASE_DIR: str = Field(
        description="Directorio base de las ejecuciones de las tareas"
    )
    SELENIUM_HUB_URL: str = Field(description="Endpoint del hub de Selenium")

    MAX_CONCURRENT_CLIENTS: int = Field(
        description="Número máximo de clientes a procesar concurrentemente"
    )
    SUPPORT_EMAIL: str = Field(description="Email de soporte")

    # class Config:
    #     env_file = ".env"
    #     case_sensitive = True
    model_config = SettingsConfigDict(
        env_file=f"{BACKEND_ROOT}/.env", env_file_encoding="utf-8", case_sensitive=True
    )


try:
    settings = Settings()
except ValidationError as e:
    print("\n" + "=" * 80)
    print("❌ ERROR CRÍTICO DE CONFIGURACIÓN ❌")
    print(
        "Faltan variables requeridas en el archivo .env o en las variables de entorno.\n"
    )
    print(str(e))
    print(
        "\nPor favor revisa el archivo .env y asegúrate de que todas las variables requeridas estén definidas."
    )
    print("=" * 80 + "\n")
    sys.exit(1)
    print(
        "Faltan variables requeridas en el archivo .env o en las variables de entorno.\n"
    )
    print(str(e))
    print(
        "\nPor favor revisa el archivo .env y asegúrate de que todas las variables requeridas estén definidas."
    )
    print("=" * 80 + "\n")
    sys.exit(1)
