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
    DATABASE_URL: str = Field(
        "postgresql://postgres:postgres@localhost:5433/tipsterbyte_fx_db",
        description="URL de conexión a base de datos",
    )
    POSTGRES_USER: str = Field("postgres", description="Usuario de PostgreSQL")
    POSTGRES_PASSWORD: str = Field("postgres", description="Contraseña de PostgreSQL")
    POSTGRES_DB: str = Field(
        "tipsterbyte_fx_db", description="Base de datos de PostgreSQL"
    )
    POSTGRES_HOST: str = Field("localhost", description="Host de PostgreSQL")
    POSTGRES_PORT: str = Field("5433", description="Puerto de PostgreSQL")

    DATABASE_POOL_SIZE: int = Field(
        5, description="Tamaño del pool de conexiones a la base de datos"
    )
    DATABASE_MAX_OVERFLOW: int = Field(
        10, description="Número máximo de conexiones adicionales al pool"
    )
    DATABASE_POOL_TIMEOUT: int = Field(30, description="Tiempo de espera del pool")

    MONGO_USER: str = Field("tipster_admin", description="Usuario de MongoDB")
    MONGO_PASSWORD: str = Field(
        "tipster_mongo_pass", description="Contraseña de MongoDB"
    )
    MONGO_HOST: str = Field("localhost", description="Host de MongoDB")
    MONGO_PORT: str = Field("27017", description="Puerto de MongoDB")
    MONGO_DB: str = Field(
        "tipsterbyte_fx_nosql_db", description="Base de datos de MongoDB"
    )
    MONGO_URI: str = Field(
        "mongodb://tipster_admin:tipster_mongo_pass@localhost:27017/tipsterbyte_fx_nosql_db?authSource=admin",
        description="URI de conexión completa para MongoDB",
    )
    MONGO_CONTAINER_NAME: str = Field(
        "db_mongo_tipsterbyte_fx_dev",
        description="Nombre del contenedor Docker de MongoDB",
    )

    POSTGRES_CONTAINER_NAME: str = Field(
        "db_pg_tipsterbyte_fx_dev",
        description="Nombre del contenedor Docker de PostgreSQL",
    )

    LOG_LEVEL: str = Field(
        "DEBUG", description="Nivel de logs: DEBUG, INFO, WARNING, ERROR"
    )
    EXECUTION_BASE_DIR: str = Field(
        "./executions", description="Directorio base de las ejecuciones de las tareas"
    )
    SELENIUM_HUB_URL: str = Field(
        "http://localhost:4444/wd/hub", description="Endpoint del hub de Selenium"
    )

    MAX_CONCURRENT_CLIENTS: int = Field(
        5, description="Número máximo de clientes a procesar concurrentemente"
    )
    SUPPORT_EMAIL: str = Field(
        "jdsolutions817@gmail.com", description="Email de soporte"
    )

    # --- Variables de Logs ---
    LOG_RETENTION_DAYS: int = Field(3, description="Días de retención de logs")
    LOG_ARCHIVE_RETENTION_DAYS: int = Field(
        30, description="Días de retención de logs archivados"
    )
    LOG_ARCHIVE_DIR: str = Field(
        "data/logs_archive", description="Directorio de logs archivados"
    )
    AUTO_CLEANUP_ENABLED: bool = Field(
        False, description="Habilitar limpieza automática de logs"
    )

    # --- Variables de Process Run Logging ---
    PROCESS_RUN_LOGGING_ENABLED: bool = Field(
        True,
        description="Controla si se escribe en las tablas process_run y process_run_log. Valores: true/1/yes = ESCRIBE en BD, false/0 = NO escribe (usa NoOp)",
    )

    # --- Variables de File Logging ---
    FILE_LOGGING_ENABLED: bool = Field(
        True,
        description="Controla si se escriben logs en archivos. Consola SIEMPRE activa. Valores: true = ESCRIBE en archivos, false = NO escribe en archivos",
    )

    # --- Variables de API-Football ---
    API_FOOTBALL_KEY: str = Field(
        "ddc44ff1c845c9c705b6f21d00926633",
        description="API key para API-Football v3",
    )
    API_FOOTBALL_HOST: str = Field(
        "v3.football.api-sports.io",
        description="Host de API-Football",
    )
    API_FOOTBALL_BASE_URL: str = Field(
        "https://v3.football.api-sports.io",
        description="URL base de API-Football",
    )

    # class Config:
    #     env_file = ".env"
    #     case_sensitive = True
    model_config = SettingsConfigDict(
        env_file=f"{BACKEND_ROOT}/.env", env_file_encoding="utf-8", case_sensitive=True
    )


try:
    settings: Settings = Settings()  # type: ignore[call-arg]
except ValidationError as e:
    print("\n" + "=" * 80)
    print("❌ ERROR CRÍTICO DE CONFIGURACIÓN ❌")
    print("=" * 80)
    print("\n🔍 VARIABLES FALTANTES O INCORRECTAS EN EL ARCHIVO .env:\n")

    # Extraer nombres de campos con error
    for error in e.errors():
        field_name = error.get("loc", ["unknown"])[0]
        print(f"   ❌ {field_name}")

    print("\n" + "-" * 80)
    print("📝 UBICACIÓN DEL ARCHIVO DE CONFIGURACIÓN:")
    print(f"   📁 {BACKEND_ROOT / 'core' / 'config.py'}")
    print("-" * 80)

    print("\n✅ SOLUCIÓN:")
    print("   1. Abre el archivo: backend/core/config.py")
    print("   2. Busca la clase 'Settings'")
    print("   3. Agrega las variables faltantes con sus valores por defecto:")
    print("\n   Ejemplo:")
    print("   ---")
    print(
        "   VARIABLE_FALTANTE: str = Field('valor_default', description='Descripción')"
    )
    print("   ---\n")

    print("📋 VARIABLES REQUERIDAS EN EL MODELO Settings:")
    print("   - ENV, DEBUG, DATABASE_URL, POSTGRES_USER, POSTGRES_PASSWORD")
    print("   - POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT")
    print("   - DATABASE_POOL_SIZE, DATABASE_MAX_OVERFLOW, DATABASE_POOL_TIMEOUT")
    print(
        "   - MONGO_USER, MONGO_PASSWORD, MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_URI"
    )
    print("   - LOG_LEVEL, EXECUTION_BASE_DIR, SELENIUM_HUB_URL")
    print("   - MAX_CONCURRENT_CLIENTS, SUPPORT_EMAIL")
    print(
        "   - LOG_RETENTION_DAYS, LOG_ARCHIVE_RETENTION_DAYS, LOG_ARCHIVE_DIR, AUTO_CLEANUP_ENABLED"
    )

    print("\n" + "=" * 80)
    print(f"📁 Ruta del .env: {BACKEND_ROOT / '.env'}")
    print(f"📁 Ruta del config.py: {BACKEND_ROOT / 'core' / 'config.py'}")
    print("=" * 80 + "\n")

    sys.exit(1)
