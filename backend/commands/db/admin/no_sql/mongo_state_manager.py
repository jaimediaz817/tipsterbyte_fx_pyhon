# filepath: c:\Users\JaimeIvanDiazGaona\Documents\proyectos_jdiaz\tipsterByte_fx\backend\scripts\db\mongo_state_manager.py
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from beanie import init_beanie
import typer
from loguru import logger
# --- NUEVAS IMPORTACIONES ---
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# # Añadir la raíz (backend) al sys.path para que encuentre 'core'
# project_root = Path(__file__).resolve().parents[4]
# sys.path.append(str(project_root))

# --- CAMBIO CLAVE: Importar las rutas centralizadas ---
from core.db.no_sql.schema_initializer import _find_beanie_models
from core.paths import PROJECT_ROOT, BACKEND_ROOT
from core.config import settings
from core.logger import configure_logging

app = typer.Typer(help="Gestiona el estado de la base de datos NoSQL (MongoDB).")

# Constantes para MongoDB
DOCKER_MONGO_CONTAINER_NAME = "db_mongo_tipsterbyte_fx"

# --- CAMBIO CLAVE: Usar BACKEND_ROOT para que coincida con el volumen de Docker ---
NOSQL_BACKUP_DIR_PATH = BACKEND_ROOT / "backups" / "mongo_backups"

# Constantes para MongoDB
DOCKER_MONGO_CONTAINER_NAME = "db_mongo_tipsterbyte_fx"

# TODO: COMENTADO: DEPRECADO: TESTING
# --- CAMBIO CLAVE: Definimos la nueva ruta del directorio de backups ---
# MONGO_BACKUP_DIR_PATH = project_root / "backups" / "mongo_backups"

# --- NUEVA FUNCIÓN HELPER ---
def _find_latest_backup(backup_dir: Path) -> Path | None:
    """Función helper para encontrar el último backup de MongoDB."""
    if not backup_dir.is_dir(): return None
    # Buscamos archivos .gz que son los backups de mongo
    backups = list(backup_dir.glob("*.gz"))
    if not backups: return None
    # Usamos st_ctime (tiempo de creación) para encontrar el más reciente
    return max(backups, key=lambda f: f.stat().st_birthtime)

# --- NUEVA FUNCIÓN HELPER PARA EL RESUMEN ---
async def _show_restore_summary():
    """Se conecta a la BD y muestra un resumen del estado actual de las colecciones."""
    logger.info("--- Resumen de la Base de Datos Restaurada ---")
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[settings.MONGO_DB]
        
        # Verificamos la conexión antes de continuar
        await client.admin.command('ping')

        collections = await db.list_collection_names()
        if not collections:
            logger.warning("La base de datos está vacía o no tiene colecciones.")
            return

        for coll_name in sorted(collections):
            # Ignoramos las colecciones internas del sistema
            if coll_name.startswith("system."):
                continue
            
            count = await db[coll_name].count_documents({})
            logger.info(f"  -> Colección '{coll_name}': {count} documentos.")

    except Exception as e:
        logger.error(f"No se pudo generar el resumen post-restauración: {e}")
    finally:
        if 'client' in locals():
            client.close()

# --- NUEVA FUNCIÓN DE LÓGICA PARA 'STATUS' ---
async def _get_nosql_status():
    """Encuentra todos los modelos, se conecta a la BD y muestra su estado."""
    logger.info("🔍 Verificando estado de la base de datos NoSQL (MongoDB)...")
    
    models = _find_beanie_models()
    if not models:
        logger.warning("No se encontraron modelos de Beanie en el proyecto.")
        return

    typer.secho(f"\n--- Resumen de {len(models)} Modelos Encontrados ---", fg=typer.colors.CYAN, bold=True)
    
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=3000)
        db = client[settings.MONGO_DB]
        
        # Es crucial inicializar Beanie para poder usar los modelos para contar
        await init_beanie(database=db, document_models=models)

        for model in sorted(models, key=lambda m: m.Settings.name):
            collection_name = model.Settings.name
            schema_name = collection_name.split('.', 1)[0] if '.' in collection_name else "default"
            
            try:
                count = await model.count()
                status_color = typer.colors.GREEN if count > 0 else typer.colors.YELLOW
                count_str = f"{count} documentos"
            except Exception:
                status_color = typer.colors.RED
                count_str = "Error al contar"

            typer.echo(
                f"Schema: " + typer.style(f"{schema_name.ljust(15)}", fg=typer.colors.BLUE) +
                f"Colección: " + typer.style(f"{collection_name.ljust(30)}", fg=typer.colors.MAGENTA) +
                f"Estado: " + typer.style(count_str, fg=status_color)
            )
            
    except Exception as e:
        logger.error(f"❌ No se pudo conectar a MongoDB para verificar el estado: {e}")
    finally:
        if 'client' in locals():
            client.close()

