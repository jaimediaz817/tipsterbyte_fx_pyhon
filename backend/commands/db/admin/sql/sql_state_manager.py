# ✅ SQL State Manager - Gestion de estado base de datos
# ✅ ARQUITECTURA LIMPIA: Este archivo solo actua como ORQUESTADOR
# ✅ TODA la logica de negocio se encuentra en la carpeta /services
# ✅ Ninguna logica de negocio aqui. Solo routers Typer y llamadas a servicios.

# ✅ PRIMERO: PROTECCION OBLIGATORIA ANTES DE TODO LO DEMAS
import os

if os.environ.get("PYTEST_VERSION") is not None:
    raise RuntimeError("⛔ NO USAR INFRAESTRUCTURA REAL EN TESTS UNITARIOS")

# ✅ AHORA SI, IMPORTAR EL RESTO
import sys
from pathlib import Path
import typer
from loguru import logger

from core.config import settings
from core.logger import configure_logging
from core.paths import BACKEND_ROOT

# ✅ Importamos TODOS los servicios desacoplados
from .services.backup_service import backup_database
from .services.restore_service import restore_database
from .services.migration_service import db_migrate
from .services.database_service import (
    clear_database,
    clear_migrations,
    _clear_all_tables,
)

# --- Constantes compartidas ---
SQL_BACKUP_DIR_PATH = BACKEND_ROOT / "backups" / "postgresql_backups"

# Creamos la app Typer principal
app = typer.Typer(help="Gestiona el estado de la base de datos SQL (PostgreSQL).")


# -----------------------------------------------------------------------------
# 🚀 COMANDOS PUBLICOS
# -----------------------------------------------------------------------------


@app.command("migrate")
def migrate(
    revision: str = typer.Argument(
        "head",
        help="La revisión a la que se quiere migrar. 'head' para la última. Ejemplo: 'abc123def456'",
    )
):
    """Aplica las migraciones de Alembic a la base de datos."""
    return db_migrate(revision)


@app.command("backup")
def backup(
    return_path: bool = typer.Option(False, hidden=True),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Modo silencioso, solo muestra errores y ruta final",
    ),
    no_stats: bool = typer.Option(
        False,
        "--no-stats",
        help="No recopilar estadisticas previas de la BD (mas rapido)",
    ),
    name: str = typer.Option(
        None, "--name", "-n", help="Nombre personalizado para el archivo de backup"
    ),
):
    """
    Crea un backup completo de la base de datos PostgreSQL.

    El backup se guarda automaticamente en formato comprimido (.sqlc) en la carpeta:
    backend/backups/postgresql_backups/
    """
    return backup_database(
        return_path=return_path, quiet=quiet, no_stats=no_stats, custom_name=name
    )


@app.command("restore")
def restore(
    file: Path = typer.Option(
        None,
        "--file",
        "-f",
        help="Ruta al archivo de backup a restaurar.",
    ),
    skip_confirmation: bool = typer.Option(
        False, hidden=True, help="Omitir la confirmación. Usar con precaución."
    ),
):
    """Restaura la BD desde un backup de PostgreSQL."""
    return restore_database(file=file, skip_confirmation=skip_confirmation)


@app.command("list")
def list_backups():
    """
    Lista todos los backups de PostgreSQL disponibles en el directorio de backups.
    Muestra nombre, fecha y tamaño de cada archivo ordenados por fecha (más reciente primero).
    """
    configure_logging()
    logger.info(
        f"🔍 Buscando backups en el directorio: {SQL_BACKUP_DIR_PATH.resolve()}"
    )

    if not SQL_BACKUP_DIR_PATH.is_dir():
        logger.warning("⚠️  El directorio de backups no existe.")
        typer.echo("💡 Para crear el primer backup ejecuta:")
        typer.secho("    python manage.py sql backup", fg=typer.colors.CYAN)
        raise typer.Exit()

    # Buscar ambos formatos de backup
    backups_sqlc = list(SQL_BACKUP_DIR_PATH.glob("*.sqlc"))
    backups_sql = list(SQL_BACKUP_DIR_PATH.glob("*.sql"))
    backup_files = backups_sqlc + backups_sql

    if not backup_files:
        logger.success("✅ El directorio de backups está vacío.")
        raise typer.Exit()

    # Ordenar por fecha de modificación (más reciente primero)
    backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    typer.echo("\n" + "=" * 80)
    typer.secho(" 📦 LISTADO DE BACKUPS DISPONIBLES", fg=typer.colors.CYAN, bold=True)
    typer.echo("=" * 80)

    total_size = 0
    for idx, backup_file in enumerate(backup_files, 1):
        stat = backup_file.stat()
        size_mb = stat.st_size / (1024 * 1024)
        total_size += stat.st_size

        from datetime import datetime

        fecha = datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S")

        typer.echo(f"  {idx:2d}. 📄 {backup_file.name}")
        typer.echo(f"       📅 Fecha: {fecha}")
        typer.echo(f"       📊 Tamaño: {size_mb:.2f} MB")
        typer.echo(f"       📍 Ruta: {backup_file.resolve()}")
        typer.echo("")

    typer.echo("=" * 80)
    logger.info(
        f"Total: {len(backup_files)} backups | Tamaño total: {total_size / (1024 * 1024):.2f} MB"
    )
    typer.echo("\n💡 Para restaurar un backup usa:")

    typer.secho("  ✅ FORMA CORRECTA (RECOMENDADA):", fg=typer.colors.GREEN)
    typer.secho(
        f"    python manage.py sql restore --file backups/postgresql_backups/{backup_files[0].name}",
        fg=typer.colors.CYAN,
    )
    typer.echo("")


