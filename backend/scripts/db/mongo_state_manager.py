# filepath: c:\Users\JaimeIvanDiazGaona\Documents\proyectos_jdiaz\tipsterByte_fx\backend\scripts\db\mongo_state_manager.py
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import typer
from loguru import logger

# Añadir la raíz del proyecto al sys.path para que encuentre 'core'
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from core.config import settings
from core.logger import configure_logging

app = typer.Typer(help="Gestiona el estado de la base de datos NoSQL (MongoDB).")

# Constantes para MongoDB
DOCKER_MONGO_CONTAINER_NAME = "db_mongo_tipsterbyte_fx"
# --- CAMBIO CLAVE: Definimos la nueva ruta del directorio de backups ---
MONGO_BACKUP_DIR_PATH = project_root / "backups" / "mongo_backups"

# --- NUEVA FUNCIÓN HELPER ---
def _find_latest_backup(backup_dir: Path) -> Path | None:
    """Función helper para encontrar el último backup de MongoDB."""
    if not backup_dir.is_dir(): return None
    # Buscamos archivos .gz que son los backups de mongo
    backups = list(backup_dir.glob("*.gz"))
    if not backups: return None
    # Usamos st_ctime (tiempo de creación) para encontrar el más reciente
    return max(backups, key=lambda f: f.stat().st_birthtime)

@app.command("backup")
def backup_mongo_database():
    """Crea un backup de la BD MongoDB ejecutando mongodump DENTRO del contenedor."""
    configure_logging()
    logger.info("🚀 Iniciando proceso de backup de MongoDB vía Docker...")
    
    # --- CAMBIO CLAVE: Usamos la nueva ruta y nos aseguramos de que exista ---
    MONGO_BACKUP_DIR_PATH.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{settings.MONGO_DB}_{timestamp}.gz"
    backup_file_path_host = MONGO_BACKUP_DIR_PATH / backup_name
    
    # La ruta DENTRO del contenedor. La estandarizamos a /backups/
    backup_path_container = f"/backups/{backup_name}"

    command = [
        "docker", "exec", DOCKER_MONGO_CONTAINER_NAME,
        "mongodump",
        f"--username={settings.MONGO_USER}",
        f"--password={settings.MONGO_PASSWORD}",
        "--authenticationDatabase=admin",
        f"--db={settings.MONGO_DB}",
        f"--archive={backup_path_container}",
        "--gzip"
    ]

    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        logger.success(f"✅ Backup de MongoDB completado exitosamente en: {backup_file_path_host}")
    except subprocess.CalledProcessError as e:
        logger.error("❌ Error al ejecutar el comando mongodump en Docker.")
        logger.error(f"Stderr: {e.stderr}")
    except Exception as e:
        logger.error(f"❌ Ocurrió un error inesperado durante el backup de MongoDB: {e}")

@app.command("restore")
def restore_mongo_database(
    # --- CAMBIO CLAVE: Hacemos el parámetro 'file' opcional (de ... a None) ---
    file: Path = typer.Option(None, "--file", "-f", help="Ruta opcional al archivo de backup de MongoDB a restaurar.")
):
    """
    Restaura la BD MongoDB desde un backup ejecutando mongorestore.
    Ejemplo de uso:
        python mongo_state_manager.py restore --file backups/mongo_backups/backup_mibd_20240610_120000.gz    
    """
    configure_logging()
    logger.info("🚀 Iniciando proceso de restauración de MongoDB vía Docker...")
    
    # --- CAMBIO CLAVE: Añadimos la lógica para buscar el último backup ---
    if not file:
        logger.info("No se especificó un archivo. Buscando el último backup de MongoDB...")
        file = _find_latest_backup(MONGO_BACKUP_DIR_PATH)    

    if not file.exists():
        logger.error(f"❌ No se encontró el archivo de backup: {file}")
        raise typer.Exit(code=1)

    typer.secho("¡ADVERTENCIA! ESTA OPERACIÓN ES REGENERATIVA - CONSTRUCTIVAS.", fg=typer.colors.RED, bold=True)
    logger.warning(f"Se borrarán los datos actuales de la base de datos '{settings.MONGO_DB}' antes de restaurar.")
    confirmation = typer.prompt(f"Para confirmar, escribe el nombre de la base de datos MongoDB: '{settings.MONGO_DB}'")
    if confirmation != settings.MONGO_DB:
        logger.info("❌ La confirmación no coincide. Proceso cancelado.")
        raise typer.Exit()

    # La ruta DENTRO del contenedor. La estandarizamos a /backups/
    backup_path_container = f"/backups/{file.name}"

    command = [
        "docker", "exec", DOCKER_MONGO_CONTAINER_NAME,
        "mongorestore",
        f"--username={settings.MONGO_USER}",
        f"--password={settings.MONGO_PASSWORD}",
        "--authenticationDatabase=admin",
        f"--db={settings.MONGO_DB}",
        f"--archive={backup_path_container}",
        "--gzip",
        "--drop"
    ]

    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        logger.success(f"✅ Restauración de MongoDB completada exitosamente desde: {file.name}")
    except subprocess.CalledProcessError as e:
        logger.error("❌ Error al ejecutar el comando mongorestore en Docker.")
        logger.error(f"Stderr: {e.stderr}")
    except Exception as e:
        logger.error(f"❌ Ocurrió un error inesperado durante la restauración de MongoDB: {e}")

@app.command("reset")
def reset_mongo_database():
    """Borra (drop) la base de datos MongoDB completa."""
    configure_logging()
    typer.secho("¡ADVERTENCIA MÁXIMA! ESTÁS A PUNTO DE BORRAR LA BASE DE DATOS MONGO.", fg=typer.colors.RED, bold=True)
    logger.warning(f"Esto afectará a la base de datos: '{settings.MONGO_DB}'.")
    confirmation = typer.prompt(f"Para confirmar esta operación, escribe el nombre de la base de datos: '{settings.MONGO_DB}'")
    if confirmation != settings.MONGO_DB:
        logger.info("❌ La confirmación no coincide. Proceso cancelado.")
        raise typer.Exit()

    drop_command = f"db.getSiblingDB('{settings.MONGO_DB}').dropDatabase()"
    
    command = [
        "docker", "exec", DOCKER_MONGO_CONTAINER_NAME,
        "mongo",
        settings.MONGO_DB,
        "-u", settings.MONGO_USER,
        "-p", settings.MONGO_PASSWORD,
        "--authenticationDatabase", "admin",
        "--eval", drop_command
    ]

    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        logger.success(f"✅ Base de datos MongoDB '{settings.MONGO_DB}' reseteada exitosamente.")
    except subprocess.CalledProcessError as e:
        logger.error("❌ Error al ejecutar el comando de reseteo en Docker.")
        logger.error(f"Stderr: {e.stderr}")
    except Exception as e:
        logger.error(f"❌ Ocurrió un error inesperado durante el reseteo de MongoDB: {e}")

if __name__ == "__main__":
    app()