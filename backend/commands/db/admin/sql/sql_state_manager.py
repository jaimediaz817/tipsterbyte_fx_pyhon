# filepath: c:\Users\JaimeIvanDiazGaona\Documents\proyectos_jdiaz\tipsterByte_fx\backend\scripts\db\state_manager.py
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import time
import typer
from sqlalchemy import create_engine, text
from loguru import logger

# --- CAMBIO CLAVE: Importar la ruta centralizada ---
from core.paths import PROJECT_ROOT, BACKEND_ROOT

# --- CAMBIO CLAVE: Añadir estas importaciones ---
from core.db.sql.admin.db_inspector import get_sql_db_status
from core.db.sql.base_class import Base
from core.db.sql.init_sql_all_models import load_all_models

# Añadir la raíz del proyecto al sys.path para que encuentre 'core'
project_root = Path(__file__).resolve().parents[4] # TODO: COMMENT: .parent.parent.parent
sys.path.append(str(project_root))

from core.config import settings
from core.logger import configure_logging









def _get_database_stats(engine):
    """Se conecta a la BD y recopila estadísticas clave."""
    stats = {"table_counts": {}, "total_size": "N/A"}
    try:
        with engine.connect() as connection:
            # Obtener tamaño total de la base de datos
            size_query = text("SELECT pg_size_pretty(pg_database_size(:db_name))")
            result = connection.execute(size_query, {"db_name": settings.POSTGRES_DB})
            stats["total_size"] = result.scalar_one()

            # Obtener conteo de filas para cada tabla definida en los modelos
            # Usamos los esquemas definidos en los modelos para ser precisos
            for table_name, table in Base.metadata.tables.items():
                schema = table.schema if table.schema else 'public'
                count_query = text(f'SELECT COUNT(*) FROM "{schema}"."{table.name}"')
                count = connection.execute(count_query).scalar_one()
                stats["table_counts"][table_name] = count
        return stats
    except Exception as e:
        logger.warning(f"⚠️ No se pudieron recopilar las estadísticas de la base de datos. Error: {e}")
        return stats


# Creamos una mini-app de Typer para este módulo.
# Esto nos permite tener subcomandos como 'backup', 'restore' y 'reset'.
# app = typer.Typer(help="Gestiona el estado de la base de datos (backups, restauraciones, reseteos).")
app = typer.Typer(help="Gestiona el estado de la base de datos SQL (PostgreSQL).")

# Constantes para PostgreSQL
DOCKER_POSTGRES_CONTAINER_NAME = "db_pg_tipsterbyte_fx"

# --- CAMBIO CLAVE: Definimos la nueva ruta del directorio de backups ---
# SQL_BACKUP_DIR_PATH = project_root / "backups" / "postgresql_backups"
# --- CAMBIO CLAVE: Usar la constante PROJECT_ROOT importada. CERO ".parent" ---
SQL_BACKUP_DIR_PATH = BACKEND_ROOT / "backups" / "postgresql_backups"

# --- CAMBIO CLAVE: Añadir nueva función helper ---
def _clear_all_tables():
    """
    Se conecta a la BD y borra TODAS las tablas conocidas por SQLAlchemy,
    y también la tabla 'alembic_version' para un reseteo completo.
    """
    logger.info("Cargando todos los modelos SQL para el borrado...")
    engine = create_engine(str(settings.DATABASE_URL))
    
    try:
        with engine.connect() as connection:
            trans = connection.begin()
            logger.warning("Procediendo a borrar todas las tablas de modelos...")
            Base.metadata.drop_all(bind=engine)
            
            # --- CAMBIO CLAVE Y DEFINITIVO ---
            # Borramos explícitamente la tabla de Alembic que drop_all() ignora.
            logger.warning("Borrando la tabla de historial de Alembic ('alembic_version')...")
            connection.execute(text("DROP TABLE IF EXISTS alembic_version;"))
            
            trans.commit()
            logger.success("✅ Todas las tablas, incluyendo el historial de Alembic, han sido borradas.")
    except Exception as e:
        logger.error(f"❌ Ocurrió un error al intentar borrar las tablas: {e}")
        if 'trans' in locals() and trans.is_active:
            trans.rollback()
        raise typer.Exit(code=1)
    finally:
        engine.dispose()
    
    # """
    # Se conecta a la BD y borra todas las tablas conocidas por SQLAlchemy.
    # """
    # # 1. Cargar todos los modelos para que Base.metadata los conozca
    # logger.info("Cargando todos los modelos SQL para el borrado...")
    
    # # 2. Conectarse a la base de datos
    # engine = create_engine(str(settings.DATABASE_URL))
    
    # try:
    #     with engine.connect() as connection:
    #         logger.warning("Procediendo a borrar todas las tablas...")
    #         # 3. Usar el método de SQLAlchemy para borrar todas las tablas
    #         Base.metadata.drop_all(bind=engine)
    #         logger.success("Todas las tablas han sido borradas.")
    # except Exception as e:
    #     logger.error(f"❌ Ocurrió un error al intentar borrar las tablas: {e}")
    #     raise typer.Exit(code=1)
    # finally:
    #     engine.dispose()

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