@app.command("backup")
def backup_mongo_database():
    """Crea un backup de la BD MongoDB ejecutando mongodump DENTRO del contenedor."""
    configure_logging()
    logger.info("🚀 Iniciando proceso de backup de MongoDB vía Docker...")
    
    # --- CAMBIO CLAVE: Usamos la nueva ruta y nos aseguramos de que exista ---
    NOSQL_BACKUP_DIR_PATH.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{settings.MONGO_DB}_{timestamp}.gz"
    backup_file_path_host = NOSQL_BACKUP_DIR_PATH / backup_name
    
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
    file: Path = typer.Option(None, "--file", "-f", help="Ruta opcional al archivo de backup de MongoDB a restaurar.")
):
    """
    Restaura la BD MongoDB desde un backup ejecutando mongorestore.
    Ejemplo de uso:
        python manage.py nosql state restore --file backups/mongo_backups/backup_mibd_20240610_120000.gz    
    """
    configure_logging()
    logger.info("🚀 Iniciando proceso de restauración de MongoDB vía Docker...")
    
    backup_to_restore = file

    # --- LÓGICA DE BÚSQUEDA MEJORADA ---
    if not backup_to_restore:
        logger.info("No se especificó un archivo. Buscando el último backup de MongoDB...")
        if not NOSQL_BACKUP_DIR_PATH.exists():
            logger.warning(f"El directorio de backups no existe: {NOSQL_BACKUP_DIR_PATH.resolve()}")
        
        backup_to_restore = _find_latest_backup(NOSQL_BACKUP_DIR_PATH)

    # --- CAMBIO CLAVE: Añadir la validación que falta ---
    # Si después de todo, no tenemos un archivo (ni del usuario ni encontrado), paramos.
    if not backup_to_restore:
        logger.error(f"❌ No se encontraron archivos de backup (.gz) en: {NOSQL_BACKUP_DIR_PATH.resolve()}")
        logger.warning("Ejecuta 'python manage.py nosql state backup' para crear uno primero.")
        raise typer.Exit(code=1)

    if not backup_to_restore.exists():
        logger.error(f"❌ El archivo de backup especificado no existe: {backup_to_restore.resolve()}")
        raise typer.Exit(code=1)

    logger.info(f"✅ Backup seleccionado para restaurar: {backup_to_restore.name}")

    typer.secho("¡ADVERTENCIA! ESTA OPERACIÓN ES REGENERATIVA - CONSTRUCTIVA.", fg=typer.colors.RED, bold=True)
    logger.warning(f"Se borrarán los datos actuales de la base de datos '{settings.MONGO_DB}' antes de restaurar.")
    confirmation = typer.prompt(f"Para confirmar, escribe el nombre de la base de datos MongoDB: '{settings.MONGO_DB}'")
    if confirmation != settings.MONGO_DB:
        logger.info("❌ La confirmación no coincide. Proceso cancelado.")
        raise typer.Exit()

    # La ruta DENTRO del contenedor.
    backup_path_container = f"/backups/{backup_to_restore.name}"

    command = [
        "docker", "exec", DOCKER_MONGO_CONTAINER_NAME,
        "mongorestore",
        f"--username={settings.MONGO_USER}",
        f"--password={settings.MONGO_PASSWORD}",
        "--authenticationDatabase=admin",
        f"--db={settings.MONGO_DB}",
        f"--archive={backup_path_container}",
        "--gzip",
        "--drop"  # Limpia la colección antes de restaurar
    ]

    try:
        subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', errors='replace')
        logger.success(f"✅ Restauración de MongoDB completada exitosamente desde: {backup_to_restore.name}")
        
        # --- CAMBIO CLAVE: Llamamos a la función de resumen ---
        asyncio.run(_show_restore_summary())        
    except subprocess.CalledProcessError as e:
        logger.error("❌ Error al ejecutar el comando mongorestore en Docker.")
        logger.error(f"Stderr: {e.stderr}")
    except Exception as e:
        logger.error(f"❌ Ocurrió un error inesperado durante la restauración de MongoDB: {e}")
