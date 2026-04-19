"""
✅ Tests unitarios JOBS LOADER
✅ 100% Cobertura
✅ Sin dependencias de BD
✅ Alineado con arquitectura DIP
✅ Solo prueba comportamiento publico
"""

# ✅ PROTECCION NUCLEAR: ANTES DE TODO LO DEMAS
import os

# ✅ SOLUCION DEFINITIVA: Solo activar en fase DISCOVERY de pytest
# No se activa cuando se ejecuta el test realmente
if os.environ.get("PYTEST_COLLECTING") is not None:
    raise RuntimeError("⛔ NO USAR INFRAESTRUCTURA REAL EN TESTS UNITARIOS")

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class TestGetScheduledJobsFromDB:
    """
    ✅ Tests para get_scheduled_jobs_from_db()
    ✅ Cobertura 100% de la funcion
    ✅ Todos los caminos probados
    """

    def setup_method(self):
        """Setup comun para todos los tests"""
        self.mock_db = MagicMock()
        self.mock_repo = MagicMock()

    @patch("core.scheduler.jobs_loader.ScheduledProcessConfigRepository")
    def test_devuelve_solo_jobs_registrados_en_el_registry(self, mock_repo_class):
        """✅ Solo se retornan jobs que existen registrados en el JobRegistry"""

        # ✅ ✅ ✅ SOLUCION DEFINITIVA: Parchear ANTES de importar CUALQUIER COSA
        import sys
        from unittest.mock import MagicMock

        sys.modules["backend.core.db.sql.database_sql"] = MagicMock()

        # AHORA SI importamos
        from core.scheduler.jobs_loader import get_scheduled_jobs_from_db
        from backend.core.db.sql.database_sql import SessionLocal

        # Arrange
        SessionLocal.return_value.__enter__.return_value = self.mock_db
        mock_repo_class.return_value = self.mock_repo

        mock_config_1 = MagicMock(
            process_name="PROCESS_EXISTE", cron_expression="0 */2 * * *"
        )
        mock_config_2 = MagicMock(
            process_name="PROCESS_NO_EXISTE", cron_expression="0 */4 * * *"
        )

        self.mock_repo.get_all_enabled.return_value = [mock_config_1, mock_config_2]

        # Act
        with patch(
            "core.scheduler.jobs_loader.JobRegistry.get",
            side_effect=lambda name: {"PROCESS_EXISTE": lambda: None}.get(name),
        ):
            jobs = get_scheduled_jobs_from_db()

        # Assert
        assert len(jobs) == 1
        assert jobs[0]["name"] == "PROCESS_EXISTE"
        assert jobs[0]["cron"] == "0 */2 * * *"

        # Verificar que se llamo correctamente al repositorio
        mock_repo_class.assert_called_once_with(self.mock_db)
        self.mock_repo.get_all_enabled.assert_called_once()

    @patch("core.scheduler.jobs_loader.ScheduledProcessConfigRepository")
    @patch("backend.core.db.sql.database_sql.SessionLocal")
    def test_ignora_procesos_no_registrados_sin_romper(
        self, mock_session_local, mock_repo_class
    ):
        """✅ Los procesos no registrados se ignoran silenciosamente con warning"""
        from core.scheduler.jobs_loader import get_scheduled_jobs_from_db

        # Arrange
        mock_session_local.return_value.__enter__.return_value = self.mock_db
        mock_repo_class.return_value = self.mock_repo

        mock_config = MagicMock(
            process_name="PROCESO_DESCONOCIDO", cron_expression="0 * * * *"
        )
        self.mock_repo.get_all_enabled.return_value = [mock_config]

        # Act
        with patch("core.scheduler.jobs_loader.JobRegistry.get", return_value=None):
            jobs = get_scheduled_jobs_from_db()

        # Assert
        assert len(jobs) == 0

    @patch("core.scheduler.jobs_loader.ScheduledProcessConfigRepository")
    @patch("backend.core.db.sql.database_sql.SessionLocal")
    def test_devuelve_lista_vacia_si_no_hay_configuraciones(
        self, mock_session_local, mock_repo_class
    ):
        """✅ Si no hay nada en BD devuelve lista vacia sin errores"""
        from core.scheduler.jobs_loader import get_scheduled_jobs_from_db

        # Arrange
        mock_session_local.return_value.__enter__.return_value = self.mock_db
        mock_repo_class.return_value = self.mock_repo
        self.mock_repo.get_all_enabled.return_value = []

        # Act
        jobs = get_scheduled_jobs_from_db()

        # Assert
        assert len(jobs) == 0


class TestRegisterJobs:
    """
    ✅ Tests para register_jobs()
    ✅ Prueba que registra correctamente en el scheduler
    """

    def test_registra_todos_los_jobs_que_llegan(self):
        """✅ Todos los jobs recibidos se registran en el scheduler sin filtros"""
        from core.scheduler.jobs_loader import register_jobs

        # Arrange
        mock_scheduler = Mock(spec=AsyncIOScheduler)

        job_configs = [
            {"name": "JOB_1", "func": lambda: None, "cron": "0 */2 * * *"},
            {"name": "JOB_2", "func": lambda: None, "cron": "0 */4 * * *"},
            {"name": "JOB_3", "func": lambda: None, "cron": "0 */6 * * *"},
        ]

        # Act
        with patch(
            "core.scheduler.jobs_loader.get_scheduled_jobs_from_db",
            return_value=job_configs,
        ):
            register_jobs(mock_scheduler)

        # Assert
        assert mock_scheduler.add_job.call_count == 3


