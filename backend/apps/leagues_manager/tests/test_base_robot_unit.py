# ------------------------------------------------------------------------------
# ✅ TEST UNITARIO BASE ROBOT
# ✅ Cumple con todas las reglas de Testing Explorer VS Code
# ✅ Ejecutable directamente con python
# ✅ Compatible con pytest
# ------------------------------------------------------------------------------
import sys
from pathlib import Path

# ✅ SOLUCION PERMANENTE PATH: Funciona en TODOS los entornos
ROOT_PROYECTO = Path(__file__).resolve().parents[5]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))
if str(ROOT_PROYECTO / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO / "backend"))

# ✅ Cargar automaticamente variables de entorno
from dotenv import load_dotenv

load_dotenv(ROOT_PROYECTO / "backend" / ".env")

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock

# Importar entidades y mocks
from apps.leagues_manager.tests.mock_data_leagues import (
    MockTorneo,
    MockDetalleFuenteExtraccion,
)
from apps.leagues_manager.tests.mock_repositories import MockProcessRunRepository
from apps.leagues_manager.domain.robots.base_robot import BaseRobot
from core.exceptions import ScrapingException


# ------------------------------------------------------------------------------
# ✅ ROBOT DE PRUEBA CONCRETO (PARA PROBAR CLASE ABSTRACTA)
# ------------------------------------------------------------------------------
class TestRobot(BaseRobot):
    """Robot concreto para pruebas de la clase abstracta BaseRobot"""

    async def _execute_scraping(self):
        """Implementación vacía para pruebas"""
        pass


class TestRobotFalla(BaseRobot):
    """Robot que falla intencionalmente para probar manejo de errores"""

    async def _execute_scraping(self):
        raise ValueError("Error simulado en scraping")


class TestRobotScrapingException(BaseRobot):
    """Robot que lanza ScrapingException para probar re-lanzamiento"""

    async def _execute_scraping(self):
        raise ScrapingException(
            robot_id="TEST-ROBOT",
            url="https://test.com",
            original_error=Exception("Error original"),
        )


# ------------------------------------------------------------------------------
# ✅ FIXTURES
# ------------------------------------------------------------------------------
@pytest.fixture
def test_data():
    """Fixture con datos de prueba"""
    torneo = MockTorneo(id=1, nombre="Torneo Test", is_active=True)

    detalle = MockDetalleFuenteExtraccion(
        id=1, torneo_id=1, fuente_id=1, url="https://test-url.com/scraping"
    )

    run_id = "test-run-12345"
    repo = MockProcessRunRepository()

    return {"torneo": torneo, "detalle": detalle, "run_id": run_id, "repo": repo}


