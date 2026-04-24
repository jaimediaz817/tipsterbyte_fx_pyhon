# ✅ PRIMERO: PROTECCION OBLIGATORIA ANTES DE TODO LO DEMAS
import os

if os.environ.get("PYTEST_VERSION") is not None:
    raise RuntimeError("⛔ NO USAR INFRAESTRUCTURA REAL EN TESTS UNITARIOS")

import sys
import subprocess
from pathlib import Path
from loguru import logger
import typer

from core.config import settings
from core.logger import configure_logging


def _get_available_migrations() -> list[dict]:
    """Obtiene la lista de migraciones disponibles desde Alembic."""
    try:
        # Primero obtener la revisión actual
        current_revision = None
        try:
            current_result = subprocess.run(
                [sys.executable, "-m", "alembic", "current"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="replace",
            )
            if current_result.stdout.strip():
                current_line = current_result.stdout.strip()
                if current_line:
                    parts = current_line.split()
                    if parts:
                        current_revision = parts[0]
        except subprocess.CalledProcessError:
            pass

        # Obtener el historial de migraciones
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "history", "--verbose"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )

        migrations = []
        lines = result.stdout.strip().split("\n")

        current_rev = None
        current_msg = None

        for line in lines:
            line = line.strip()

            # Detectar líneas de revisión
            if line.startswith("Rev:"):
                if current_rev:
                    # Guardar la migración anterior
                    migrations.append(
                        {
                            "revision": current_rev,
                            "message": current_msg or "Sin mensaje",
                            "is_head": current_rev == current_revision,
                        }
                    )

                # Extraer nueva revisión
                parts = line.split()
                if len(parts) >= 2:
                    current_rev = parts[1]
                    # Verificar si tiene marcador (head)
                    if len(parts) >= 3 and parts[2] == "(head)":
                        current_msg = "HEAD - Migración más reciente"
                    else:
                        current_msg = None

            # Detectar líneas de mensaje/comentario
            elif (
                line.startswith("#")
                or line.startswith("Revises:")
                or line.startswith("Parent:")
            ):
                if line.startswith("#"):
                    # Extraer el mensaje del comentario
                    msg_content = line[1:].strip()
                    if msg_content and not msg_content.startswith("Create Date:"):
                        current_msg = msg_content

        # Agregar la última migración procesada
        if current_rev:
            migrations.append(
                {
                    "revision": current_rev,
                    "message": current_msg or "Sin mensaje",
                    "is_head": current_rev == current_revision,
                }
            )

        # Si no se encontraron migraciones, agregar la actual
        if not migrations and current_revision:
            migrations.append(
                {
                    "revision": current_revision,
                    "message": "Migración actual",
                    "is_head": True,
                }
            )

        return migrations

    except subprocess.CalledProcessError as e:
        logger.warning(f"No se pudo obtener el historial de migraciones: {e.stderr}")
        return []
    except Exception as e:
        logger.warning(f"Error inesperado al obtener migraciones: {e}")
        return []


def _check_and_create_migrations():
    """Verifica si existen archivos de migración y crea una migración inicial si no hay ninguno."""
    versions_dir = Path(settings.ALEMBIC_VERSIONS_DIR)
    logger.info(
        f"Ruta del directorio de migraciones (versions_dir): {versions_dir.resolve()}  existe={versions_dir.exists()}"
    )
    if not versions_dir.is_dir() or not any(versions_dir.glob("*.py")):
        logger.warning(
            "No se encontraron archivos de migración. Creando una migración inicial..."
        )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "alembic",
                "revision",
                "--autogenerate",
                "-m",
                "initial migration",
            ],
            check=True,
        )
        logger.success("Migración inicial creada exitosamente.")
    else:
        logger.info("Se encontraron archivos de migración existentes.")


def clear_migrations_files_only():
    """Función auxiliar que solo borra los archivos de migración sin pedir confirmación."""
    versions_dir = Path(settings.ALEMBIC_VERSIONS_DIR)
    if versions_dir.is_dir():
        for file in versions_dir.glob("*.py"):
            file.unlink()
        logger.trace("Archivos de migración borrados.")