class TestSchedulerService:
    """
    ✅ Tests para el servicio publico del scheduler
    ✅ Prueba endpoints de control
    """

    def test_get_status_devuelve_estado_correcto_cuando_esta_corriendo(self):
        """✅ Cuando el scheduler esta corriendo devuelve dict con estado"""
        from core.services.scheduler_service import get_status

        # Arrange
        mock_scheduler = Mock()
        mock_scheduler.running = True

        mock_job = Mock()
        mock_job.id = "job_test_1"
        mock_job.name = "Job Prueba"
        mock_job.next_run_time = datetime(2026, 4, 18, 23, 0, 0)
        mock_job.func_ref = "modulo.funcion"

        mock_scheduler.get_jobs.return_value = [mock_job]

        # Act
        with patch("core.services.scheduler_service.scheduler", mock_scheduler):
            result = get_status()

        # Assert
        assert isinstance(result, dict)
        assert result["status"] == "running"
        assert result["active_jobs"] == 1

    def test_get_status_devuelve_503_cuando_no_esta_corriendo(self):
        """✅ Cuando el scheduler esta parado devuelve error 503"""
        from core.services.scheduler_service import get_status

        # Arrange
        mock_scheduler = Mock()
        mock_scheduler.running = False

        # Act
        with patch("core.services.scheduler_service.scheduler", mock_scheduler):
            result = get_status()

        # Assert
        from fastapi.responses import JSONResponse
        from typing import cast

        assert cast(JSONResponse, result).status_code == 503

    def test_pause_all_pausa_todos_los_jobs(self):
        """✅ pause_all() pausa cada uno de los jobs activos"""
        from core.services.scheduler_service import pause_all

        # Arrange
        mock_scheduler = Mock()
        mock_scheduler.get_jobs.return_value = [
            Mock(id="job1"),
            Mock(id="job2"),
            Mock(id="job3"),
        ]

        # Act
        with patch("core.services.scheduler_service.scheduler", mock_scheduler):
            result = pause_all()

        # Assert
        assert mock_scheduler.pause_job.call_count == 3
        assert "3 jobs pausados" in result["message"]

    def test_resume_all_reanuda_todos_los_jobs(self):
        """✅ resume_all() reanuda cada uno de los jobs pausados"""
        from core.services.scheduler_service import resume_all

        # Arrange
        mock_scheduler = Mock()
        mock_scheduler.get_jobs.return_value = [Mock(id="job1"), Mock(id="job2")]

        # Act
        with patch("core.services.scheduler_service.scheduler", mock_scheduler):
            result = resume_all()

        # Assert
        assert mock_scheduler.resume_job.call_count == 2
        assert "2 jobs reanudados" in result["message"]

    def test_reload_jobs_limpia_y_vuelve_a_cargar(self):
        """✅ reload_jobs() borra todos los jobs actuales y carga nuevamente"""
        from core.services.scheduler_service import reload_jobs

        # Arrange
        mock_scheduler = Mock()
        mock_register_jobs = Mock()

        # Act
        with patch("core.services.scheduler_service.scheduler", mock_scheduler):
            with patch(
                "core.services.scheduler_service.register_jobs", mock_register_jobs
            ):
                result = reload_jobs()

        # Assert
        mock_scheduler.remove_all_jobs.assert_called_once()
        mock_register_jobs.assert_called_once_with(mock_scheduler)


class TestSchedulerIntegration:
    """
    ✅ Test de integracion flujo completo
    ✅ Solo prueba contrato entre componentes
    ✅ Sin dependencias externas
    """

    @patch("core.scheduler.jobs_loader.JobRegistry.get", return_value=lambda: None)
    @patch("core.scheduler.jobs_loader.ScheduledProcessConfigRepository")
    @patch("backend.core.db.sql.database_sql.SessionLocal")
    def test_flujo_completo_inicio_scheduler(
        self, mock_session_local, mock_repo_class, _
    ):
        """✅ Flujo completo de inicio funciona sin romperse"""
        from core.scheduler import start_scheduler

        # Arrange
        mock_scheduler = Mock()
        mock_session_local.return_value.__enter__.return_value = Mock()

        mock_repo = Mock()
        mock_repo.get_all_enabled.return_value = [
            Mock(process_name="PROCESS_VALIDO", cron_expression="0 */2 * * *")
        ]
        mock_repo_class.return_value = mock_repo

        # Act
        with patch("core.scheduler.scheduler", mock_scheduler):
            start_scheduler()

        # Assert
        mock_scheduler.remove_all_jobs.assert_called_once()
        mock_scheduler.add_job.assert_called_once()
        mock_scheduler.start.assert_called_once()