# ------------------------------------------------------------------------------
# ✅ TESTS UNITARIOS
# ------------------------------------------------------------------------------
class TestBaseRobot:

    def test_inicializacion_correcta(self, test_data):
        """✅ Verifica que el robot se inicialice correctamente con todos los parametros"""

        robot = TestRobot(
            torneo=test_data["torneo"],
            detalle=test_data["detalle"],
            run_id=test_data["run_id"],
            repo=test_data["repo"],
        )

        # Verificar atributos
        assert robot.torneo == test_data["torneo"]
        assert robot.detalle == test_data["detalle"]
        assert robot.fuente == test_data["detalle"].fuente
        assert robot.run_id == test_data["run_id"]
        assert robot.repo == test_data["repo"]
        assert robot.robot_id is not None
        assert robot.job_context is not None

        print(f"✅ Test inicializacion correcto: robot_id={robot.robot_id}")

    @pytest.mark.asyncio
    async def test_run_ejecucion_exitosa(self, test_data):
        """✅ Verifica que el robot se ejecute exitosamente y registre logs correctamente"""

        # Inyectar RobotLogger con nuestro repo mock
        from apps.leagues_manager.domain.robots.robot_logger import RobotLogger

        robot_logger = RobotLogger(
            robot_id="TEST-ROBOT",
            run_id=test_data["run_id"],
            detalle_id=test_data["detalle"].id,
            repo=test_data["repo"],
        )

        robot = TestRobot(
            torneo=test_data["torneo"],
            detalle=test_data["detalle"],
            run_id=test_data["run_id"],
            repo=test_data["repo"],
            robot_logger=robot_logger,
        )

        with (
            patch(
                "apps.leagues_manager.domain.robots.base_robot.log_robot_start"
            ) as mock_start,
            patch(
                "apps.leagues_manager.domain.robots.base_robot.log_robot_end"
            ) as mock_end,
        ):

            await robot.run()

            # Verificar que se llamaron las funciones de logging
            mock_start.assert_called_once()
            mock_end.assert_called_once()

            # Verificar que se escribieron logs en el repositorio
            logs = test_data["repo"].get_logs(test_data["run_id"])
            assert len(logs) >= 2  # Al menos START y END

            # Verificar orden de logs
            assert logs[0]["step"] == "START"
            assert logs[0]["level"] == "info"
            assert logs[-1]["step"] == "END"
            assert logs[-1]["level"] == "info"

            print(f"✅ Test ejecucion exitosa correcto: {len(logs)} logs registrados")

    @pytest.mark.asyncio
    async def test_run_manejo_excepcion_general(self, test_data):
        """✅ Verifica que las excepciones generales se envuelvan en ScrapingException"""

        # Inyectar RobotLogger con nuestro repo mock
        from apps.leagues_manager.domain.robots.robot_logger import RobotLogger

        robot_logger = RobotLogger(
            robot_id="TEST-ROBOT",
            run_id=test_data["run_id"],
            detalle_id=test_data["detalle"].id,
            repo=test_data["repo"],
        )

        robot = TestRobotFalla(
            torneo=test_data["torneo"],
            detalle=test_data["detalle"],
            run_id=test_data["run_id"],
            repo=test_data["repo"],
            robot_logger=robot_logger,
        )

        with (
            patch("apps.leagues_manager.domain.robots.base_robot.log_robot_start"),
            patch(
                "apps.leagues_manager.domain.robots.base_robot.log_robot_end"
            ) as mock_end,
        ):

            with pytest.raises(ScrapingException) as exc_info:
                await robot.run()

            # Verificar que se registro el error
            mock_end.assert_called_once()
            assert mock_end.call_args[1]["success"] == False
            assert isinstance(mock_end.call_args[1]["error"], ValueError)

            # Verificar que la excepcion tiene los datos correctos
            assert exc_info.value.context["robot_id"] == robot.robot_id
            assert exc_info.value.context["url"] == test_data["detalle"].url

            # Verificar log de error en repositorio
            logs = test_data["repo"].get_logs(test_data["run_id"])
            error_log = next((log for log in logs if log["step"] == "ERROR"), None)
            assert error_log is not None
            assert error_log["level"] == "error"

            print("✅ Test manejo excepcion general correcto")

    @pytest.mark.asyncio
    async def test_run_relanza_scraping_exception(self, test_data):
        """✅ Verifica que ScrapingException no se envuelva nuevamente y se re-lance directamente"""

        # Inyectar RobotLogger con nuestro repo mock
        from apps.leagues_manager.domain.robots.robot_logger import RobotLogger

        robot_logger = RobotLogger(
            robot_id="TEST-ROBOT",
            run_id=test_data["run_id"],
            detalle_id=test_data["detalle"].id,
            repo=test_data["repo"],
        )

        robot = TestRobotScrapingException(
            torneo=test_data["torneo"],
            detalle=test_data["detalle"],
            run_id=test_data["run_id"],
            repo=test_data["repo"],
            robot_logger=robot_logger,
        )

        with (
            patch("apps.leagues_manager.domain.robots.base_robot.log_robot_start"),
            patch("apps.leagues_manager.domain.robots.base_robot.log_robot_end"),
        ):

            with pytest.raises(ScrapingException) as exc_info:
                await robot.run()

            # Verificar que es la misma excepcion original (no envuelta)
            assert "Error original" in exc_info.value.context["original_error_message"]

            print("✅ Test re-lanzamiento ScrapingException correcto")

    @pytest.mark.asyncio
    async def test_log_step_escribe_en_ambos_lugares(self, test_data):
        """✅ Verifica que _log_step escribe tanto en logger como en repositorio"""

        # Inyectar explicitamente el RobotLogger con nuestro repo mock
        from apps.leagues_manager.domain.robots.robot_logger import RobotLogger

        robot_logger = RobotLogger(
            robot_id="TEST-ROBOT",
            run_id=test_data["run_id"],
            detalle_id=test_data["detalle"].id,
            repo=test_data["repo"],
        )

        robot = TestRobot(
            torneo=test_data["torneo"],
            detalle=test_data["detalle"],
            run_id=test_data["run_id"],
            repo=test_data["repo"],
            robot_logger=robot_logger,
        )

        with patch("loguru.logger.info") as mock_logger:
            await robot._log_step(
                step="TEST_STEP",
                level="info",
                message="Mensaje de prueba",
                input_data="input=test",
                output_data="output=test",
            )

            # Verificar que se llamo al logger
            mock_logger.assert_called_once()

            # Verificar que se escribio en el repositorio
            logs = test_data["repo"].get_logs(test_data["run_id"])
            assert len(logs) == 1
            assert logs[0]["step"] == "TEST_STEP"
            assert logs[0]["message"] == "Mensaje de prueba"

            print("✅ Test log_step correcto")


# ------------------------------------------------------------------------------
# ✅ EJECUCION DIRECTA
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("✅ EJECUTANDO TEST UNITARIO BASE ROBOT DIRECTAMENTE")
    print("=" * 80)

    # Ejecutar pruebas manualmente
    test = TestBaseRobot()
    data = test_data()

    print("\n🔹 Ejecutando test_inicializacion_correcta...")
    test.test_inicializacion_correcta(data)

    print("\n🔹 Ejecutando test_log_step_escribe_en_ambos_lugares...")
    asyncio.run(test.test_log_step_escribe_en_ambos_lugares(data))

    print("\n🔹 Ejecutando test_run_ejecucion_exitosa...")
    asyncio.run(test.test_run_ejecucion_exitosa(data))

    print("\n🔹 Ejecutando test_run_manejo_excepcion_general...")
    asyncio.run(test.test_run_manejo_excepcion_general(data))

    print("\n🔹 Ejecutando test_run_relanza_scraping_exception...")
    asyncio.run(test.test_run_relanza_scraping_exception(data))

    print("\n" + "=" * 80)
    print("✅ TODOS LOS TESTS PASARON CORRECTAMENTE!")
    print("=" * 80)
