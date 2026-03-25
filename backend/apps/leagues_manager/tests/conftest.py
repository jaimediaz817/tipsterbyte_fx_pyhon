"""
Fixture de pytest para tests unitarios.
- Deshabilita logging en BD automáticamente (NoOpProcessRunRepository)
- Limpia tablas de process_run/process_run_log después de tests de integración
"""

import sys
import os
from pathlib import Path

# --- INICIO: Configuración para asegurar que pytest encuentre los módulos ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# Subimos tres niveles desde 'tests' para llegar a 'backend'
# tests -> leagues_manager -> apps -> backend
backend_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)
# --- FIN: Configuración para asegurar que pytest encuentre los módulos ---

import pytest
from core.db.sql.database_sql import SessionLocal
from apps.platform_config.infrastructure.models.sql.process_run import ProcessRun
from apps.platform_config.infrastructure.models.sql.process_run_log import ProcessRunLog
from shared.repositories.scheduler_repos import (
    NoOpProcessRunRepository,
    ProcessRunRepositoryFactory,
)


@pytest.fixture(autouse=True)
def disable_process_run_logging():
    """
    Fixture que deshabilita automáticamente el logging en BD para TODOS los tests.
    Los tests unitarios usarán NoOpProcessRunRepository automáticamente.
    """
    original_value = os.environ.get("PROCESS_RUN_LOGGING_ENABLED")
    os.environ["PROCESS_RUN_LOGGING_ENABLED"] = "false"
    yield
    # Restaurar valor original después del test
    if original_value is None:
        os.environ.pop("PROCESS_RUN_LOGGING_ENABLED", None)
    else:
        os.environ["PROCESS_RUN_LOGGING_ENABLED"] = original_value


@pytest.fixture
def noop_process_run_repo():
    """
    Fixture que proporciona un NoOpProcessRunRepository para tests.
    Útil cuando necesitas verificar que se llamaron ciertos métodos
    sin escribir en la base de datos.

    Ejemplo:
        def test_mi_test(noop_process_run_repo):
            noop_process_run_repo.create_run("run_123", "TEST_PROCESS")
            assert "run_123" in noop_process_run_repo.get_runs_created()
    """
    return NoOpProcessRunRepository()


@pytest.fixture(scope="function")
def cleanup_process_runs():
    """
    Fixture que limpia SOLO los registros de process_run y process_run_log
    creados durante el test actual, preservando cualquier dato existente.

    Uso: Añadir como parámetro en tests que creen ProcessRun/ProcessRunLog
    y quieras que se limpien automáticamente después del test.

    Ejemplo:
        def test_mi_test(cleanup_process_runs):
            # tu test aquí
    """
    # ANTES del test: Capturar los IDs existentes
    session = SessionLocal()
    existing_run_ids = set()
    try:
        existing_run_ids = set(row[0] for row in session.query(ProcessRun.run_id).all())
    except Exception as e:
        print(f"⚠️ Error capturando IDs existentes: {e}")
    finally:
        session.close()

    yield  # Ejecuta el test

    # DESPUÉS del test: Eliminar solo los registros NUEVOS
    session = SessionLocal()
    try:
        # Obtener los IDs actuales
        current_run_ids = set(row[0] for row in session.query(ProcessRun.run_id).all())

        # Identificar los IDs nuevos (creados durante el test)
        new_run_ids = current_run_ids - existing_run_ids

        if new_run_ids:
            # Eliminar logs de los nuevos runs
            session.query(ProcessRunLog).filter(
                ProcessRunLog.run_id.in_(new_run_ids)
            ).delete(synchronize_session=False)

            # Eliminar los nuevos runs
            session.query(ProcessRun).filter(ProcessRun.run_id.in_(new_run_ids)).delete(
                synchronize_session=False
            )

            session.commit()
            print(f"🧹 Limpieza: {len(new_run_ids)} registros de test eliminados")
    except Exception as e:
        session.rollback()
        print(f"⚠️ Error limpiando registros de test: {e}")
    finally:
        session.close()
