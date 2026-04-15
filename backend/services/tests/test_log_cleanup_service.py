"""
Tests unitarios para LogCleanupService
=======================================

Cubre todas las funcionalidades del servicio de limpieza de logs.
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# ✅ SOLUCION PERMANENTE PATH: Funciona en TODOS los entornos
ROOT_PROYECTO = Path(__file__).resolve().parents[4]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

# ✅ Cargar automaticamente variables de entorno
from dotenv import load_dotenv

load_dotenv(ROOT_PROYECTO / "backend" / ".env")

from backend.services.log_cleanup_service import LogCleanupService, CleanupResult


@pytest.fixture
def temp_dirs():
    """Crea directorios temporales para tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logs_dir = Path(tmpdir) / "logs"
        archive_dir = Path(tmpdir) / "archive"
        logs_dir.mkdir()
        archive_dir.mkdir()
        yield logs_dir, archive_dir


@pytest.fixture
def service(temp_dirs):
    """Crea instancia del servicio con directorios temporales."""
    logs_dir, archive_dir = temp_dirs
    return LogCleanupService(
        logs_dir=logs_dir,
        archive_dir=archive_dir,
        retention_days=3,
        archive_retention_days=30,
    )


class TestCleanupResult:
    """Tests para la clase CleanupResult."""

    def test_default_values(self):
        """Verifica valores por defecto."""
        result = CleanupResult()
        assert result.success is True
        assert result.archived_files == 0
        assert result.deleted_files == 0
        assert result.freed_space_mb == 0.0
        assert result.errors == []

    def test_to_dict(self):
        """Verifica conversión a diccionario."""
        result = CleanupResult(
            success=True,
            archived_files=5,
            deleted_files=3,
            freed_space_mb=10.5,
        )
        data = result.to_dict()
        assert data["success"] is True
        assert data["archived_files"] == 5
        assert data["deleted_files"] == 3
        assert data["freed_space_mb"] == 10.5

    def test_str_success(self):
        """Verifica representación string en éxito."""
        result = CleanupResult(success=True, archived_files=2, deleted_files=1)
        assert "✅ ÉXITO" in str(result)
        assert "Archivados: 2" in str(result)
        assert "Eliminados: 1" in str(result)

    def test_str_error(self):
        """Verifica representación string en error."""
        result = CleanupResult(success=False)
        assert "❌ ERROR" in str(result)


