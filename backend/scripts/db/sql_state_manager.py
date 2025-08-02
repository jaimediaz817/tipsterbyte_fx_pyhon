# filepath: c:\Users\JaimeIvanDiazGaona\Documents\proyectos_jdiaz\tipsterByte_fx\backend\scripts\db\state_manager.py
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import typer
from sqlalchemy import create_engine, text
from loguru import logger

# Añadir la raíz del proyecto al sys.path para que encuentre 'core'
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from core.config import settings
from core.logger import configure_logging

# Creamos una mini-app de Typer para este módulo.
# Esto nos permite tener subcomandos como 'backup', 'restore' y 'reset'.
# app = typer.Typer(help="Gestiona el estado de la base de datos (backups, restauraciones, reseteos).")
app = typer.Typer(help="Gestiona el estado de la base de datos SQL (PostgreSQL).")

# Constantes para PostgreSQL
DOCKER_POSTGRES_CONTAINER_NAME = "db_pg_tipsterbyte_fx"
# --- CAMBIO CLAVE: Definimos la nueva ruta del directorio de backups ---
SQL_BACKUP_DIR_PATH = project_root / "backups" / "postgresql_backups"

def _find_latest_backup(backup_dir: Path) -> Path | None:
    """Función helper para encontrar el último backup."""
    if not backup_dir.is_dir(): return None
    backups = list(backup_dir.glob("*.sql"))
    if not backups: return None
    
    # return max(backups, key=lambda f: f.stat().st_ctime)
    # Usar st_mtime (modificación) en vez de st_ctime (creación), para mayor compatibilidad cross-platform
    return max(backups, key=lambda f: f.stat().st_mtime)

def _drop_and_create_db():
    """Función helper para conectarse al servidor de BD y recrear la base de datos."""
    # Nos conectamos a una BD de mantenimiento (como 'postgres') para poder operar sobre nuestra BD
    server_url = str(settings.DATABASE_URL).replace(f"/{settings.POSTGRES_DB}", "/postgres")
    engine = create_engine(server_url, isolation_level="AUTOCOMMIT")
    
    try:
        with engine.connect() as connection:
            logger.warning(f"Intentando borrar la base de datos '{settings.POSTGRES_DB}'...")
            # Usamos FORCE para desconectar a otros usuarios que puedan estar conectados
            connection.execute(text(f'DROP DATABASE IF EXISTS "{settings.POSTGRES_DB}" WITH (FORCE)'))
            logger.info("Base de datos borrada.")
            
            logger.info(f"Intentando crear la base de datos '{settings.POSTGRES_DB}'...")
            connection.execute(text(f'CREATE DATABASE "{settings.POSTGRES_DB}"'))
            logger.info("Base de datos creada.")
    except Exception as e:
        logger.error(f"❌ Ocurrió un error al intentar borrar/crear la base de datos: {e}")
        raise typer.Exit(code=1)
    finally:
        engine.dispose()

@app.command("backup")
def backup_database(return_path: bool = typer.Option(False, hidden=True)) -> Path | None:
    """Crea un backup de la BD PostgreSQL ejecutando pg_dump DENTRO del contenedor."""
    configure_logging()
    logger.info("🚀 Iniciando proceso de backup de PostgreSQL vía Docker...")
    
    # --- CAMBIO CLAVE: Usamos la nueva ruta y nos aseguramos de que exista ---
    SQL_BACKUP_DIR_PATH.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{settings.POSTGRES_DB}_{timestamp}.sql"
    backup_file_path_host = SQL_BACKUP_DIR_PATH / backup_filename
    
    backup_file_path_container = f"/backups/{backup_filename}"

    command = [
        "docker", "exec",
        "-e", f"PGPASSWORD={settings.POSTGRES_PASSWORD}",
        DOCKER_POSTGRES_CONTAINER_NAME,
        "pg_dump",
        "--username", settings.POSTGRES_USER,
        "--dbname", settings.POSTGRES_DB,
        "--file", backup_file_path_container,
        "--format", "c",
        "--verbose"
    ]

    try:
        # Ya no necesitamos pasar `env` porque lo incluimos en el comando docker
        subprocess.run(command, capture_output=True, text=True, check=True)
        logger.success(f"✅ Backup completado exitosamente en: {backup_file_path_host}")
        if return_path:
            return backup_file_path_host
    except subprocess.CalledProcessError as e:
        logger.error("❌ Error al ejecutar el comando de backup en Docker.")
        logger.error(f"Stderr: {e.stderr}") # Stderr es muy útil para ver los errores de pg_dump
        if return_path:
            return None
    except Exception as e:
        logger.error(f"❌ Ocurrió un error inesperado durante el backup: {e}")
        if return_path:
            return None
        
