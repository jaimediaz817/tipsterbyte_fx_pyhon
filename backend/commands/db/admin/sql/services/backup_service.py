# ✅ PRIMERO: PROTECCION OBLIGATORIA ANTES DE TODO LO DEMAS
import os

if os.environ.get("PYTEST_VERSION") is not None:
    raise RuntimeError("⛔ NO USAR INFRAESTRUCTURA REAL EN TESTS UNITARIOS")

from pathlib import Path
from datetime import datetime
import subprocess
import time
from sqlalchemy import create_engine, text
from loguru import logger

from core.config import settings
from core.logger import configure_logging
from core.db.sql.init_sql_all_models import load_all_models


# Constantes locales al servicio
from core.paths import BACKEND_ROOT

DOCKER_POSTGRES_CONTAINER_NAME = settings.POSTGRES_CONTAINER_NAME
SQL_BACKUP_DIR_PATH = BACKEND_ROOT / "backups" / "postgresql_backups"


def _get_database_stats(engine):
    """Se conecta a la BD y recopila estadísticas clave."""
    stats = {"table_counts": {}, "total_size": "N/A"}
    try:
        with engine.connect() as connection:
            size_query = text("SELECT pg_size_pretty(pg_database_size(:db_name))")
            result = connection.execute(size_query, {"db_name": settings.POSTGRES_DB})
            stats["total_size"] = result.scalar_one()

            from core.db.sql.base_class import Base

            for table_name, table in Base.metadata.tables.items():
                schema = table.schema if table.schema else "public"
                count_query = text(f'SELECT COUNT(*) FROM "{schema}"."{table.name}"')
                count = connection.execute(count_query).scalar_one()
                stats["table_counts"][table_name] = count
        return stats
    except Exception as e:
        logger.warning(f"⚠️ No se pudieron recopilar las estadísticas: {e}")
        return stats


def backup_database(
    return_path: bool = False,
    quiet: bool = False,
    no_stats: bool = False,
    custom_name: str | None = None,
) -> Path | None:
    """Crea un backup de la BD PostgreSQL con un resumen detallado."""
    configure_logging()
    load_all_models()

    if not quiet:
        logger.info("🚀 Iniciando proceso de backup de PostgreSQL...")

    if not no_stats and not quiet:
        logger.info("Recopilando estadísticas previas de la base de datos...")
        engine = create_engine(str(settings.DATABASE_URL))
        db_stats = _get_database_stats(engine)
        engine.dispose()

    SQL_BACKUP_DIR_PATH.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if custom_name:
        backup_filename = f"{custom_name}_{timestamp}.sqlc"
    else:
        backup_filename = f"backup_{settings.POSTGRES_DB}_{timestamp}.sqlc"

    backup_file_path_host = SQL_BACKUP_DIR_PATH / backup_filename
    backup_file_path_container = f"/backups/{backup_filename}"

    try:
        start_time = time.monotonic()

        # ✅ PASO 0: Crear el directorio /backups DENTRO del contenedor primero
        mkdir_command = [
            "docker",
            "exec",
            DOCKER_POSTGRES_CONTAINER_NAME,
            "mkdir",
            "-p",
            "/backups",
        ]
        subprocess.run(mkdir_command, capture_output=True, text=True, check=True)

        # ✅ PASO 1: Ejecutar pg_dump
        command = [
            "docker",
            "exec",
            "-e",
            f"PGPASSWORD={settings.POSTGRES_PASSWORD}",
            DOCKER_POSTGRES_CONTAINER_NAME,
            "pg_dump",
            "--username",
            settings.POSTGRES_USER,
            "--dbname",
            settings.POSTGRES_DB,
            "--file",
            backup_file_path_container,
            "--format=c",
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )

        # ✅ PASO 2: Verificar que el archivo SI existe en el contenedor
        check_command = [
            "docker",
            "exec",
            DOCKER_POSTGRES_CONTAINER_NAME,
            "ls",
            "-la",
            backup_file_path_container,
        ]
        check_result = subprocess.run(check_command, capture_output=True, text=True)
        if check_result.returncode != 0:
            raise RuntimeError(
                f"El backup NO se creo dentro del contenedor. Error pg_dump: {result.stderr}"
            )

        # ✅ PASO 3: Copiar el backup desde el contenedor al host
        copy_command = [
            "docker",
            "cp",
            f"{DOCKER_POSTGRES_CONTAINER_NAME}:{backup_file_path_container}",
            str(backup_file_path_host),
        ]
        subprocess.run(copy_command, check=True, capture_output=True, text=True)

        # ✅ PASO 4: Verificar que el archivo llego correctamente al host
        if not backup_file_path_host.exists():
            raise RuntimeError("El backup no se copio correctamente al host")

        # ✅ PASO 5: Borrar el archivo del contenedor para no dejar basura
        clean_command = [
            "docker",
            "exec",
            DOCKER_POSTGRES_CONTAINER_NAME,
            "rm",
            "-f",
            backup_file_path_container,
        ]
        subprocess.run(clean_command, capture_output=True, text=True)

        end_time = time.monotonic()

        backup_size_bytes = os.path.getsize(backup_file_path_host)
        backup_size_mb = backup_size_bytes / (1024 * 1024)
        duration = end_time - start_time

        logger.success("✅ Backup completado exitosamente.")
        logger.success(f"📄 Archivo guardado: {backup_file_path_host}")
        logger.info(f"📊 Tamaño: {backup_size_mb:.2f} MB")
        logger.info(f"⏱️  Duración: {duration:.2f} segundos")

        if return_path:
            return backup_file_path_host

    except Exception as e:
        logger.error(f"❌ Error durante el backup: {e}")
        raise
