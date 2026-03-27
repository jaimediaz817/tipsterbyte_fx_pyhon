"""
Test de Integración: LogCleanupService + Cron + Historial
==========================================================

Simula un escenario real de años de logs acumulados,
ejecuta limpieza automática y verifica auditoría.
"""

import os
import sys
import tempfile
import time as time_module
from datetime import datetime
from pathlib import Path

import pytest

backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services.log_cleanup_service import LogCleanupService
from services.models.cleanup_history import CleanupHistory, CleanupHistoryEntry


class TestLogCleanupIntegration:
    """Tests de integración para limpieza de logs con cron y auditoría."""

    @pytest.fixture
    def temp_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = Path(tmpdir) / "logs"
            archive_dir = Path(tmpdir) / "archive"
            logs_dir.mkdir()
            archive_dir.mkdir()
            yield logs_dir, archive_dir

    @pytest.fixture
    def service(self, temp_dirs):
        logs_dir, archive_dir = temp_dirs
        return LogCleanupService(
            logs_dir=logs_dir,
            archive_dir=archive_dir,
            retention_days=3,
            archive_retention_days=30,
        )

    def test_simulate_years_of_logs(self, service, temp_dirs):
        """Simula logs acumulados de 2 años y ejecuta limpieza con auditoría."""
        logs_dir, archive_dir = temp_dirs
        history_file = archive_dir / "cleanup_history.json"

        print("\n Simulando logs de 2 anos (~730 dias)...")

        total_files = 50
        for i in range(total_files):
            days_back = 730 - i
            file_time = time_module.time() - (days_back * 24 * 60 * 60)
            log_file = logs_dir / f"app_{i:04d}.log"
            log_file.write_text(f"Log content for day {i}\n" * 10000)
            os.utime(str(log_file), (file_time, file_time))

        print(f" Creados {total_files} archivos de logs (~{total_files * 10} MB)")

        history = CleanupHistory(history_file=history_file)

        print("\n Simulando ejecucion de cron despues de 5 segundos...")
        time_module.sleep(0.1)

        start_time = time_module.time()
        result = service.archive_old_logs()
        duration = time_module.time() - start_time

        history_entry = CleanupHistoryEntry(
            timestamp=datetime.now(),
            profile_name="integration_test",
            action="archive",
            files_count=result.archived_files,
            freed_space_mb=result.freed_space_mb,
            files_processed=[
                f.name for f in list(logs_dir.glob("*.log"))[: result.archived_files]
            ],
            errors=result.errors,
            duration_seconds=duration,
        )
        history.add_entry(history_entry)

        print("\n Verificando resultados...")
        assert result.success is True
        assert result.archived_files > 0
        print(f" Archivados: {result.archived_files} archivos")
        print(f" Espacio liberado: {result.freed_space_mb:.2f} MB")

        stats = history.get_stats()
        assert stats["total_cleanups"] == 1
        print(f" Historial: {stats}")

        print("\n" + "=" * 60)
        print(" TEST DE INTEGRACION COMPLETADO EXITOSAMENTE")
        print("=" * 60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
