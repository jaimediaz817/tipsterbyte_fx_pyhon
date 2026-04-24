# ✅ PRIMERO: PROTECCION OBLIGATORIA ANTES DE TODO LO DEMAS
import os

if os.environ.get("PYTEST_VERSION") is not None:
    raise RuntimeError("⛔ NO USAR INFRAESTRUCTURA REAL EN TESTS UNITARIOS")

from pathlib import Path
import subprocess
from loguru import logger
import typer

from core.config import settings
from core.logger import configure_logging
from core.db.sql.init_sql_all_models import load_all_models

from .backup_service import DOCKER_POSTGRES_CONTAINER_NAME, SQL_BACKUP_DIR_PATH


def restore_database(file: Path | None = None, skip_confirmation: bool = False):
    """Restaura la BD desde un backup ejecutando pg_restore DENTRO del contenedor."""
    configure_logging()
    load_all_models()

    if not skip_confirmation:
        logger.info("🚀 Iniciando proceso de restauración de PostgreSQL...")

    backup_to_restore = None
    if file:
        logger.info(f"Intentando restaurar desde el archivo especificado: {file}")

        if not file.exists():
            if len(file.parts) == 1:
                potential_backup = SQL_BACKUP_DIR_PATH / file.name
                if potential_backup.exists():
                    logger.info(
                        f"✅ Archivo encontrado en el directorio de backups: {potential_backup}"
                    )
                    backup_to_restore = potential_backup
                else:
                    logger.error(
                        f"❌ El archivo de backup especificado no existe: {file.resolve()}"
                    )
                    logger.info(f"💡 Buscado también en: {potential_backup.resolve()}")
                    raise typer.Exit(code=1)
            else:
                logger.error(
                    f"❌ El archivo de backup especificado no existe: {file.resolve()}"
                )
                raise typer.Exit(code=1)
        else:
            backup_to_restore = file
    else:
        logger.info("No se especificó un archivo. Mostrando backups disponibles...")

        if not SQL_BACKUP_DIR_PATH.exists() or not any(SQL_BACKUP_DIR_PATH.iterdir()):
            logger.error(
                f"❌ El directorio de backups está vacío o no existe: {SQL_BACKUP_DIR_PATH.resolve()}"
            )
            logger.warning(
                "Asegúrate de haber creado un backup primero con 'python manage.py sql state backup'."
            )
            raise typer.Exit(code=1)

        backups_sqlc = list(SQL_BACKUP_DIR_PATH.glob("*.sqlc"))
        backups_sql = list(SQL_BACKUP_DIR_PATH.glob("*.sql"))
        backup_files = sorted(
            backups_sqlc + backups_sql, key=lambda f: f.stat().st_mtime, reverse=True
        )

        if not backup_files:
            logger.error(
                f"❌ No se encontraron archivos de backup (.sql o .sqlc) en: {SQL_BACKUP_DIR_PATH.resolve()}"
            )
            logger.warning(
                "Ejecuta 'python manage.py sql state backup' para crear uno primero."
            )
            raise typer.Exit(code=1)

        typer.echo("\n" + "=" * 70)
        typer.secho(" 📦 BACKUPS DISPONIBLES", fg=typer.colors.CYAN, bold=True)
        typer.echo("=" * 70)

        for i, backup in enumerate(backup_files[:10], 1):
            backup_size = backup.stat().st_size / (1024 * 1024)
            mod_time = Path(backup).stat().st_mtime
            from datetime import datetime

            mod_time_str = datetime.fromtimestamp(mod_time).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            marker = " (más reciente)" if i == 1 else ""
            typer.echo(f"  {i:2d}. {backup.name}")
            typer.echo(
                f"      Tamaño: {backup_size:.2f} MB | Fecha: {mod_time_str}{marker}"
            )

        typer.echo("=" * 70)

        typer.echo("")
        typer.secho(" 💡 EJEMPLOS DE USO:", fg=typer.colors.GREEN, bold=True)
        typer.echo("-" * 70)
        typer.secho("  Para restaurar el backup más reciente:", fg=typer.colors.WHITE)
        typer.secho("    python manage.py sql state restore", fg=typer.colors.CYAN)
        typer.echo("")
        typer.secho(
            "  Para restaurar un backup específico por nombre:", fg=typer.colors.WHITE
        )
        latest_example = (
            backup_files[0].name
            if backup_files
            else "backup_tipsterbyte_fx_db_20260323_195912.sqlc"
        )
        typer.secho(
            f'    python manage.py sql state restore --file "{latest_example}"',
            fg=typer.colors.CYAN,
        )
        typer.echo("")
        typer.secho("  Para restaurar usando la ruta completa:", fg=typer.colors.WHITE)
        typer.secho(
            f'    python manage.py sql state restore --file "{SQL_BACKUP_DIR_PATH / latest_example}"',
            fg=typer.colors.CYAN,
        )
        typer.echo("-" * 70)
        typer.echo("")

        latest_backup = backup_files[0]
        logger.info(f"✅ Se usará el backup más reciente: {latest_backup.name}")
        backup_to_restore = latest_backup

    if not skip_confirmation:
        typer.secho(
            "¡ADVERTENCIA! Esta operación sobreescribirá la base de datos actual con el contenido del backup.",
            fg=typer.colors.YELLOW,
            bold=True,
        )
        if not typer.confirm("¿Estás seguro de que deseas continuar?"):
            logger.info("Operación cancelada.")
            raise typer.Exit()

    logger.info(f"Procediendo a restaurar desde: {backup_to_restore.name}...")

    backup_file_path_container = f"/backups/{backup_to_restore.name}"

    command = [
        "docker",
        "exec",
        "-e",
        f"PGPASSWORD={settings.POSTGRES_PASSWORD}",
        DOCKER_POSTGRES_CONTAINER_NAME,
        "pg_restore",
        "--username",
        settings.POSTGRES_USER,
        "--dbname",
        settings.POSTGRES_DB,
        "--clean",
        "--if-exists",
        "--verbose",
        backup_file_path_container,
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )

        if result.stderr:
            logger.info(
                f"--- Salida de pg_restore (informativo) ---\n{result.stderr.strip()}"
            )

        logger.success("✅ Restauración completada exitosamente.")
        logger.info("La base de datos ha sido restaurada al estado del backup.")
        logger.info(
            "Puede que necesites ejecutar 'python manage.py sql migrate' si el backup no estaba totalmente al día."
        )

    except subprocess.CalledProcessError as e:
        logger.error("❌ Falló el proceso de restauración de la base de datos.")
        logger.error(f"Error de pg_restore:\n{e.stderr}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"❌ Ocurrió un error inesperado: {e}")
        raise typer.Exit(code=1)