def db_migrate(revision: str = "head"):
    """Aplica las migraciones de Alembic a la base de datos."""
    configure_logging()

    # Verificar que existen archivos de migración
    versions_dir = Path(settings.ALEMBIC_VERSIONS_DIR)
    if not versions_dir.exists() or not any(versions_dir.glob("*.py")):
        logger.warning("⚠️ No se encontraron archivos de migración.")
        typer.echo("")
        typer.secho(" 💡 SOLUCIÓN:", fg=typer.colors.GREEN, bold=True)
        typer.echo("-" * 70)
        typer.secho("  Crea una nueva migración con:", fg=typer.colors.WHITE)
        typer.secho(
            '    python manage.py sql create-migration "tu mensaje"',
            fg=typer.colors.CYAN,
        )
        typer.echo("-" * 70)
        return

    # Si se especifica "head" o no se especifica revisión, mostrar migraciones disponibles
    if revision == "head":
        logger.info(
            "No se especificó una revisión. Mostrando migraciones disponibles..."
        )

        # Obtener migraciones disponibles
        migrations = _get_available_migrations()

        if not migrations:
            logger.warning("⚠️ No se pudieron obtener las migraciones.")
            logger.info("Intentando aplicar todas las migraciones pendientes...")
        else:
            # Mostrar migraciones disponibles
            typer.echo("\n" + "=" * 70)
            typer.secho(" 🔄 MIGRACIONES DISPONIBLES", fg=typer.colors.CYAN, bold=True)
            typer.echo("=" * 70)

            for i, migration in enumerate(migrations[:10], 1):  # Mostrar máximo 10
                marker = " (HEAD)" if i == 1 else ""
                typer.echo(f"  {i:2d}. {migration['revision'][:12]}...{marker}")
                typer.echo(f"      {migration['message']}")

            typer.echo("=" * 70)

            # Mostrar ejemplos de uso
            typer.echo("")
            typer.secho(" 💡 EJEMPLOS DE USO:", fg=typer.colors.GREEN, bold=True)
            typer.echo("-" * 70)
            typer.secho(
                "  Para aplicar todas las migraciones pendientes:",
                fg=typer.colors.WHITE,
            )
            typer.secho("    python manage.py sql migrate head", fg=typer.colors.CYAN)
            typer.echo("")
            typer.secho(
                "  Para aplicar una migración específica:", fg=typer.colors.WHITE
            )
            if migrations:
                example_rev = (
                    migrations[0]["revision"][:12] if migrations else "abc123def456"
                )
                typer.secho(
                    f"    python manage.py sql migrate {example_rev}",
                    fg=typer.colors.CYAN,
                )
            typer.echo("")
            typer.secho(
                "  Para ver el estado actual de las migraciones:", fg=typer.colors.WHITE
            )
            typer.secho("    python manage.py sql status", fg=typer.colors.CYAN)
            typer.echo("-" * 70)
            typer.echo("")

            # Aplicar todas las migraciones (head)
            logger.info("Aplicando todas las migraciones pendientes...")

    logger.info(
        f"🚀 Aplicando migraciones de Alembic hasta la revisión: '{revision}'..."
    )
    try:
        # En Windows, usar shell=True para que encuentre el ejecutable correctamente
        import platform

        use_shell = platform.system() == "Windows"

        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", revision],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=use_shell,
        )
        logger.success("✅ Migraciones aplicadas exitosamente.")
        if result.stdout:
            typer.echo(result.stdout)
    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr.strip() if e.stderr else "No stderr output."
        logger.error(
            f"❌ Falló la aplicación de las migraciones.\nDetalles:\n{stderr_output}"
        )
        raise typer.Exit(code=1)
    except FileNotFoundError as e:
        logger.error(f"❌ No se encontró el ejecutable de Python o Alembic: {e}")
        logger.info("💡 Asegúrate de tener Python y Alembic instalados correctamente.")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"❌ Ocurrió un error inesperado durante la migración: {e}")
        raise typer.Exit(code=1)
