"""
Tests unitarios para el módulo de scheduler.
Valida el comportamiento del cargador de jobs y el registro de trabajos programados.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


class TestGetScheduledJobsFromDB:
    """Tests para la función get_scheduled_jobs_from_db."""

    @patch("core.scheduler.jobs_loader.SessionLocal")
    @patch("core.scheduler.jobs_loader.ScheduledProcessConfigRepository")
    def test_get_jobs_with_valid_process_names(
        self, mock_repo_class, mock_session_local
    ):
        """Test que verifica que los jobs se cargan correctamente cuando los process_name son válidos."""
        from core.scheduler.jobs_loader import get_scheduled_jobs_from_db

        # Mock del contexto de sesión
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        mock_session_local.return_value.__exit__.return_value = None

        # Mock del repositorio
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        # Mock de configuraciones de la BD
        mock_config_1 = MagicMock()
        mock_config_1.process_name = "PROCESS_STANDINGS_EXTRACTION"
        mock_config_1.cron_expression = "0 */2 * * *"

        mock_config_2 = MagicMock()
        mock_config_2.process_name = "PROCESS_CALENDAR_EXTRACTION"
        mock_config_2.cron_expression = "0 */4 * * *"

        mock_repo.get_all_enabled.return_value = [mock_config_1, mock_config_2]

        # Ejecutar
        with patch(
            "core.scheduler.jobs_loader.JobRegistry.get",
            side_effect=lambda name: {
                "PROCESS_STANDINGS_EXTRACTION": lambda: None,
                "PROCESS_CALENDAR_EXTRACTION": lambda: None,
            }.get(name),
        ):
            jobs = get_scheduled_jobs_from_db()

        # Verificar
        assert len(jobs) == 2
        assert jobs[0]["name"] == "PROCESS_STANDINGS_EXTRACTION"
        assert jobs[0]["cron"] == "0 */2 * * *"
        assert jobs[1]["name"] == "PROCESS_CALENDAR_EXTRACTION"
        assert jobs[1]["cron"] == "0 */4 * * *"

    @patch("core.scheduler.jobs_loader.SessionLocal")
    @patch("core.scheduler.jobs_loader.ScheduledProcessConfigRepository")
    def test_get_jobs_with_unregistered_process(
        self, mock_repo_class, mock_session_local
    ):
        """Test que verifica que los jobs no registrados se ignoran con warning."""
        from core.scheduler.jobs_loader import get_scheduled_jobs_from_db

        # Mock del contexto de sesión
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        mock_session_local.return_value.__exit__.return_value = None

        # Mock del repositorio
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        # Mock de configuraciones con un proceso no registrado
        mock_config = MagicMock()
        mock_config.process_name = "UNREGISTERED_PROCESS"
        mock_config.cron_expression = "0 * * * *"

        mock_repo.get_all_enabled.return_value = [mock_config]

        # Ejecutar con mapa vacío
        with patch("core.scheduler.jobs_loader.JobRegistry.get", return_value=None):
            jobs = get_scheduled_jobs_from_db()

        # Verificar que no se agregó el job no registrado
        assert len(jobs) == 0

    @patch("core.scheduler.jobs_loader.SessionLocal")
    @patch("core.scheduler.jobs_loader.ScheduledProcessConfigRepository")
    def test_get_jobs_empty_database(self, mock_repo_class, mock_session_local):
        """Test que verifica el comportamiento cuando no hay jobs en la BD."""
        from core.scheduler.jobs_loader import get_scheduled_jobs_from_db

        # Mock del contexto de sesión
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        mock_session_local.return_value.__exit__.return_value = None

        # Mock del repositorio vacío
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_all_enabled.return_value = []

        # Ejecutar
        jobs = get_scheduled_jobs_from_db()

        # Verificar
        assert len(jobs) == 0


class TestRegisterJobs:
    """Tests para la función register_jobs."""

    def test_register_jobs_with_valid_config(self):
        """Test que verifica que los jobs se registran correctamente en el scheduler."""
        from core.scheduler.jobs_loader import register_jobs

        # Mock del scheduler
        mock_scheduler = MagicMock()

        # Mock de configuraciones de jobs
        mock_func_1 = MagicMock()
        mock_func_2 = MagicMock()

        job_configs = [
            {
                "name": "PROCESS_STANDINGS_EXTRACTION",
                "func": mock_func_1,
                "cron": "0 */2 * * *",
            },
            {
                "name": "PROCESS_CALENDAR_EXTRACTION",
                "func": mock_func_2,
                "cron": "0 */4 * * *",
            },
        ]

        with patch(
            "core.scheduler.jobs_loader.get_scheduled_jobs_from_db",
            return_value=job_configs,
        ):
            register_jobs(mock_scheduler)

        # Verificar que se llamó add_job para cada configuración
        assert mock_scheduler.add_job.call_count == 2

    def test_register_jobs_with_valid_job_config(self):
        """Test que verifica que los jobs se registran correctamente."""
        from core.scheduler.jobs_loader import register_jobs

        # Mock del scheduler
        mock_scheduler = MagicMock()

        # Mock de configuración con función faltante
        job_configs = [
            {
                "name": "MISSING_PROCESS",
                "func": lambda: None,
                "cron": "0 * * * *",
            }
        ]

        with patch(
            "core.scheduler.jobs_loader.get_scheduled_jobs_from_db",
            return_value=job_configs,
        ):
            register_jobs(mock_scheduler)

        # La validacion se hace en get_scheduled_jobs_from_db, register_jobs registra todo lo que llega
        assert mock_scheduler.add_job.call_count == 1


class TestSchedulerService:
    """Tests para el servicio del scheduler."""

    @patch("core.services.scheduler_service.scheduler")
    def test_get_status_when_running(self, mock_scheduler):
        """Test que verifica el estado del scheduler cuando está corriendo."""
        from core.services.scheduler_service import get_status

        # Mock del scheduler corriendo
        mock_scheduler.running = True

        # Mock de jobs
        mock_job = MagicMock()
        mock_job.id = "test_job_1"
        mock_job.name = "Test Job"
        mock_job.next_run_time = datetime(2026, 3, 20, 19, 30, 0)
        mock_job.func_ref = "test.module.function"

        mock_scheduler.get_jobs.return_value = [mock_job]

        # Ejecutar
        result = get_status()

        # Verificar - result es un dict cuando scheduler está corriendo
        assert isinstance(result, dict)
        assert result["status"] == "running"
        assert result["active_jobs"] == 1
        assert len(result["jobs"]) == 1
        assert result["jobs"][0]["id"] == "test_job_1"

    @patch("core.services.scheduler_service.scheduler")
    def test_get_status_when_not_running(self, mock_scheduler):
        """Test que verifica el estado del scheduler cuando no está corriendo."""
        from core.services.scheduler_service import get_status
        from fastapi.responses import JSONResponse

        # Mock del scheduler detenido
        mock_scheduler.running = False

        # Ejecutar
        result = get_status()

        # Verificar que retorna JSONResponse con error 503
        assert isinstance(result, JSONResponse)
        assert result.status_code == 503

    @patch("core.services.scheduler_service.scheduler")
    def test_pause_all_jobs(self, mock_scheduler):
        """Test que verifica que se pausan todos los jobs."""
        from core.services.scheduler_service import pause_all

        # Mock de jobs
        mock_job_1 = MagicMock()
        mock_job_1.id = "job_1"
        mock_job_2 = MagicMock()
        mock_job_2.id = "job_2"

        mock_scheduler.get_jobs.return_value = [mock_job_1, mock_job_2]

        # Ejecutar
        result = pause_all()

        # Verificar
        assert mock_scheduler.pause_job.call_count == 2
        assert "2 jobs pausados" in result["message"]

    @patch("core.services.scheduler_service.scheduler")
    def test_resume_all_jobs(self, mock_scheduler):
        """Test que verifica que se reanudan todos los jobs."""
        from core.services.scheduler_service import resume_all

        # Mock de jobs
        mock_job_1 = MagicMock()
        mock_job_1.id = "job_1"
        mock_job_2 = MagicMock()
        mock_job_2.id = "job_2"

        mock_scheduler.get_jobs.return_value = [mock_job_1, mock_job_2]

        # Ejecutar
        result = resume_all()

        # Verificar
        assert mock_scheduler.resume_job.call_count == 2
        assert "2 jobs reanudados" in result["message"]

    @patch("core.services.scheduler_service.scheduler")
    def test_pause_specific_job(self, mock_scheduler):
        """Test que verifica que se pausa un job específico."""
        from core.services.scheduler_service import pause

        # Ejecutar
        result = pause("test_job_id")

        # Verificar
        mock_scheduler.pause_job.assert_called_once_with("test_job_id")
        assert "test_job_id pausado" in result["message"]

    @patch("core.services.scheduler_service.scheduler")
    def test_resume_specific_job(self, mock_scheduler):
        """Test que verifica que se reanuda un job específico."""
        from core.services.scheduler_service import resume

        # Ejecutar
        result = resume("test_job_id")

        # Verificar
        mock_scheduler.resume_job.assert_called_once_with("test_job_id")
        assert "test_job_id reanudado" in result["message"]

    @patch("core.services.scheduler_service.register_jobs")
    @patch("core.services.scheduler_service.scheduler")
    def test_reload_jobs(self, mock_scheduler, mock_register_jobs):
        """Test que verifica que los jobs se recargan correctamente."""
        from core.services.scheduler_service import reload_jobs

        # Ejecutar
        result = reload_jobs()

        # Verificar
        mock_scheduler.remove_all_jobs.assert_called_once()
        mock_register_jobs.assert_called_once_with(mock_scheduler)
        assert "recargados" in result["message"]


class TestSchedulerIntegration:
    """Tests de integración para el flujo completo del scheduler."""

    @patch("core.scheduler.jobs_loader.SessionLocal")
    @patch("core.scheduler.jobs_loader.ScheduledProcessConfigRepository")
    @patch("core.scheduler.scheduler")
    def test_full_scheduler_startup_flow(
        self, mock_scheduler, mock_repo_class, mock_session_local
    ):
        """Test de integración que simula el flujo completo de inicio del scheduler."""
        from core.scheduler import start_scheduler

        # Mock del contexto de sesión
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        mock_session_local.return_value.__exit__.return_value = None

        # Mock del repositorio
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        # Mock de configuraciones
        mock_config = MagicMock()
        mock_config.process_name = "PROCESS_STANDINGS_EXTRACTION"
        mock_config.cron_expression = "0 */2 * * *"

        mock_repo.get_all_enabled.return_value = [mock_config]

        # Mock del JobRegistry
        mock_func = MagicMock()
        with patch(
            "core.scheduler.jobs_loader.JobRegistry.get", return_value=mock_func
        ):
            # Ejecutar
            start_scheduler()

        # Verificar flujo completo
        mock_scheduler.remove_all_jobs.assert_called_once()
        mock_scheduler.add_job.assert_called_once()
        mock_scheduler.start.assert_called_once()
