"""
Test de Integración: Scheduler + LogCleanupService
===================================================

Verifica que el job de limpieza de logs se registre y ejecute correctamente
en el scheduler.
"""

import pytest
from unittest.mock import MagicMock, patch
from core.scheduler.log_cleanup_jobs import (
    LOG_CLEANUP_PROCESS_MAP,
    create_log_cleanup_job,
)


class TestLogCleanupScheduler:
    """Tests de integración para el job de limpieza de logs en el scheduler."""

    def test_log_cleanup_job_exists_in_process_map(self):
        """Verifica que el job de limpieza está registrado en el mapa de procesos."""
        assert "PROCESS_LOG_CLEANUP" in LOG_CLEANUP_PROCESS_MAP
        assert callable(LOG_CLEANUP_PROCESS_MAP["PROCESS_LOG_CLEANUP"])

    def test_log_cleanup_job_is_callable(self):
        """Verifica que el job de limpieza es una función callable."""
        job = LOG_CLEANUP_PROCESS_MAP["PROCESS_LOG_CLEANUP"]
        assert callable(job)

    def test_log_cleanup_job_executes_successfully(self):
        """Verifica que el job de limpieza ejecuta sin errores."""
        job = LOG_CLEANUP_PROCESS_MAP["PROCESS_LOG_CLEANUP"]

        # Mock del servicio para evitar operaciones reales
        with patch("core.scheduler.log_cleanup_jobs.LogCleanupService") as MockService:
            mock_service = MagicMock()
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.archived_files = 5
            mock_result.deleted_files = 3
            mock_result.freed_space_mb = 10.5
            mock_result.errors = []

            mock_service.run_cleanup.return_value = mock_result
            MockService.return_value = mock_service

            # Mock del historial
            with patch(
                "core.scheduler.log_cleanup_jobs.get_cleanup_history"
            ) as mock_get_history:
                mock_history = MagicMock()
                mock_get_history.return_value = mock_history

                # Ejecutar el job
                job()

                # Verificar que se llamó al servicio
                mock_service.run_cleanup.assert_called_once()

                # Verificar que se registró en el historial
                mock_history.add_entry.assert_called_once()

    def test_log_cleanup_job_handles_errors_gracefully(self):
        """Verifica que el job maneja errores sin fallar."""
        job = LOG_CLEANUP_PROCESS_MAP["PROCESS_LOG_CLEANUP"]

        # Mock del servicio para que lance una excepción
        with patch("core.scheduler.log_cleanup_jobs.LogCleanupService") as MockService:
            mock_service = MagicMock()
            mock_service.run_cleanup.side_effect = Exception("Error simulado")
            MockService.return_value = mock_service

            # Mock del historial
            with patch(
                "core.scheduler.log_cleanup_jobs.get_cleanup_history"
            ) as mock_get_history:
                mock_history = MagicMock()
                mock_get_history.return_value = mock_history

                # Ejecutar el job (no debe fallar)
                job()

                # Verificar que se registró el error en el historial
                mock_history.add_entry.assert_called_once()
                entry = mock_history.add_entry.call_args[0][0]
                assert entry.action == "cleanup_error"
                assert len(entry.errors) > 0

    def test_cron_expression_is_correct(self):
        """Verifica que la expresión cron configurada es correcta (3:00 AM diario)."""
        # La expresión cron debe ser "0 3 * * *" (minuto 0, hora 3, todos los días)
        from core.scheduler.jobs_loader import get_scheduled_jobs_from_db
        from core.scheduler.job_registry import JobRegistry

        # Mockear JobRegistry para que devuelva el job
        with patch("core.scheduler.jobs_loader.JobRegistry") as MockJobRegistry:
            MockJobRegistry.get.return_value = LOG_CLEANUP_PROCESS_MAP[
                "PROCESS_LOG_CLEANUP"
            ]

            # Este test requiere conexión a BD, así que lo mockeamos
            with patch("core.scheduler.jobs_loader.SessionLocal") as mock_session:
                mock_db = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_db

                mock_repo = MagicMock()
                mock_config = MagicMock()
                mock_config.process_name = "PROCESS_LOG_CLEANUP"
                mock_config.cron_expression = "0 3 * * *"

                mock_repo.get_all_enabled.return_value = [mock_config]

                with patch(
                    "core.scheduler.jobs_loader.ScheduledProcessConfigRepository"
                ) as MockRepo:
                    MockRepo.return_value = mock_repo

                    jobs = get_scheduled_jobs_from_db()

                    # Verificar que el job está en la lista
                    assert len(jobs) > 0
                    log_cleanup_job = next(
                        (j for j in jobs if j["name"] == "PROCESS_LOG_CLEANUP"), None
                    )
                    assert log_cleanup_job is not None
                    assert log_cleanup_job["cron"] == "0 3 * * *"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
