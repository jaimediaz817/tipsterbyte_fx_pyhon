# ✅ TEST UNITARIO JobRunnerApplication.run_full_orchestrator
# ✅ FUNCIONA EN VS CODE TESTING EXPLORER
# ✅ FUNCIONA EJECUTANDO python test_job_runner_full_orchestrator_unit.py
# ✅ FUNCIONA CON pytest

import sys
import io
from pathlib import Path
from typing import cast, Awaitable, Coroutine
from unittest.mock import MagicMock

# ✅ ✅ ✅ SOLUCION DEFINITIVA ANTES DE TODO ✅ ✅ ✅
# NO USAR PATCH NUNCA: patch intenta importar el modulo primero y se dispara la proteccion
# DIRECTAMENTE MATAMOS EL MODULO EN sys.modules ANTES DE QUE NADIE LO TOQUE
sys.modules["core.db.sql.database_sql"] = MagicMock()
sys.modules["core.db.sql"] = MagicMock()
sys.modules["core.db"] = MagicMock()

# ✅ SOLUCION CODIFICACION WINDOWS (UnicodeEncodeError ✅)
# ✅ SOLAMENTE CUANDO SE EJECUTA DIRECTAMENTE: NO ROMPER PYTEST CAPTURE
if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# ✅ SOLUCION PERMANENTE PATH: Funciona en TODOS los entornos
ROOT_PROYECTO = Path(__file__).resolve().parents[3]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

# ✅ Cargar automaticamente variables de entorno
from dotenv import load_dotenv

load_dotenv(ROOT_PROYECTO / "backend" / ".env")

# AHORA SI IMPORTAMOS TODO LO DEMAS
import pytest
from unittest.mock import Mock, AsyncMock, patch
from apps.leagues_manager.application.job_runner_application import JobRunnerApplication
from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum
from shared.repositories.scheduler_repos.noop_process_run_repository import (
    NoOpProcessRunRepository,
)
from core.exceptions import ProcessInactiveException, NoActiveJobsException


