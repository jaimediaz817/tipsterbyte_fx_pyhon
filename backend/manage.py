import asyncio
from datetime import datetime
import subprocess
import typer
from loguru import logger

# --- 1. IMPORTACIONES DE MÓDULOS DEL PROYECTO ---
# Se agrupan las importaciones por su origen para mayor claridad.

# --- 1. IMPORTACIONES DE MÓDULOS DEL PROYECTO ---
# Se agrupan las importaciones por su origen para mayor claridad.

# Core
from core.logger import configure_logging

# Scripts de gestión de estado de las bases de datos
from scripts.db.sql_state_manager import app as sql_state_app
from scripts.db.mongo_state_manager import app as mongo_state_app

# Scripts para poblar las bases de datos (Seeders)
from scripts.db.seeders.sql.seed_database_sql import seed_sql_data_auth_module
from scripts.db.seeders.no_sql.seed_database_no_sql import seed_nosql_data_auth_module # Asumiendo que el seeder de mongo se llama así para consistencia
from scripts.db.migrations.nosql.migration_add_process_name_to_access_logs import run_migration as run_mongo_migration_001


# --- 2. APLICACIÓN PRINCIPAL DE TYPER ---
# Este es el punto de entrada para todos los comandos.
app = typer.Typer(
    name="TipsterByte FX Manager",
    help="Herramienta de gestión centralizada para el backend del proyecto.",
    no_args_is_help=True # Muestra la ayuda si no se pasan argumentos
)



# --- 3. SECCIÓN DE COMANDOS PARA POSTGRESQL (SQL) ---
# Todos los comandos relacionados con la base de dato

# --- Sub-comando para la Base de Datos SQL (PostgreSQL) ---
# db_app = typer.Typer()
# app.add_typer(db_app, name="db", help="Comandos para la gestión de la base de datos SQL.")
db_app = typer.Typer(name="sql", help="Gestiona la base de datos SQL (PostgreSQL).")
app.add_typer(db_app)

@db_app.command("create-migration")
def db_create_migration(message: str | None = typer.Argument(None, help="Mensaje descriptivo. Si se omite, se genera uno automático.")):
    """Genera un nuevo archivo de migración de Alembic."""
    configure_logging()
    
    # --- CAMBIO CLAVE: Añadimos la lógica para el mensaje automático ---
    if not message:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        message = f"auto_migration_{timestamp}"
        logger.info("No se proporcionó mensaje. Usando mensaje autogenerado.")

    logger.info(f"Generando migración con mensaje: '{message}'")
    try:
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", message], check=True)
        logger.success("✅ Archivo de migración generado exitosamente.")
    except Exception as e:
        logger.error(f"❌ Falló la generación de la migración. Error: {e}")

@db_app.command("migrate")
def db_migrate():
    """Aplica todas las migraciones pendientes a la base de datos SQL."""
    configure_logging()
    logger.info("Aplicando migraciones SQL a la base de datos...")
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logger.success("✅ Migraciones aplicadas exitosamente.")
    except Exception as e:
        logger.error(f"❌ Falló la aplicación de las migraciones. Error: {e}")

# --- CAMBIO CLAVE: Añadimos el comando 'seed' ---
@db_app.command("seed")
def db_seed():
    
    """
    Puebla la base de datos con datos iniciales (roles, usuario admin, etc.).
    """
    seed_sql_data_auth_module()

# Anidamos la app de backup/restore/reset dentro de los comandos de 'db'
db_app.add_typer(sql_state_app, name="state", help="Gestiona el estado de la BD (backups/restauraciones/reseteos).")


# --- 4. SECCIÓN DE COMANDOS PARA MONGODB (NOSQL) ---
# Todos los comandos relacionados con la base de datos NoSQL viven aquí.
# Se invocarán con: python manage.py mongo <comando>
mongo_app = typer.Typer(name="nosql", help="Gestiona la base de datos NoSQL (MongoDB).")
app.add_typer(mongo_app)

@mongo_app.command("seed")
def mongo_seed():
    """Puebla la base de datos MongoDB con datos de ejemplo (señales, logs, etc.)."""
    asyncio.run(seed_nosql_data_auth_module())
    
    
# Anidamos los comandos de backup/restore/reset para MongoDB
mongo_app.add_typer(mongo_state_app, name="state", help="Gestiona el estado de la BD NoSQL (backup/restore/reset).")
    
  
# --- CAMBIO CLAVE: Añadimos la nueva sección para migraciones de datos de MongoDB ---
mongo_migrations_app = typer.Typer(name="nosql-migrate", help="Ejecuta migraciones de datos para MongoDB.")
app.add_typer(mongo_migrations_app)

@mongo_migrations_app.command("run")
def run_mongo_migrations():
    """Añade campos faltantes a documentos existentes según los nuevos modelos."""
    configure_logging()
    logger.info("Iniciando proceso de migración de datos de MongoDB...")
    # Aquí podrías tener una lógica para ejecutar varias migraciones en orden
    asyncio.run(run_mongo_migration_001())
    logger.info("Proceso de migración de MongoDB finalizado.")  
    
# --- 5. SECCIÓN DE COMANDOS PARA EL SERVIDOR WEB ---
# Comandos para iniciar y gestionar el servidor de desarrollo.
# Se invocarán con: python manage.py server <comando>
server_app = typer.Typer(name="server", help="Gestiona el servidor web de desarrollo.")
app.add_typer(server_app)
# app.add_typer(server_app, name="server", help="Comandos para el servidor web.")

@server_app.command("run")
def server_run(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    """Inicia el servidor web Uvicorn con recarga automática."""
    configure_logging()
    logger.info(f"Iniciando servidor en http://{host}:{port}")
    command = ["uvicorn", "main_init_web_server:app", f"--host={host}", f"--port={port}"]
    if reload:
        command.append("--reload")
    subprocess.run(command)

if __name__ == "__main__":
    app()