@app.command("restore")
def restore_database(
    file: Path = typer.Option(None, "--file", "-f", help="Ruta opcional al archivo .sql del backup a restaurar."),
    skip_confirmation: bool = typer.Option(False, hidden=True)
):
    """Restaura la BD desde un backup ejecutando pg_restore DENTRO del contenedor."""
    configure_logging()
    if not skip_confirmation:
        logger.info("🚀 Iniciando proceso de restauración de PostgreSQL vía Docker...")
    
    if not file:
        logger.info("No se especificó un archivo. Buscando el último backup...")
        # --- CAMBIO CLAVE: Buscamos en la nueva ruta ---
        file = _find_latest_backup(SQL_BACKUP_DIR_PATH)

    if not file or not file.exists():
        logger.error(f"❌ No se encontró el archivo de backup: {file}")
        raise typer.Exit(code=1)

    if not skip_confirmation:
        logger.error("¡ADVERTENCIA! ESTA OPERACIÓN ES REGENERATIVA.")
        logger.warning(f"Se llevará a cabo un proceso de restauración en la base de datos '{settings.POSTGRES_DB}'.")
        confirmation = typer.prompt(f"Para confirmar, escribe el nombre de la base de datos '{settings.POSTGRES_DB}'")
        if confirmation != settings.POSTGRES_DB:
            logger.info("❌ La confirmación no coincide. Proceso cancelado.")
            raise typer.Exit()

    backup_file_path_container = f"/backups/{file.name}"

    command = [
        "docker", "exec",
        "-e", f"PGPASSWORD={settings.POSTGRES_PASSWORD}",
        DOCKER_POSTGRES_CONTAINER_NAME,
        "pg_restore",
        "--username", settings.POSTGRES_USER,
        "--dbname", settings.POSTGRES_DB,
        "--clean",
        "--if-exists",
        "--verbose",
        backup_file_path_container
    ]

    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        logger.success("✅ Restauración completada. Recuerda ejecutar 'alembic upgrade head' para sincronizar.")
    except subprocess.CalledProcessError as e:
        logger.error("❌ Error al ejecutar el comando de restauración en Docker.")
        logger.error(f"Stderr: {e.stderr}")
    except Exception as e:
        logger.error(f"❌ Ocurrió un error inesperado durante la restauración: {e}")

@app.command("reset")
def reset_database(
    hard: bool = typer.Option(False, "--hard", help="Modo destructivo: Borra la BD, la recrea y migra. PIERDE TODOS LOS DATOS."),
    with_backup: bool = typer.Option(False, "--with-backup", help="Modo seguro: Hace backup, resetea y restaura los datos."),
):
    """Resetea la base de datos. Debes elegir un modo: --hard o --with-backup."""
    configure_logging()
    if not hard and not with_backup:
        logger.error("❌ Debes especificar un modo de reseteo. Usa --hard o --with-backup.")
        raise typer.Exit(code=1)
    if hard and with_backup:
        logger.error("❌ Los modos --hard y --with-backup son mutuamente excluyentes.")
        raise typer.Exit(code=1)

    mode_description = "MODO DESTRUCTIVO (--hard)" if hard else "MODO SEGURO (--with-backup)"
    logger.error(f"¡ADVERTENCIA MÁXIMA! ESTÁS A PUNTO DE RESETEAR LA BASE DE DATOS.")
    logger.warning(f"Modo seleccionado: {mode_description}")
    logger.warning(f"Esto afectará a la base de datos: '{settings.POSTGRES_DB}' en el host '{settings.POSTGRES_HOST}'.")
    confirmation = typer.prompt(f"Para confirmar esta operación, escribe el nombre de la base de datos '{settings.POSTGRES_DB}'")
    if confirmation != settings.POSTGRES_DB:
        logger.info("❌ La confirmación no coincide. Proceso cancelado.")
        raise typer.Exit()

    logger.info("Confirmación aceptada. Procediendo con el reseteo...")
    if with_backup:
        logger.info("Paso 1/4: Creando backup...")
        backup_path = backup_database(return_path=True)
        if not backup_path: raise typer.Exit(code=1)
        logger.info("Paso 2/4: Borrando y recreando la base de datos...")
        _drop_and_create_db()
        logger.info("Paso 3/4: Restaurando datos desde el backup...")
        restore_database(file=backup_path, skip_confirmation=True)
        logger.info("Paso 4/4: Aplicando migraciones pendientes...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
    if hard:
        logger.info("Paso 1/2: Borrando y recreando la base de datos...")
        _drop_and_create_db()
        logger.info("Paso 2/2: Aplicando todas las migraciones...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
    logger.success("✅ Proceso de reseteo completado exitosamente.")

if __name__ == "__main__":
    app()