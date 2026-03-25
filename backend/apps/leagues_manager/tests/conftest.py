"""
Fixture de pytest para tests unitarios.
- Deshabilita logging en BD automáticamente (NoOpProcessRunRepository)
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


@pytest.fixture(autouse=True)
def disable_file_logging():
    """
    Fixture que deshabilita automáticamente el logging en archivos para TODOS los tests.
    Los tests unitarios solo mostrarán logs en consola, sin generar archivos.
    """
    original_value = os.environ.get("FILE_LOGGING_ENABLED")
    os.environ["FILE_LOGGING_ENABLED"] = "false"
    yield
    # Restaurar valor original después del test
    if original_value is None:
        os.environ.pop("FILE_LOGGING_ENABLED", None)
    else:
        os.environ["FILE_LOGGING_ENABLED"] = original_value


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