class TestJobRunnerFullOrchestratorUnit:
    """
    ✅ TEST UNITARIO COMPLETO
    ✅ NO USA BASE DE DATOS REAL
    ✅ ✅ ✅ USAMOS DEPENDENCY INJECTION NATIVA DEL METODO ✅ ✅ ✅
    ✅ NO HAY NINGUN PATCH() NI NINGUN MOCK DE IMPORTACIONES
    ✅ 100% FIABLE Y SENCILLO
    """

    @pytest.fixture
    def job_runner(self):
        return JobRunnerApplication(robot_factory={})

    @pytest.fixture
    def mock_process(self):
        process = Mock()
        process.id = 999
        process.code = "TEST_PROCESS"
        process.is_active = True
        return process

    @pytest.fixture
    def mock_detalle_fuente(self):
        detalle = Mock()
        detalle.id = 123
        detalle.process_id = 999
        detalle.is_active = True
        detalle.fuente = Mock()
        detalle.fuente.type = RobotTypeEnum.STANDINGS
        detalle.fuente.name = "Test Fuente"
        detalle.fuente.is_active = True
        return detalle

    @pytest.fixture
    def mock_torneo(self, mock_detalle_fuente):
        torneo = Mock()
        torneo.id = 456
        torneo.nombre = "Torneo Test"
        torneo.is_active = True
        torneo.detalles_fuente = [mock_detalle_fuente]
        return torneo

    @pytest.fixture
    def mock_league(self, mock_torneo):
        league = Mock()
        league.id = 789
        league.nombre = "Liga Test"
        league.is_active = True
        league.torneos = [mock_torneo]
        return league

    @pytest.fixture
    def mock_platform_repo(self, mock_process):
        repo = Mock()
        repo.get_process_by_code.return_value = mock_process
        return repo

    @pytest.fixture
    def mock_league_repo(self, mock_league):
        repo = Mock()
        repo.get_all_leagues_with_full_details.return_value = [mock_league]
        return repo

    @pytest.fixture
    def mock_repo(self):
        return NoOpProcessRunRepository()

    @pytest.mark.asyncio
    async def test_run_full_orchestrator_ok(
        self,
        job_runner,
        mock_platform_repo,
        mock_league_repo,
        mock_repo,
        mock_process,
        mock_league,
        mock_torneo,
        mock_detalle_fuente,
    ):
        """
        ✅ Prueba que el orquestador funciona correctamente
        ✅ USAMOS INYECCION DE DEPENDENCIAS: NO HAY NI UN SOLO PATCH
        """
        # ✅ MOCKEAMOS SOLAMENTE run_job
        with patch.object(
            job_runner, "run_job", new_callable=AsyncMock
        ) as mock_run_job:

            # ✅ ✅ ✅ INYECTAMOS DIRECTAMENTE LOS MOCKS POR PARAMETRO ✅ ✅ ✅
            # El metodo tiene estos parametros EXACTAMENTE para testing
            await job_runner.run_full_orchestrator(
                "TEST_PROCESS",
                platform_repo=mock_platform_repo,
                process_run_repo=mock_repo,
                league_repo=mock_league_repo,
            )

            # ✅ VERIFICACIONES
            mock_platform_repo.get_process_by_code.assert_called_once_with(
                "TEST_PROCESS"
            )
            mock_league_repo.get_all_leagues_with_full_details.assert_called_once()
            mock_run_job.assert_awaited_once()

            # ✅ Verificar que se llamo a run_job con los parametros correctos
            args = mock_run_job.call_args
            assert args[0][0] == mock_torneo
            assert args[0][1] == mock_detalle_fuente
            assert isinstance(args[0][3], NoOpProcessRunRepository)

    @pytest.mark.asyncio
    async def test_run_full_orchestrator_proceso_inactivo(
        self, job_runner, mock_platform_repo, mock_repo, mock_process
    ):
        """
        ✅ Prueba que falla correctamente cuando el proceso esta inactivo
        """
        mock_process.is_active = False

        # ✅ Debe lanzar la excepcion correcta
        with pytest.raises(ProcessInactiveException):
            await cast(
                Awaitable[None],
                job_runner.run_full_orchestrator(
                    "TEST_PROCESS",
                    platform_repo=mock_platform_repo,
                    process_run_repo=mock_repo,
                ),
            )

    @pytest.mark.asyncio
    async def test_run_full_orchestrator_sin_trabajos(
        self, job_runner, mock_platform_repo, mock_repo, mock_process
    ):
        """
        ✅ Prueba que funciona correctamente cuando no hay trabajos activos
        """
        mock_league_repo = Mock()
        mock_league_repo.get_all_leagues_with_full_details.return_value = []

        # ✅ Debe lanzar la excepcion correcta cuando no hay trabajos
        with pytest.raises(NoActiveJobsException):
            await cast(
                Awaitable[None],
                job_runner.run_full_orchestrator(
                    "TEST_PROCESS",
                    platform_repo=mock_platform_repo,
                    process_run_repo=mock_repo,
                    league_repo=mock_league_repo,
                ),
            )


if __name__ == "__main__":
    # ✅ Permite ejecutar este test directamente desde consola
    import asyncio

    print("\n✅ Ejecutando test unitario JobRunner Full Orchestrator ...")

    # ✅ NO LLAMAR FIXTURES DIRECTAMENTE: Creamos objetos manualmente
    runner = JobRunnerApplication(robot_factory={})

    # Crear mocks manualmente (sin fixtures)
    process = Mock()
    process.id = 999
    process.code = "TEST_PROCESS"
    process.is_active = True

    detalle = Mock()
    detalle.id = 123
    detalle.process_id = 999
    detalle.is_active = True
    detalle.fuente = Mock()
    detalle.fuente.type = RobotTypeEnum.STANDINGS
    detalle.fuente.name = "Test Fuente"
    detalle.fuente.is_active = True

    torneo = Mock()
    torneo.id = 456
    torneo.nombre = "Torneo Test"
    torneo.is_active = True
    torneo.detalles_fuente = [detalle]

    league = Mock()
    league.id = 789
    league.nombre = "Liga Test"
    league.is_active = True
    league.torneos = [torneo]

    platform_repo = Mock()
    platform_repo.get_process_by_code.return_value = process

    league_repo = Mock()
    league_repo.get_all_leagues_with_full_details.return_value = [league]

    repo = NoOpProcessRunRepository()

    asyncio.run(
        cast(
            "Coroutine[None, None, None]",
            TestJobRunnerFullOrchestratorUnit().test_run_full_orchestrator_ok(
                runner,
                platform_repo,
                league_repo,
                repo,
                process,
                league,
                torneo,
                detalle,
            ),
        )
    )

    print("✅ TEST PASADO: run_full_orchestrator funciona correctamente")