# @app.command("restore")
# def restore_mongo_database(
#     # --- CAMBIO CLAVE: Hacemos el parámetro 'file' opcional (de ... a None) ---
#     file: Path = typer.Option(None, "--file", "-f", help="Ruta opcional al archivo de backup de MongoDB a restaurar.")
# ):
#     """
#     Restaura la BD MongoDB desde un backup ejecutando mongorestore.
#     Ejemplo de uso:
#         python mongo_state_manager.py restore --file backups/mongo_backups/backup_mibd_20240610_120000.gz    
#     """
#     configure_logging()
#     logger.info("🚀 Iniciando proceso de restauración de MongoDB vía Docker...")
#     logger.info(f"📁 Directorio local de backups: {NOSQL_BACKUP_DIR_PATH.resolve()}")
#     if not NOSQL_BACKUP_DIR_PATH.exists():
#         logger.warning("El directorio de backups no existe aún. Ejecuta el comando 'backup' primero o verifica la ruta.")
    
#     # --- CAMBIO CLAVE: Añadimos la lógica para buscar el último backup ---
#     if not file:
#         logger.info("No se especificó un archivo. Buscando el último backup de MongoDB...")
#         file = _find_latest_backup(NOSQL_BACKUP_DIR_PATH)    

#     if not file.exists():
#         logger.error(f"❌ No se encontró el archivo de backup: {file}")
#         raise typer.Exit(code=1)

#     typer.secho("¡ADVERTENCIA! ESTA OPERACIÓN ES REGENERATIVA - CONSTRUCTIVAS.", fg=typer.colors.RED, bold=True)
#     logger.warning(f"Se borrarán los datos actuales de la base de datos '{settings.MONGO_DB}' antes de restaurar.")
#     confirmation = typer.prompt(f"Para confirmar, escribe el nombre de la base de datos MongoDB: '{settings.MONGO_DB}'")
#     if confirmation != settings.MONGO_DB:
#         logger.info("❌ La confirmación no coincide. Proceso cancelado.")
#         raise typer.Exit()

#     # La ruta DENTRO del contenedor. La estandarizamos a /backups/
#     backup_path_container = f"/backups/{file.name}"

#     command = [
#         "docker", "exec", DOCKER_MONGO_CONTAINER_NAME,
#         "mongorestore",
#         f"--username={settings.MONGO_USER}",
#         f"--password={settings.MONGO_PASSWORD}",
#         "--authenticationDatabase=admin",
#         f"--db={settings.MONGO_DB}",
#         f"--archive={backup_path_container}",
#         "--gzip",
#         "--drop"
#     ]

#     try:
#         subprocess.run(command, capture_output=True, text=True, check=True)
#         logger.success(f"✅ Restauración de MongoDB completada exitosamente desde: {file.name}")
#     except subprocess.CalledProcessError as e:
#         logger.error("❌ Error al ejecutar el comando mongorestore en Docker.")
#         logger.error(f"Stderr: {e.stderr}")
#     except Exception as e:
#         logger.error(f"❌ Ocurrió un error inesperado durante la restauración de MongoDB: {e}")

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
    
    # TODO: verificar opciones para PROD con/sin docker, definir TB-HU 
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

