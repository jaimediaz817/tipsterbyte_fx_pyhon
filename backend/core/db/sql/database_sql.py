# ✅ ✅ ✅ PROTECCION GLOBAL PRIMERO, ANTES DE TODO!
# Esta es la correccion que soluciona TODO el problema de lentitud en tests
import os

if os.environ.get("PYTEST_VERSION") is not None:
    # 🚀 SI ESTAMOS EN TESTS: NO CARGAMOS NADA DE NADA!
    # NO HACEMOS NINGUN OTRO IMPORT! NI MODULOS, NI NADA!
    raise RuntimeError(
        """⛔ INTENTO DE CONEXION A BD REAL EN TESTS! Usa Mocks. Esta proteccion se ejecuta ANTES de cargar cualquier modulo."""
    )

# AHORA SI, CARGAMOS EL RESTO SOLAMENTE SI NO ESTAMOS EN TESTS
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from loguru import logger

try:
    from core.db.sql.init_sql_all_models import load_all_models
except ImportError:
    # Modulo no existe, no hacemos nada, solo para backwards compatibility
    load_all_models = lambda: None

from core.config import settings

# Importa la Base fundamental
from core.db.sql.base_class import Base

# ✅ Cargar todos los modelos SQL antes de crear engine/sesiones
load_all_models()

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()

    finally:
        db.close()


def verify_database_connection() -> bool:
    """
    Verifica que la base de datos PostgreSQL esté disponible.

    Returns:
        bool: True si la conexión es exitosa, False en caso contrario.
    """
    from sqlalchemy import text

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Conexión a PostgreSQL verificada correctamente.")
        return True
    except Exception as e:
        logger.error(f"❌ BD no disponible: {e}")
        return False


def run_startup_migrations() -> bool:
    """
    Ejecuta migraciones de Alembic al iniciar la aplicación.

    Reutiliza la lógica de 'manage.py sql migrate' para aplicar
    migraciones pendientes automáticamente al iniciar el servidor.

    Returns:
        bool: True si las migraciones se aplicaron exitosamente, False en caso contrario.
    """
    import subprocess
    import platform

    use_shell = platform.system() == "Windows"

    try:
        logger.info("🔄 Verificando migraciones pendientes de Alembic...")

        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
            shell=use_shell,
        )

        output = result.stdout + result.stderr
        if output.strip():
            lines = output.strip().split("\n")
            applied_count = 0
            for line in lines:
                if "Running upgrade" in line or "->" in line:
                    applied_count += 1
                    logger.info(f"  📋 {line.strip()}")
            if applied_count > 0:
                logger.success(
                    f"✅ {applied_count} migración(es) aplicada(s) exitosamente."
                )
            else:
                logger.info("✅ No hay migraciones pendientes. Esquema actualizado.")
        else:
            logger.info("✅ No hay migraciones pendientes. Esquema actualizado.")

        return True

    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr.strip() if e.stderr else "No stderr output."

        # Detectar error de tablas duplicadas
        if "already exists" in stderr_output.lower():
            logger.warning("⚠️ Las tablas ya existen en la BD.")
            logger.info("➡️ Marcando migración como aplicada...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "alembic", "stamp", "head"],
                    check=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    shell=use_shell,
                )
                logger.success("✅ Migración marcada como aplicada.")
                return True
            except Exception as stamp_error:
                logger.error(f"❌ No se pudo marcar la migración: {stamp_error}")
                return False
        else:
            logger.error(f"❌ Error en migraciones: {stderr_output}")
            return False

    except Exception as e:
        logger.error(f"❌ Error inesperado en migraciones: {e}")
        return False


def create_db_and_tables():
    """
    [DEPRECATED] Crea todas las tablas en la base de datos.

    ⚠️ DEPRECATED: Este método será eliminado en futuras versiones.
    Use 'run_startup_migrations()' en su lugar, que ejecuta migraciones
    de Alembic y maneja correctamente los cambios de esquema.

    Razón de deprecación:
    - create_all() no maneja cambios de esquema correctamente
    - No aplica migraciones pendientes
    - Puede causar inconsistencias en producción

    Alternativa recomendada:
        from core.db.sql.database_sql import run_startup_migrations
        run_startup_migrations()

    Timeline de eliminación:
    - v1.1.0: Deprecated (advertencia)
    - v2.0.0: Eliminado completamente
    """
    import warnings

    warnings.warn(
        "create_db_and_tables() está deprecado. "
        "Use run_startup_migrations() en su lugar para manejo correcto de migraciones.",
        DeprecationWarning,
        stacklevel=2,
    )

    logger.warning(
        "⚠️ DEPRECATED: create_db_and_tables() será eliminado. "
        "Use run_startup_migrations() en su lugar."
    )

    Base.metadata.create_all(bind=engine)