@app.command("reset")
def reset_database(
    hard: bool = typer.Option(
        False,
        "--hard",
        help="MODO DESTRUCTIVO: Borra todo, recrea la BD y aplica migraciones. PIERDE TODOS LOS DATOS.",
    ),
    with_backup: bool = typer.Option(
        False,
        "--with-backup",
        help="MODO SEGURO: Hace backup, resetea y restaura los datos.",
    ),
):
    """Resetea la base de datos. Debes elegir un modo: --hard o --with-backup."""
    configure_logging()

    from core.db.sql.init_sql_all_models import load_all_models

    load_all_models()

    if not hard and not with_backup:
        logger.error(
            "❌ Debes especificar un modo de reseteo. Usa --hard o --with-backup."
        )
        raise typer.Exit(code=1)

    if hard:
        logger.warning("Iniciando reseteo en MODO DESTRUCTIVO (--hard)...")

        logger.info("Paso 1/3: Borrando todas las tablas de la base de datos...")
        _clear_all_tables()

        logger.info("Paso 2/3: Limpiando el directorio de migraciones...")
        from .services.migration_service import clear_migrations_files_only

        clear_migrations_files_only()

        logger.info(
            "Paso 3/3: Creando nueva migración inicial desde los modelos actuales..."
        )
        import subprocess
        import sys

        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "alembic",
                    "revision",
                    "--autogenerate",
                    "-m",
                    "initial_migration_after_hard_reset",
                ],
                check=True,
                capture_output=True,
            )
            logger.success("✅ Nueva migración inicial creada.")
        except subprocess.CalledProcessError as e:
            logger.error("❌ Falló la creación de la migración inicial.")
            raise typer.Exit(code=1)

        logger.info("Aplicando la nueva migración inicial a la base de datos...")
        db_migrate(revision="head")

        logger.success(
            "🚀 Reseteo completo. La base de datos está limpia y sincronizada con los modelos actuales."
        )

    if with_backup:
        logger.info("Iniciando reseteo en MODO SEGURO (--with-backup)...")
        backup_file = backup_database(return_path=True)
        if backup_file:
            reset_database(hard=True)
            restore_database(file=backup_file)


@app.command("clear-all-tables")
def clear_all_tables():
    """
    Borra todas las tablas de la base de datos, pero NO la base de datos en sí.
    Es un "reseteo suave" ideal para limpiar datos antes de las pruebas.
    """
    return clear_database()


@app.command("clear-migrations")
def clear_migrations_command():
    """
    [DESTRUCTIVO] Borra todos los archivos de migración de la carpeta 'alembic/versions'.
    """
    return clear_migrations()


@app.command("clear-backups")
def clear_backups():
    """
    [DESTRUCTIVO] Elimina TODOS los archivos de backup de PostgreSQL (.sqlc y .sql).
    """
    configure_logging()
    logger.info(
        f"🔍 Buscando backups en el directorio: {SQL_BACKUP_DIR_PATH.resolve()}"
    )

    if not SQL_BACKUP_DIR_PATH.is_dir():
        logger.warning("⚠️  El directorio de backups no existe. No hay nada que borrar.")
        raise typer.Exit()

    backups_sqlc = list(SQL_BACKUP_DIR_PATH.glob("*.sqlc"))
    backups_sql = list(SQL_BACKUP_DIR_PATH.glob("*.sql"))
    backup_files = backups_sqlc + backups_sql

    if not backup_files:
        logger.success(
            "✅ El directorio de backups está vacío. No hay archivos que borrar."
        )
        raise typer.Exit()

    logger.info(
        f"Se encontraron {len(backup_files)} archivos de backup que serán eliminados:"
    )

    typer.echo("-" * 60)
    for file in sorted(backup_files):
        typer.secho(f"  - {file.name}", fg=typer.colors.YELLOW)
    typer.echo("-" * 60)

    typer.secho(
        "¡ADVERTENCIA! Esta operación es irreversible y borrará permanentemente los archivos listados.",
        fg=typer.colors.RED,
        bold=True,
    )

    if not typer.confirm("¿Estás seguro de que deseas continuar?"):
        logger.info("❌ Operación cancelada por el usuario.")
        raise typer.Exit()

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

    logger.success(
        f"✅ Proceso finalizado. Se eliminaron {deleted_count} archivos de backup."
    )