def _check_and_create_migrations():
    """Verifica si existen archivos de migración y crea una migración inicial si no hay ninguno."""
    versions_dir = Path(settings.ALEMBIC_VERSIONS_DIR)  # Asegúrate de que esta ruta esté definida en tu configuración
    logger.info(f"Ruta del directorio de migraciones (versions_dir): {versions_dir.resolve()}  existe={versions_dir.exists()}")
    if not versions_dir.is_dir() or not any(versions_dir.glob("*.py")):
        logger.warning("No se encontraron archivos de migración. Creando una migración inicial...")
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", "initial migration"], check=True)
        logger.success("Migración inicial creada exitosamente.")
    else:
        logger.info("Se encontraron archivos de migración existentes.")

# filepath: c:\Users\JaimeIvanDiazGaona\Documents\proyectos_jdiaz\tipsterByte_fx\backend\commands\db\admin\sql\sql_state_manager.py
def clear_migrations_files_only():
    """Función auxiliar que solo borra los archivos de migración sin pedir confirmación."""
    versions_dir = Path(settings.ALEMBIC_VERSIONS_DIR)
    if versions_dir.is_dir():
        for file in versions_dir.glob("*.py"):
            file.unlink()
        logger.trace("Archivos de migración borrados.")

# ... (resto de tus funciones) ...
@app.command("migrate")
def db_migrate(revision: str = typer.Argument("head", help="La revisión a la que se quiere migrar. 'head' para la última.")):
    """Aplica las migraciones de Alembic a la base de datos."""
    configure_logging()
    logger.info(f"🚀 Aplicando migraciones de Alembic hasta la revisión: '{revision}'...")
    try:
        subprocess.run(
            ["alembic", "upgrade", revision],
            check=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            # --- CAMBIO CLAVE: Añadir manejo de errores de codificación ---
            errors='replace'
        )
        logger.success("✅ Migraciones aplicadas exitosamente.")
    except subprocess.CalledProcessError as e:
        # Usamos un logging más detallado para futuros diagnósticos
        stderr_output = e.stderr.strip() if e.stderr else "No stderr output."
        logger.error(f"❌ Falló la aplicación de las migraciones.\nDetalles:\n{stderr_output}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"❌ Ocurrió un error inesperado durante la migración: {e}")
        raise typer.Exit(code=1)

@app.command("backup")
def backup_database(return_path: bool = typer.Option(False, hidden=True)) -> Path | None:
    """Crea un backup de la BD PostgreSQL con un resumen detallado."""
    configure_logging()
    load_all_models()
    logger.info("🚀 Iniciando proceso de backup de PostgreSQL...")
    
    # --- PASO 1: Recopilar estadísticas ANTES del backup ---
    logger.info("Recopilando estadísticas previas de la base de datos...")
    engine = create_engine(str(settings.DATABASE_URL))
    db_stats = _get_database_stats(engine)
    engine.dispose()

    # --- PASO 2: Preparar y ejecutar el backup ---
    SQL_BACKUP_DIR_PATH.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{settings.POSTGRES_DB}_{timestamp}.sqlc" # Usamos .sqlc para formato custom
    backup_file_path_host = SQL_BACKUP_DIR_PATH / backup_filename
    backup_file_path_container = f"/backups/{backup_filename}"

    command = [
        "docker", "exec",
        "-e", f"PGPASSWORD={settings.POSTGRES_PASSWORD}",
        DOCKER_POSTGRES_CONTAINER_NAME,
        "pg_dump", "--username", settings.POSTGRES_USER, "--dbname", settings.POSTGRES_DB,
        "--file", backup_file_path_container, "--format=c", "--verbose"
    ]

    try:
        start_time = time.monotonic()
        subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', errors='replace')
        end_time = time.monotonic()

        # --- PASO 3: Generar y mostrar el resumen detallado ---
        backup_size_bytes = os.path.getsize(backup_file_path_host)
        backup_size_mb = backup_size_bytes / (1024 * 1024)
        duration = end_time - start_time

        logger.success("✅ Backup completado exitosamente.")
        typer.echo("\n" + "="*60)
        typer.secho(" Resumen del Backup", fg=typer.colors.CYAN, bold=True)
        typer.echo("="*60)
        typer.echo(f" Archivo de Backup: {backup_file_path_host.name}")
        typer.echo(f" Ruta Completa:     {backup_file_path_host.resolve()}")
        typer.echo(f" Tamaño del Archivo: {backup_size_mb:.2f} MB")
        typer.echo(f" Duración:           {duration:.2f} segundos")
        typer.echo(f" Tamaño Total de BD: {db_stats['total_size']} (antes del backup)")
        typer.echo("\n--- Conteo de Registros por Tabla ---")
        
        if db_stats["table_counts"]:
            # Imprime una tabla bien formateada
            max_len = max(len(name) for name in db_stats["table_counts"].keys())
            for table, count in sorted(db_stats["table_counts"].items()):
                typer.echo(f"  {table:<{max_len}} : {count:>8,} registros")
        else:
            typer.echo("  No se encontraron tablas o no se pudo obtener el conteo.")
        
        typer.echo("="*60 + "\n")

        if return_path:
            return backup_file_path_host
    except subprocess.CalledProcessError as e:
        logger.error("❌ Error al ejecutar el comando de backup en Docker.")
        logger.error(f"Stderr: {e.stderr}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"❌ Ocurrió un error inesperado durante el backup: {e}")
        raise typer.Exit(code=1)

# def backup_database(return_path: bool = typer.Option(False, hidden=True)) -> Path | None:
#     """Crea un backup de la BD PostgreSQL ejecutando pg_dump DENTRO del contenedor."""
#     configure_logging()
#     load_all_models()
#     logger.info("🚀 Iniciando proceso de backup de PostgreSQL vía Docker...")
    
#     # --- CAMBIO CLAVE: Usamos la nueva ruta y nos aseguramos de que exista ---
#     SQL_BACKUP_DIR_PATH.mkdir(parents=True, exist_ok=True)
    
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     backup_filename = f"backup_{settings.POSTGRES_DB}_{timestamp}.sql"
#     backup_file_path_host = SQL_BACKUP_DIR_PATH / backup_filename
    
#     backup_file_path_container = f"/backups/{backup_filename}"

#     command = [
#         "docker", "exec",
#         "-e", f"PGPASSWORD={settings.POSTGRES_PASSWORD}",
#         DOCKER_POSTGRES_CONTAINER_NAME,
#         "pg_dump",
#         "--username", settings.POSTGRES_USER,
#         "--dbname", settings.POSTGRES_DB,
#         "--file", backup_file_path_container,
#         "--format", "c",
#         "--verbose"
#     ]

#     try:
#         # Ya no necesitamos pasar `env` porque lo incluimos en el comando docker
#         subprocess.run(command, capture_output=True, text=True, check=True)
#         logger.success(f"✅ Backup completado exitosamente. Archivo guardado en: {backup_file_path_host}")
#         if return_path:
#             return backup_file_path_host
#     except subprocess.CalledProcessError as e:
#         logger.error("❌ Error al ejecutar el comando de backup en Docker.")
#         logger.error(f"Stderr: {e.stderr}") # Stderr es muy útil para ver los errores de pg_dump
#         if return_path:
#             return None
#     except Exception as e:
#         logger.error(f"❌ Ocurrió un error inesperado durante el backup: {e}")
#         if return_path:
#             return None
        
@app.command("restore")
def restore_database(
    file: Path = typer.Option(None, "--file", "-f", help="Ruta opcional al archivo de backup a restaurar."),
    skip_confirmation: bool = typer.Option(False, hidden=True, help="Omitir la confirmación. Usar con precaución.")
):
    """Restaura la BD desde un backup ejecutando pg_restore DENTRO del contenedor."""
    configure_logging()
    load_all_models()

    if not skip_confirmation:
        logger.info("🚀 Iniciando proceso de restauración de PostgreSQL...")

    # --- LÓGICA DE VALIDACIÓN MEJORADA ---
    backup_to_restore = None
    if file:
        # Caso 1: El usuario especificó un archivo. Validamos que exista.
        logger.info(f"Intentando restaurar desde el archivo especificado: {file}")
        if not file.exists():
            logger.error(f"❌ El archivo de backup especificado no existe: {file.resolve()}")
            raise typer.Exit(code=1)
        backup_to_restore = file
    else:
        # Caso 2: No se especificó archivo. Buscamos el último backup disponible.
        logger.info("No se especificó un archivo. Buscando el último backup...")
        
        # Validamos que el directorio de backups exista y no esté vacío.
        if not SQL_BACKUP_DIR_PATH.exists() or not any(SQL_BACKUP_DIR_PATH.iterdir()):
            logger.error(f"❌ El directorio de backups está vacío o no existe: {SQL_BACKUP_DIR_PATH.resolve()}")
            logger.warning("Asegúrate de haber creado un backup primero con 'python manage.py sql state backup'.")
            raise typer.Exit(code=1)

        # Usamos la función helper para encontrar el archivo .sql más reciente.
        latest_backup = _find_latest_backup(SQL_BACKUP_DIR_PATH)
        if not latest_backup:
            logger.error(f"❌ No se encontraron archivos de backup (.sql) en: {SQL_BACKUP_DIR_PATH.resolve()}")
            logger.warning("Ejecuta 'python manage.py sql state backup' para crear uno primero.")
            raise typer.Exit(code=1)
        
        logger.info(f"✅ Backup más reciente encontrado: {latest_backup.name}")
        backup_to_restore = latest_backup

    # --- LÓGICA DE CONFIRMACIÓN DE SEGURIDAD ---
    if not skip_confirmation:
        typer.secho("¡ADVERTENCIA! Esta operación sobreescribirá la base de datos actual con el contenido del backup.", fg=typer.colors.YELLOW, bold=True)
        if not typer.confirm("¿Estás seguro de que deseas continuar?"):
            logger.info("Operación cancelada.")
            raise typer.Exit()

    logger.info(f"Procediendo a restaurar desde: {backup_to_restore.name}...")

    # --- LÓGICA DE EJECUCIÓN ---
    backup_file_path_container = f"/backups/{backup_to_restore.name}"

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
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', errors='replace')
        
        if result.stderr:
            logger.info(f"--- Salida de pg_restore (informativo) ---\n{result.stderr.strip()}")

        logger.success("✅ Restauración completada exitosamente.")
        logger.info("La base de datos ha sido restaurada al estado del backup.")
        logger.info("Puede que necesites ejecutar 'python manage.py sql migrate' si el backup no estaba totalmente al día.")

    except subprocess.CalledProcessError as e:
        logger.error("❌ Falló el proceso de restauración de la base de datos.")
        logger.error(f"Error de pg_restore:\n{e.stderr}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"❌ Ocurrió un error inesperado: {e}")
        raise typer.Exit(code=1)

@app.command("reset")
def reset_database(
    hard: bool = typer.Option(False, "--hard", help="MODO DESTRUCTIVO: Borra todo, recrea la BD y aplica migraciones. PIERDE TODOS LOS DATOS."),
    with_backup: bool = typer.Option(False, "--with-backup", help="MODO SEGURO: Hace backup, resetea y restaura los datos.")
):
    """Resetea la base de datos. Debes elegir un modo: --hard o --with-backup."""
    configure_logging()
    load_all_models()
    
    if not hard and not with_backup:
        logger.error("❌ Debes especificar un modo de reseteo. Usa --hard o --with-backup.")
        raise typer.Exit(code=1)

    if hard:
        logger.warning("Iniciando reseteo en MODO DESTRUCTIVO (--hard)...")
        
        # --- LÓGICA CORREGIDA ---
        # 1. PRIMERO, borra todas las tablas existentes.
        logger.info("Paso 1/3: Borrando todas las tablas de la base de datos...")
        _clear_all_tables()
        
        # 2. SEGUNDO, borra el historial de archivos de migración.
        logger.info("Paso 2/3: Limpiando el directorio de migraciones...")
        clear_migrations_files_only() # Usamos una función helper para no pedir confirmación de nuevo

        # 3. TERCERO, ahora que todo está limpio, crea la nueva migración inicial.
        logger.info("Paso 3/3: Creando nueva migración inicial desde los modelos actuales...")
        try:
            subprocess.run(
                ["alembic", "revision", "--autogenerate", "-m", "initial_migration_after_hard_reset"],
                check=True, capture_output=True
            )
            logger.success("✅ Nueva migración inicial creada.")
        except subprocess.CalledProcessError as e:
            logger.error("❌ Falló la creación de la migración inicial.")
            logger.error(f"Detalles: {e.stderr.decode('utf-8')}")
            raise typer.Exit(code=1)

        # 4. Finalmente, aplica la nueva migración.
        logger.info("Aplicando la nueva migración inicial a la base de datos...")
        # --- CAMBIO CLAVE: Pasar el argumento explícitamente ---
        db_migrate(revision="head")
        
        logger.success("🚀 Reseteo completo. La base de datos está limpia y sincronizada con los modelos actuales.")

    if with_backup:
        logger.info("Iniciando reseteo en MODO SEGURO (--with-backup)...")
        # (La lógica de with-backup no se ve afectada, pero la dejamos por completitud)
        backup_file = backup_database()
        if backup_file:
            reset_database(hard=True) # Llama a la lógica de reseteo duro
            restore_database(file=backup_file)

# --- CAMBIO CLAVE: Añadir el nuevo comando 'clear' ---
@app.command("clear-all-tables")
def clear_database():
    """
    Borra todas las tablas de la base de datos, pero NO la base de datos en sí.
    Es un "reseteo suave" ideal para limpiar datos antes de las pruebas.
    """
    configure_logging()
    load_all_models()
    
    typer.secho("¡ADVERTENCIA! ESTÁS A PUNTO DE BORRAR TODAS LAS TABLAS DE LA BASE DE DATOS.", fg=typer.colors.YELLOW, bold=True)
    logger.warning(f"Esto afectará a la base de datos: '{settings.POSTGRES_DB}', pero no la eliminará.")
    logger.warning("Esta operación es irreversible y todos los datos en las tablas se perderán.")
    
    confirmation = typer.prompt(f"Para confirmar esta operación, escribe el nombre de la base de datos: '{settings.POSTGRES_DB}'")
    if confirmation != settings.POSTGRES_DB:
        logger.info("❌ La confirmación no coincide. Proceso cancelado.")
        raise typer.Exit()

    logger.info("Confirmación aceptada. Procediendo a limpiar la base de datos...")
    _clear_all_tables()
    
    # --- CAMBIO CLAVE: Añadir guía para el siguiente paso ---
    logger.info("-" * 60)
    logger.info("PASO SIGUIENTE RECOMENDADO:")
    logger.info("La base de datos está ahora vacía. Para recrear la estructura de tablas, ejecuta:")
    typer.secho("    python manage.py sql migrate", fg=typer.colors.CYAN)
    logger.info("-" * 60)
    logger.success("✅ Proceso de limpieza de tablas completado exitosamente.")
    

# --- CAMBIO CLAVE: Añadir el nuevo comando 'clear-migrations' ---
@app.command("clear-migrations")
def clear_migrations():
    """
    [DESTRUCTIVO] Borra todos los archivos de migración de la carpeta 'alembic/versions'.
    
    Útil para empezar el historial de migraciones  desde cero. ¡ADVERTENCIA! Esto no
    afecta a la base de datos. Si la BD ya tiene migraciones aplicadas, quedará
    desincronizada. Usar junto con un reseteo de la base de datos.
    """
    configure_logging()
    load_all_models()
    
    versions_dir = Path(settings.ALEMBIC_VERSIONS_DIR)
    
    logger.warning("¡ADVERTENCIA MÁXIMA! ESTÁS A PUNTO DE BORRAR TODO EL HISTORIAL DE MIGRACIONES.")
    logger.warning(f"Se eliminarán todos los archivos de la carpeta: {versions_dir.resolve()}")
    logger.warning("Además, se borrarán todos los registros de la tabla 'alembic_version' en la base de datos.")
    
    confirmation = typer.prompt("Para confirmar esta operación, escribe la frase exacta: 'BORRAR MIGRACIONES'")
    if confirmation != "BORRAR MIGRACIONES":
        logger.info("Operación cancelada.")
        raise typer.Exit()

    logger.info("Confirmación aceptada. Procediendo...")

    # 1. Borrar archivos de migración
    try:
        if versions_dir.is_dir():
            # Usamos la función helper que ya teníamos
            clear_migrations_files_only()
            logger.success("✅ Archivos de migración borrados exitosamente.")
        else:
            logger.warning("El directorio de migraciones no existe. No hay archivos que borrar.")
    except Exception as e:
        logger.error(f"❌ Ocurrió un error al borrar los archivos: {e}")
        raise typer.Exit(code=1)

    # --- CAMBIO CLAVE Y DEFINITIVO: Usar SQL directo para vaciar la tabla ---
    # Esto es más robusto que 'alembic stamp base' porque no depende de los archivos.
    logger.info("Vaciando la tabla de historial 'alembic_version' en la base de datos...")
    engine = create_engine(str(settings.DATABASE_URL))
    try:
        with engine.connect() as connection:
            trans = connection.begin()
            # Usamos TRUNCATE que es más eficiente para borrar todas las filas.
            # También resetea secuencias si las hubiera.
            connection.execute(text("TRUNCATE TABLE alembic_version;"))
            trans.commit()
        logger.success("✅ La tabla 'alembic_version' ha sido vaciada.")
        logger.info("Ahora la base de datos no tiene un historial de migración asociado.")
    except Exception as e:
        # Manejamos el caso en que la tabla ni siquiera exista (p. ej. en una BD limpia)
        if "does not exist" in str(e).lower():
             logger.warning("⚠️  La tabla 'alembic_version' no existe en la base de datos. No hay nada que vaciar.")
        else:
            logger.error(f"❌ Falló el vaciado de la tabla 'alembic_version'. Error: {e}")
            if 'trans' in locals() and trans.is_active:
                trans.rollback()
            raise typer.Exit(code=1)
    finally:
        engine.dispose()

@app.command("clear-backups")
def clear_backups():
    """
    [DESTRUCTIVO] Elimina TODOS los archivos de backup de PostgreSQL (.sqlc y .sql).
    
    Busca, lista y luego elimina todos los archivos de backup encontrados.
    Esta operación es irreversible.
    """
    configure_logging()
    logger.info(f"🔍 Buscando backups en el directorio: {SQL_BACKUP_DIR_PATH.resolve()}")

    if not SQL_BACKUP_DIR_PATH.is_dir():
        logger.warning("⚠️  El directorio de backups no existe. No hay nada que borrar.")
        raise typer.Exit()

    # --- CAMBIO CLAVE: Buscar ambos tipos de extensiones ---
    # Creamos una lista combinando los resultados de dos búsquedas.
    backups_sqlc = list(SQL_BACKUP_DIR_PATH.glob("*.sqlc"))
    backups_sql = list(SQL_BACKUP_DIR_PATH.glob("*.sql"))
    backup_files = backups_sqlc + backups_sql

    if not backup_files:
        logger.success("✅ El directorio de backups está vacío. No hay archivos que borrar.")
        raise typer.Exit()

    # --- Listar los archivos ANTES de confirmar (sin cambios aquí) ---
    logger.info(f"Se encontraron {len(backup_files)} archivos de backup que serán eliminados:")
    
    typer.echo("-" * 60)
    for file in sorted(backup_files):
        typer.secho(f"  - {file.name}", fg=typer.colors.YELLOW)
    typer.echo("-" * 60)
    
    # --- Pedir la confirmación (sin cambios aquí) ---
    typer.secho("¡ADVERTENCIA! Esta operación es irreversible y borrará permanentemente los archivos listados.", fg=typer.colors.RED, bold=True)
    
    if not typer.confirm("¿Estás seguro de que deseas continuar?"):
        logger.info("❌ Operación cancelada por el usuario.")
        raise typer.Exit()

    # --- Proceder con la eliminación (sin cambios aquí) ---
    logger.info("Confirmación aceptada. Procediendo a eliminar los backups...")
    deleted_count = 0
    errors_count = 0
    for file in backup_files:
        try:
            file.unlink()
            logger.trace(f"Eliminado: {file.name}")
            deleted_count += 1
        except Exception as e:
            logger.error(f"No se pudo eliminar el archivo {file.name}. Error: {e}")
            errors_count += 1
    
    if errors_count > 0:
        logger.error(f"🚨 Proceso completado con {errors_count} errores.")
    
    logger.success(f"✅ Proceso finalizado. Se eliminaron {deleted_count} archivos de backup.")

@app.command("stats")
def stats():
    """Muestra estadísticas detalladas de la base de datos: tamaño y conteo de registros."""
    configure_logging()
    load_all_models()
    logger.info("📊 Recopilando estadísticas de la base de datos...")

    # --- PASO 1: Conectarse y obtener las estadísticas ---
    engine = create_engine(str(settings.DATABASE_URL))
    db_stats = _get_database_stats(engine)
    engine.dispose()

    # --- PASO 2: Presentar los resultados de forma clara ---
    if not db_stats["table_counts"] and db_stats["total_size"] == "N/A":
        logger.error("❌ No se pudieron obtener las estadísticas. Revisa la conexión a la base de datos.")
        raise typer.Exit(code=1)

    typer.echo("\n" + "="*60)
    typer.secho(" Resumen de la Base de Datos", fg=typer.colors.BLUE, bold=True)
    typer.echo("="*60)
    typer.echo(f" Base de Datos:    {settings.POSTGRES_DB}")
    typer.echo(f" Tamaño Total:     {db_stats['total_size']}")
    typer.echo("\n--- Conteo de Registros por Tabla ---")
    
    if db_stats["table_counts"]:
        # Imprime una tabla bien formateada, igual que en el backup
        max_len = max(len(name) for name in db_stats["table_counts"].keys()) if db_stats["table_counts"] else 0
        for table, count in sorted(db_stats["table_counts"].items()):
            typer.echo(f"  {table:<{max_len}} : {count:>8,} registros")
    else:
        typer.echo("  No se encontraron tablas o están vacías.")
    
    typer.echo("="*60 + "\n")

@app.command("status")
def db_status():
    """
    Muestra el estado de sincronización de los modelos y las migraciones,
    detectando problemas comunes como desincronizaciones.
    """
    configure_logging()
    logger.info("🔍 Verificando estado de la base de datos SQL...")

    # Parte 1: Compara modelos vs. tablas
    logger.info("--- Estado de Modelos vs. Tablas en la Base de Datos ---")
    status = get_sql_db_status()

    if status["synced"]:
        logger.success("✅ Modelos Sincronizados:")
        for table in status["synced"]: print(f"  - {table}")
    
    if status["code_only"]:
        logger.warning("\n⚠️  Modelos en código que FALTAN en la Base de Datos (necesitan migración):")
        for table in status["code_only"]: print(f"  - {table}")

    db_only_filtered = [t for t in status["db_only"] if t != 'alembic_version']
    if db_only_filtered:
        logger.info("ℹ️ Tablas en la Base de Datos que NO están en el código (posiblemente obsoletas):")
        for table in db_only_filtered: print(f"  - {table}")

    # Parte 2: Verifica el estado de Alembic de forma inteligente
    logger.info("\n--- Estado de Migraciones (Alembic) ---")
    try:
        # 1. Intentamos obtener la revisión actual. Capturamos la salida para analizarla.
        current_rev = subprocess.run(
            ["alembic", "current"], 
            capture_output=True, 
            text=True, 
            check=True,
            encoding='utf-8',
            errors='replace'
        ).stdout.strip()
        logger.info(f"\nRevisión actual en la base de datos: {current_rev or 'Ninguna (base)'}")
        # Imprimimos la salida estándar del comando si fue exitoso
        # print(current_process.stdout.strip())



        # 2. Si 'current' funcionó, ahora comprobamos si hay cambios pendientes.
        logger.info("\nComprobando si se necesita una nueva migración...")
        check_result = subprocess.run(
            ["alembic", "check"], 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if check_result.returncode == 0:
            logger.success("✅ ¡Sincronizado! No se necesita una nueva migración.")
        else:
            # --- CAMBIO CLAVE: Mostrar los detalles de los cambios ---
            logger.error("❌ ¡Se detectaron cambios en los modelos que no están en un archivo de migración!")
            
            # --- CAMBIO CLAVE: Usar el comando correcto para previsualizar cambios ---
            logger.info("Analizando los cambios SQL pendientes (preview)...")
            try:
                # Ejecutamos 'upgrade --sql head' para ver el SQL que se generaría.
                sql_preview_result = subprocess.run(
                    ["alembic", "upgrade", "head", "--sql"],
                    capture_output=True, text=True, check=True, encoding='utf-8', errors='replace'
                )
                # La salida de este comando es el SQL puro.
                detected_sql_changes = sql_preview_result.stdout
                
                logger.warning("\n--- Vista Previa de los Cambios SQL Pendientes ---")
                # Imprimimos el SQL detectado para que el usuario lo vea.
                print(detected_sql_changes)
                logger.warning("\n-------------------------------------------------")

            except subprocess.CalledProcessError as preview_error:
                logger.error("No se pudieron detallar los cambios. Error en la previsualización SQL.")
                logger.error(preview_error.stderr)

            logger.info("\n➡️  SOLUCIÓN: Ejecuta el siguiente comando para crear la migración:")
            typer.secho("    python manage.py sql create-migration \"tu mensaje\"", fg=typer.colors.CYAN, bold=True)



    except subprocess.CalledProcessError as e:
        # 3. Si CUALQUIER comando de Alembic falla, entramos aquí y analizamos el error.
        stderr_output = e.stderr.lower() # Convertimos a minúsculas para una búsqueda insensible
        
        if "can't locate revision" in stderr_output:
            # ¡Este es el error específico que queríamos detectar!
            logger.error("❌ DESINCRONIZACIÓN DETECTADA:")
            logger.warning("La base de datos apunta a una revisión de migración que ya no existe en la carpeta 'alembic/versions/'.")
            logger.warning("Esto suele ocurrir después de ejecutar 'clear-migrations'.")
            logger.info("➡️  Solución recomendada: Ejecuta 'python manage.py sql state reset --hard' para resincronizar todo.")
        else:
            # Si es otro error de Alembic, lo mostramos de forma genérica.
            logger.error(f"❌ Ocurrió un error inesperado al ejecutar Alembic.")
            logger.error(f"Detalles del error:\n{e.stderr}")

    except Exception as e:
        # Captura para cualquier otro tipo de error no relacionado con subprocess.
        logger.error(f"❌ Ocurrió un error general: {e}")
# def db_status():
#     """Muestra el estado de sincronización de los modelos y las migraciones."""
#     configure_logging()
#     logger.info("🔍 Verificando estado de la base de datos SQL...")

#     # Parte 1: Compara modelos vs. tablas
#     logger.info("--- Estado de Modelos vs. Tablas en la Base de Datos ---")
#     status = get_sql_db_status()

#     if status["synced"]:
#         logger.success("✅ Modelos Sincronizados:")
#         for table in status["synced"]: print(f"  - {table}")
    
#     if status["code_only"]:
#         logger.warning("⚠️  Modelos en código que FALTAN en la Base de Datos (necesitan migración):")
#         for table in status["code_only"]: print(f"  - {table}")

#     db_only_filtered = [t for t in status["db_only"] if t != 'alembic_version']
#     if db_only_filtered:
#         logger.info("ℹ️ Tablas en la Base de Datos que NO están en el código (posiblemente obsoletas):")
#         for table in db_only_filtered: print(f"  - {table}")

#     # Parte 2: Verifica el estado de Alembic
#     logger.info("\n--- Estado de Migraciones (Alembic) ---")
#     try:
#         logger.info("Revisión actual en la base de datos:")
#         subprocess.run(["alembic", "current"], check=True)
#         logger.info("\nComprobando si se necesita una nueva migración...")
#         check_result = subprocess.run(["alembic", "check"], capture_output=True, text=True)
#         if check_result.returncode == 0:
#             logger.success("✅ Los modelos y las migraciones están sincronizados.")
#         else:
#             logger.error("❌ ¡Se detectaron cambios en los modelos que no están en un archivo de migración!")
#             logger.warning("Ejecuta 'python manage.py sql create-migration \"tu mensaje\"' para crear la migración.")
#     except Exception as e:
#         logger.error(f"❌ Ocurrió un error al ejecutar Alembic: {e}")

if __name__ == "__main__":
    app()