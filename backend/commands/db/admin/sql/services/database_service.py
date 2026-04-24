# ✅ PRIMERO: PROTECCION OBLIGATORIA ANTES DE TODO LO DEMAS
import os

if os.environ.get("PYTEST_VERSION") is not None:
    raise RuntimeError("⛔ NO USAR INFRAESTRUCTURA REAL EN TESTS UNITARIOS")

from pathlib import Path
from sqlalchemy import create_engine, text
from loguru import logger
import typer

from core.config import settings
from core.logger import configure_logging
from core.db.sql.base_class import Base
from core.db.sql.init_sql_all_models import load_all_models


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

            logger.warning(
                "Borrando la tabla de historial de Alembic ('alembic_version')..."
            )
            connection.execute(text("DROP TABLE IF EXISTS alembic_version;"))

            trans.commit()
            logger.success(
                "✅ Todas las tablas, incluyendo el historial de Alembic, han sido borradas."
            )
    except Exception as e:
        logger.error(f"❌ Ocurrió un error al intentar borrar las tablas: {e}")
        if "trans" in locals() and trans.is_active:
            trans.rollback()
        raise typer.Exit(code=1)
    finally:
        engine.dispose()


def _drop_and_create_db():
    """Función helper para conectarse al servidor de BD y recrear la base de datos."""
    # Nos conectamos a una BD de mantenimiento (como 'postgres') para poder operar sobre nuestra BD
    server_url = str(settings.DATABASE_URL).replace(
        f"/{settings.POSTGRES_DB}", "/postgres"
    )
    engine = create_engine(server_url, isolation_level="AUTOCOMMIT")

    try:
        with engine.connect() as connection:
            logger.warning(
                f"Intentando borrar la base de datos '{settings.POSTGRES_DB}'..."
            )
            # Usamos FORCE para desconectar a otros usuarios que puedan estar conectados
            connection.execute(
                text(f'DROP DATABASE IF EXISTS "{settings.POSTGRES_DB}" WITH (FORCE)')
            )
            logger.info("Base de datos borrada.")

            logger.info(
                f"Intentando crear la base de datos '{settings.POSTGRES_DB}'..."
            )
            connection.execute(text(f'CREATE DATABASE "{settings.POSTGRES_DB}"'))
            logger.info("Base de datos creada.")
    except Exception as e:
        logger.error(
            f"❌ Ocurrió un error al intentar borrar/crear la base de datos: {e}"
        )
        raise typer.Exit(code=1)
    finally:
        engine.dispose()


def clear_database():
    """
    Borra todas las tablas de la base de datos, pero NO la base de datos en sí.
    Es un "reseteo suave" ideal para limpiar datos antes de las pruebas.
    """
    configure_logging()
    load_all_models()

    typer.secho(
        "¡ADVERTENCIA! ESTÁS A PUNTO DE BORRAR TODAS LAS TABLAS DE LA BASE DE DATOS.",
        fg=typer.colors.YELLOW,
        bold=True,
    )
    typer.secho(
        f"Esto afectará a la base de datos: '{settings.POSTGRES_DB}', pero no la eliminará.",
        fg=typer.colors.YELLOW,
    )
    typer.secho(
        "Esta operación es irreversible y todos los datos en las tablas se perderán.",
        fg=typer.colors.YELLOW,
    )

    confirmation = typer.prompt(
        f"Para confirmar esta operación, escribe el nombre de la base de datos: '{settings.POSTGRES_DB}'"
    )
    if confirmation != settings.POSTGRES_DB:
        logger.info("❌ La confirmación no coincide. Proceso cancelado.")
        raise typer.Exit()

    logger.info("Confirmación aceptada. Procediendo a limpiar la base de datos...")
    _clear_all_tables()

    logger.info("-" * 60)
    logger.info("PASO SIGUIENTE RECOMENDADO:")
    logger.info(
        "La base de datos está ahora vacía. Para recrear la estructura de tablas, ejecuta:"
    )
    typer.secho("    python manage.py sql migrate", fg=typer.colors.CYAN)
    logger.info("-" * 60)
    logger.success("✅ Proceso de limpieza de tablas completado exitosamente.")


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

    logger.warning(
        "¡ADVERTENCIA MÁXIMA! ESTÁS A PUNTO DE BORRAR TODO EL HISTORIAL DE MIGRACIONES."
    )
    logger.warning(
        f"Se eliminarán todos los archivos de la carpeta: {versions_dir.resolve()}"
    )
    logger.warning(
        "Además, se borrarán todos los registros de la tabla 'alembic_version' en la base de datos."
    )

    typer.echo("")
    typer.echo("=" * 70)
    typer.secho("⚠️  CONFIRMACIÓN REQUERIDA", fg=typer.colors.RED, bold=True)
    typer.echo("=" * 70)
    typer.secho(
        "Para confirmar esta operación, escribe la frase exacta: 'BORRAR_MIGRACIONES'",
        fg=typer.colors.YELLOW,
    )
    confirmation = input("Escribe aquí: ")

    if confirmation != "BORRAR_MIGRACIONES":
        logger.info("Operación cancelada.")
        raise typer.Exit()

    logger.info("Confirmación aceptada. Procediendo...")

    # 1. Borrar archivos de migración
    try:
        if versions_dir.is_dir():
            from .migration_service import clear_migrations_files_only

            clear_migrations_files_only()
            logger.success("✅ Archivos de migración borrados exitosamente.")
        else:
            logger.warning(
                "El directorio de migraciones no existe. No hay archivos que borrar."
            )
    except Exception as e:
        logger.error(f"❌ Ocurrió un error al borrar los archivos: {e}")
        raise typer.Exit(code=1)

    logger.info(
        "Vaciando la tabla de historial 'alembic_version' en la base de datos..."
    )
    engine = create_engine(str(settings.DATABASE_URL))
    try:
        with engine.connect() as connection:
            trans = connection.begin()
            connection.execute(text("TRUNCATE TABLE alembic_version;"))
            trans.commit()
        logger.success("✅ La tabla 'alembic_version' ha sido vaciada.")
        logger.info(
            "Ahora la base de datos no tiene un historial de migración asociado."
        )
    except Exception as e:
        if "does not exist" in str(e).lower():
            logger.warning(
                "⚠️  La tabla 'alembic_version' no existe en la base de datos. No hay nada que vaciar."
            )
        else:
            logger.error(
                f"❌ Falló el vaciado de la tabla 'alembic_version'. Error: {e}"
            )
            if "trans" in locals() and trans.is_active:
                trans.rollback()
            raise typer.Exit(code=1)
    finally:
        engine.dispose()