@app.command("stats")
def stats():
    """Muestra estadísticas detalladas de la base de datos: tamaño y conteo de registros."""
    configure_logging()

    from core.db.sql.init_sql_all_models import load_all_models

    load_all_models()
    logger.info("📊 Recopilando estadísticas de la base de datos...")

    from .services.backup_service import _get_database_stats
    from sqlalchemy import create_engine

    engine = create_engine(str(settings.DATABASE_URL))
    db_stats = _get_database_stats(engine)
    engine.dispose()

    if not db_stats["table_counts"] and db_stats["total_size"] == "N/A":
        logger.error(
            "❌ No se pudieron obtener las estadísticas. Revisa la conexión a la base de datos."
        )
        raise typer.Exit(code=1)

    typer.echo("\n" + "=" * 60)
    typer.secho(" Resumen de la Base de Datos", fg=typer.colors.BLUE, bold=True)
    typer.echo("=" * 60)
    typer.echo(f" Base de Datos:    {settings.POSTGRES_DB}")
    typer.echo(f" Tamaño Total:     {db_stats['total_size']}")
    typer.echo("\n--- Conteo de Registros por Tabla ---")

    if db_stats["table_counts"]:
        max_len = (
            max(len(name) for name in db_stats["table_counts"].keys())
            if db_stats["table_counts"]
            else 0
        )
        for table, count in sorted(db_stats["table_counts"].items()):
            typer.echo(f"  {table:<{max_len}} : {count:>8,} registros")
    else:
        typer.echo("  No se encontraron tablas o están vacías.")

    typer.echo("=" * 60 + "\n")


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
    from core.db.sql.admin.db_inspector import get_sql_db_status

    status = get_sql_db_status()

    if status["synced"]:
        logger.success("✅ Modelos Sincronizados:")
        for table in status["synced"]:
            print(f"  - {table}")

    if status["code_only"]:
        logger.warning(
            "\n⚠️  Modelos en código que FALTAN en la Base de Datos (necesitan migración):"
        )
        for table in status["code_only"]:
            print(f"  - {table}")

    db_only_filtered = [t for t in status["db_only"] if t != "alembic_version"]
    if db_only_filtered:
        logger.info(
            "ℹ️ Tablas en la Base de Datos que NO están en el código (posiblemente obsoletas):"
        )
        for table in db_only_filtered:
            print(f"  - {table}")

    # Parte 2: Verifica el estado de Alembic
    logger.info("\n--- Estado de Migraciones (Alembic) ---")
    import subprocess
    import sys

    try:
        current_rev = subprocess.run(
            [sys.executable, "-m", "alembic", "current"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        ).stdout.strip()
        logger.info(
            f"\nRevisión actual en la base de datos: {current_rev or 'Ninguna (base)'}"
        )

        check_result = subprocess.run(
            [sys.executable, "-m", "alembic", "check"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if check_result.returncode == 0:
            logger.success("✅ ¡Sincronizado! No se necesita una nueva migración.")
        else:
            logger.error(
                "❌ ¡Se detectaron cambios en los modelos que no están en un archivo de migración!"
            )
            logger.info(
                "\n➡️  SOLUCIÓN: Ejecuta el siguiente comando para crear la migración:"
            )
            typer.secho(
                '    python manage.py sql create-migration "tu mensaje"',
                fg=typer.colors.CYAN,
                bold=True,
            )

    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr.lower()
        if "can't locate revision" in stderr_output:
            logger.error("❌ DESINCRONIZACIÓN DETECTADA:")
            logger.warning(
                "La base de datos apunta a una revisión de migración que ya no existe en la carpeta 'alembic/versions/'."
            )
            logger.info(
                "➡️  Solución recomendada: Ejecuta 'python manage.py sql state reset --hard' para resincronizar todo."
            )
        else:
            logger.error(f"❌ Ocurrió un error inesperado al ejecutar Alembic.")
    except Exception as e:
        logger.error(f"❌ Ocurrió un error general: {e}")


if __name__ == "__main__":
    app()
