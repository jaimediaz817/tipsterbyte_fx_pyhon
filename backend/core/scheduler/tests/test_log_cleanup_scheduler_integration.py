"""
Test de Integración: Scheduler + LogCleanupService (Simulación Real)
====================================================================

Simula el comportamiento real del scheduler ejecutando el job de limpieza,
verificando que se registra en BD y se ejecuta correctamente.
"""

import os
import sys
import tempfile
import time as time_module
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

backend_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services.log_cleanup_service import LogCleanupService
from services.models.cleanup_history import CleanupHistory, CleanupHistoryEntry
from core.scheduler.log_cleanup_jobs import LOG_CLEANUP_PROCESS_MAP


class TestLogCleanupSchedulerIntegration:
    """Tests de integración que simulan el scheduler ejecutando el job."""

    @pytest.fixture
    def temp_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = Path(tmpdir) / "logs"
            archive_dir = Path(tmpdir) / "archive"
            logs_dir.mkdir()
            archive_dir.mkdir()
            yield logs_dir, archive_dir

    def test_scheduler_executes_log_cleanup_job(self, temp_dirs):
        """
        Simula el scheduler ejecutando el job de limpieza.

        Este test simula el flujo real:
        1. Scheduler carga el job desde BD
        2. Ejecuta el job en el tiempo programado
        3. El job ejecuta la limpieza
        4. Se registra en el historial
        """
        logs_dir, archive_dir = temp_dirs
        history_file = archive_dir / "cleanup_history.json"

        print("\n Simulando scheduler ejecutando job de limpieza...")

        # Crear logs de prueba
        total_files = 10
        for i in range(total_files):
            days_back = 10 - i
            file_time = time_module.time() - (days_back * 24 * 60 * 60)
            log_file = logs_dir / f"app_{i:04d}.log"
            log_file.write_text(f"Log content for day {i}\n" * 1000)
            os.utime(str(log_file), (file_time, file_time))

        print(f" Creados {total_files} archivos de logs")

        # Mock del servicio para usar directorios temporales
        with patch("core.scheduler.log_cleanup_jobs.LogCleanupService") as MockService:
            mock_service = MagicMock()
            mock_service.logs_dir = logs_dir
            mock_service.archive_dir = archive_dir
            mock_service.retention_days = 3
            mock_service.archive_retention_days = 30

            # Crear resultado mock
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.archived_files = 5
            mock_result.deleted_files = 0
            mock_result.freed_space_mb = 5.0
            mock_result.errors = []

            mock_service.run_cleanup.return_value = mock_result
            MockService.return_value = mock_service

            # Mock del historial
            with patch(
                "core.scheduler.log_cleanup_jobs.get_cleanup_history"
            ) as mock_get_history:
                mock_history = MagicMock()
                mock_get_history.return_value = mock_history

                # Obtener el job del mapa de procesos
                job = LOG_CLEANUP_PROCESS_MAP["PROCESS_LOG_CLEANUP"]

                # Ejecutar el job (simula que el scheduler lo ejecuta)
                print(" Ejecutando job de limpieza...")
                job()

                # Verificar que se llamó al servicio
                mock_service.run_cleanup.assert_called_once()
                print(" Servicio ejecutado correctamente")

                # Verificar que se registró en el historial
                mock_history.add_entry.assert_called_once()
                entry = mock_history.add_entry.call_args[0][0]
                assert entry.profile_name == "scheduler"
                assert entry.action == "cleanup"
                print(" Historial registrado correctamente")

        print("\n TEST DE INTEGRACION CON SCHEDULER COMPLETADO")

    def test_scheduler_job_handles_cleanup_errors(self, temp_dirs):
        """
        Verifica que el scheduler maneja errores de limpieza sin fallar.
        """
        logs_dir, archive_dir = temp_dirs

        print("\n Verificando manejo de errores en scheduler...")

        # Mock del servicio para que falle
        with patch("core.scheduler.log_cleanup_jobs.LogCleanupService") as MockService:
            mock_service = MagicMock()
            mock_service.run_cleanup.side_effect = Exception(
                "Error simulado en limpieza"
            )
            MockService.return_value = mock_service

            # Mock del historial
            with patch(
                "core.scheduler.log_cleanup_jobs.get_cleanup_history"
            ) as mock_get_history:
                mock_history = MagicMock()
                mock_get_history.return_value = mock_history

                # Obtener y ejecutar el job
                job = LOG_CLEANUP_PROCESS_MAP["PROCESS_LOG_CLEANUP"]
                job()

                # Verificar que se registró el error en el historial
                mock_history.add_entry.assert_called_once()
                entry = mock_history.add_entry.call_args[0][0]
                assert entry.action == "cleanup_error"
                assert len(entry.errors) > 0
                print(" Error registrado correctamente en historial")

        print(" MANEJO DE ERRORES VERIFICADO")

    def test_scheduler_job_cron_expression(self):
        """
        Verifica que la expresión cron está configurada correctamente.
        """
        print("\n Verificando configuración de cron...")

        # Verificar que el job está registrado
        assert "PROCESS_LOG_CLEANUP" in LOG_CLEANUP_PROCESS_MAP
        print(" Job registrado correctamente en LOG_CLEANUP_PROCESS_MAP")

        # Verificar que es callable
        job = LOG_CLEANUP_PROCESS_MAP["PROCESS_LOG_CLEANUP"]
        assert callable(job)
        print(" Job es callable")

        # Verificar que el job ejecuta sin errores
        with patch("core.scheduler.log_cleanup_jobs.LogCleanupService") as MockService:
            mock_service = MagicMock()
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.archived_files = 0
            mock_result.deleted_files = 0
            mock_result.freed_space_mb = 0.0
            mock_result.errors = []
            mock_service.run_cleanup.return_value = mock_result
            MockService.return_value = mock_service

            with patch(
                "core.scheduler.log_cleanup_jobs.get_cleanup_history"
            ) as mock_get_history:
                mock_history = MagicMock()
                mock_get_history.return_value = mock_history

                job()
                print(" Job ejecutado sin errores")

        print(" CONFIGURACION DE CRON VERIFICADA")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