class TestLogCleanupService:
    """Tests para la clase LogCleanupService."""

    def test_initialization(self, service, temp_dirs):
        """Verifica inicialización correcta."""
        logs_dir, archive_dir = temp_dirs
        assert service.logs_dir == logs_dir
        assert service.archive_dir == archive_dir
        assert service.retention_days == 3
        assert service.archive_retention_days == 30

    def test_get_disk_usage_empty(self, service):
        """Verifica cálculo de espacio con directorios vacíos."""
        usage = service.get_disk_usage()
        assert usage["logs_size_mb"] == 0.0
        assert usage["archive_size_mb"] == 0.0
        assert usage["total_size_mb"] == 0.0

    def test_get_disk_usage_with_files(self, service, temp_dirs):
        """Verifica cálculo de espacio con archivos."""
        logs_dir, _ = temp_dirs

        # Crear archivo de prueba
        test_file = logs_dir / "test.log"
        test_file.write_text("x" * 1024 * 1024)  # 1 MB

        usage = service.get_disk_usage()
        assert usage["logs_size_mb"] >= 1.0

    def test_get_files_older_than_empty(self, service, temp_dirs):
        """Verifica obtención de archivos antiguos en directorio vacío."""
        logs_dir, _ = temp_dirs
        old_files = service._get_files_older_than(logs_dir, days=1)
        assert old_files == []

    def test_get_files_older_than_with_files(self, service, temp_dirs):
        """Verifica obtención de archivos antiguos."""
        logs_dir, _ = temp_dirs

        # Crear archivo reciente
        recent_file = logs_dir / "recent.log"
        recent_file.write_text("recent")

        # Crear archivo antiguo (simular con mtime)
        old_file = logs_dir / "old.log"
        old_file.write_text("old")

        # Modificar mtime para simular archivo antiguo
        old_time = (datetime.now() - timedelta(days=10)).timestamp()
        os.utime(old_file, (old_time, old_time))

        old_files = service._get_files_older_than(logs_dir, days=3)
        assert len(old_files) == 1
        assert old_file in old_files

    def test_get_files_older_than_nonexistent_dir(self, service):
        """Verifica manejo de directorio inexistente."""
        fake_dir = Path("/nonexistent/path")
        old_files = service._get_files_older_than(fake_dir, days=1)
        assert old_files == []

    def test_archive_old_logs_empty(self, service):
        """Verifica archivación con directorio vacío."""
        result = service.archive_old_logs()
        assert result.success is True
        assert result.archived_files == 0
        assert result.freed_space_mb == 0.0

    def test_archive_old_logs_with_files(self, service, temp_dirs):
        """Verifica archivación de archivos antiguos."""
        logs_dir, archive_dir = temp_dirs

        # Crear subdirectorio para simular estructura
        subdir = logs_dir / "scheduler"
        subdir.mkdir()

        # Crear archivo antiguo
        old_file = subdir / "old_scheduler.log"
        old_file.write_text("old log content")

        # Modificar mtime para simular archivo antiguo (usar time.time() para compatibilidad Windows)
        import time

        old_time = time.time() - (10 * 24 * 60 * 60)  # 10 días atrás
        os.utime(str(old_file), (old_time, old_time))

        # Verificar que el mtime se actualizó correctamente
        mtime = datetime.fromtimestamp(old_file.stat().st_mtime)
        assert mtime < datetime.now() - timedelta(
            days=3
        ), f"mtime={mtime}, now={datetime.now()}"

        result = service.archive_old_logs()

        assert result.success is True
        assert result.archived_files == 1
        assert not old_file.exists()
        assert (archive_dir / "scheduler" / "old_scheduler.log").exists()

    def test_archive_old_logs_skips_recent(self, service, temp_dirs):
        """Verifica que no archiva archivos recientes."""
        logs_dir, _ = temp_dirs

        # Crear archivo reciente
        recent_file = logs_dir / "recent.log"
        recent_file.write_text("recent")

        result = service.archive_old_logs()

        assert result.success is True
        assert result.archived_files == 0
        assert recent_file.exists()

    def test_delete_archived_logs_empty(self, service):
        """Verifica eliminación con directorio vacío."""
        result = service.delete_archived_logs()
        assert result.success is True
        assert result.deleted_files == 0

    def test_delete_archived_logs_with_files(self, service, temp_dirs):
        """Verifica eliminación de logs archivados antiguos."""
        _, archive_dir = temp_dirs

        # Crear archivo archivado antiguo
        old_file = archive_dir / "old_archived.log"
        old_file.write_text("old archived content")

        # Modificar mtime para simular archivo antiguo
        old_time = (datetime.now() - timedelta(days=60)).timestamp()
        os.utime(old_file, (old_time, old_time))

        result = service.delete_archived_logs()

        assert result.success is True
        assert result.deleted_files == 1
        assert not old_file.exists()

    def test_delete_archived_logs_skips_recent(self, service, temp_dirs):
        """Verifica que no elimina archivos archivados recientes."""
        _, archive_dir = temp_dirs

        # Crear archivo archivado reciente
        recent_file = archive_dir / "recent_archived.log"
        recent_file.write_text("recent archived")

        result = service.delete_archived_logs()

        assert result.success is True
        assert result.deleted_files == 0
        assert recent_file.exists()

    def test_run_cleanup_full_workflow(self, service, temp_dirs):
        """Verifica flujo completo de limpieza."""
        import time

        logs_dir, archive_dir = temp_dirs

        # Crear archivo antiguo para archivar
        old_log = logs_dir / "old.log"
        old_log.write_text("old log")
        old_time = time.time() - (10 * 24 * 60 * 60)  # 10 días atrás
        os.utime(str(old_log), (old_time, old_time))

        # Verificar que el mtime se actualizó correctamente
        mtime = datetime.fromtimestamp(old_log.stat().st_mtime)
        assert mtime < datetime.now() - timedelta(
            days=3
        ), f"mtime={mtime}, now={datetime.now()}"

        # Crear archivo archivado antiguo para eliminar (>30 días)
        old_archive = archive_dir / "old_archive.log"
        old_archive.write_text("old archive")
        old_time_archive = time.time() - (60 * 24 * 60 * 60)  # 60 días atrás
        os.utime(str(old_archive), (old_time_archive, old_time_archive))

        result = service.run_cleanup()

        assert result.success is True
        assert result.archived_files == 1
        assert result.deleted_files == 1

    def test_handles_file_disappearing(self, service, temp_dirs):
        """Verifica manejo de archivos que desaparecen durante procesamiento."""
        logs_dir, _ = temp_dirs

        # Crear archivo
        log_file = logs_dir / "test.log"
        log_file.write_text("test")
        old_time = (datetime.now() - timedelta(days=10)).timestamp()
        os.utime(log_file, (old_time, old_time))

        # Eliminar antes de procesar
        log_file.unlink()

        # No debe fallar
        result = service.archive_old_logs()
        assert result.success is True
        assert result.archived_files == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