@app.command("clear")
def clear_mongo_database():
    """
    Borra todos los documentos de todas las colecciones, pero MANTIENE la estructura
    (colecciones e índices). Es un "reseteo suave".
    """
    configure_logging()
    typer.secho("¡ADVERTENCIA! ESTÁS A PUNTO DE BORRAR TODOS LOS DOCUMENTOS DE LA BASE DE DATOS.", fg=typer.colors.YELLOW, bold=True)
    logger.warning(f"Esto afectará a la base de datos: '{settings.MONGO_DB}', pero no la eliminará.")
    confirmation = typer.prompt(f"Para confirmar esta operación, escribe el nombre de la base de datos: '{settings.MONGO_DB}'")
    
    if confirmation != settings.MONGO_DB:
        logger.info("❌ La confirmación no coincide. Proceso cancelado.")
        raise typer.Exit()

    # Script de JavaScript para limpiar todas las colecciones sin borrarlas
    clear_script = """
    var collections = db.getCollectionNames().filter(c => !c.startsWith('system.'));
    var totalDeleted = 0;
    collections.forEach(function(collName) {
      var result = db.getCollection(collName).deleteMany({});
      var count = result.deletedCount;
      totalDeleted += count;
      print('Limpiada colección: ' + collName + ' (' + count + ' documentos eliminados)');
    });
    print('Total de documentos eliminados: ' + totalDeleted);
    """
    
    command = [
        "docker", "exec", DOCKER_MONGO_CONTAINER_NAME,
        "mongo",
        settings.MONGO_DB,
        "-u", settings.MONGO_USER,
        "-p", settings.MONGO_PASSWORD,
        "--authenticationDatabase", "admin",
        "--eval", clear_script
    ]

    try:
        logger.info("🚀 Ejecutando limpieza de colecciones en MongoDB...")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8"
        )
        logger.success(f"✅ Todas las colecciones de '{settings.MONGO_DB}' han sido limpiadas exitosamente.")
        # Imprimimos la salida del script para ver el detalle
        if result.stdout:
            logger.info("--- Resumen de la operación ---")
            print(result.stdout.strip())
            
    except subprocess.CalledProcessError as e:
        logger.error("❌ Error al ejecutar el comando de limpieza en Docker.")
        logger.error(f"Stderr: {e.stderr}")
    except Exception as e:
        logger.error(f"❌ Ocurrió un error inesperado durante la limpieza de MongoDB: {e}")

@app.command("status")
def get_mongo_status():
    """
    Muestra un resumen de todos los modelos NoSQL definidos, sus colecciones
    y la cantidad de documentos en cada una.
    """
    configure_logging()
    asyncio.run(_get_nosql_status())

# --- NUEVO COMANDO 'CLEAR-BACKUPS' ---
@app.command("clear-backups")
def clear_mongo_backups():
    """
    Elimina TODOS los archivos de backup de MongoDB encontrados en el directorio de backups.
    """
    configure_logging()
    logger.info(f"🔍 Buscando backups de MongoDB en: {NOSQL_BACKUP_DIR_PATH.resolve()}")

    if not NOSQL_BACKUP_DIR_PATH.is_dir():
        logger.warning("El directorio de backups no existe. No hay nada que limpiar.")
        raise typer.Exit()

    # Buscamos todos los archivos .gz que son los backups
    backup_files = list(NOSQL_BACKUP_DIR_PATH.glob("*.gz"))

    if not backup_files:
        logger.info("✅ No se encontraron backups de MongoDB. El directorio ya está limpio.")
        raise typer.Exit()

    # Mostramos al usuario lo que se va a borrar
    typer.secho(f"\nSe encontraron {len(backup_files)} backups de MongoDB:", bold=True)
    for file in backup_files:
        typer.echo(f"  - {file.name}")

    typer.secho("\n¡ADVERTENCIA! Esta acción es irreversible.", fg=typer.colors.RED, bold=True)
    
    # Pedimos confirmación
    confirmed = typer.confirm(f"¿Estás seguro de que deseas eliminar permanentemente estos {len(backup_files)} archivos?")
    
    if not confirmed:
        logger.info("❌ Operación cancelada por el usuario.")
        raise typer.Exit()

    # Procedemos con la eliminación
    logger.info("🗑️ Eliminando archivos de backup...")
    deleted_count = 0
    try:
        for file in backup_files:
            file.unlink() # Elimina el archivo
            deleted_count += 1
        logger.success(f"✅ Se eliminaron exitosamente {deleted_count} archivos de backup.")
    except Exception as e:
        logger.error(f"❌ Ocurrió un error al eliminar los archivos: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()