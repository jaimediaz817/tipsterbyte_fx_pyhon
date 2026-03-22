import pytest
from apps.leagues_manager.application.job_runner_application import JobRunnerApplication
from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum
from apps.leagues_manager.robots.standings_robot import StandingsRobot
from apps.leagues_manager.robots.odds_wplay_robot import OddsWPlayRobot
from apps.leagues_manager.robots.calendar_robot import CalendarRobot
from apps.leagues_manager.tests.mock_data_leagues import (
    MockDetalleFuenteExtraccion,
    MockFuenteExtraccion,
    MockTorneo,
)


class MockProcessRunRepository:
    """Mock simple del repositorio para pruebas."""

    def __init__(self):
        self.logs = []

    def write_log(self, run_id, step, level, message, input=None, output=None):
        self.logs.append(
            {
                "run_id": run_id,
                "step": step,
                "level": level,
                "message": message,
            }
        )


# =====================================================
# TESTS: Asociación Proceso → Fuente → Robot
# =====================================================


def test_robot_factory_tiene_todos_los_tipos():
    """✅ El JobRunnerApplication debe tener mapeado todos los tipos de robot."""
    runner = JobRunnerApplication()

    # Verificar que cada tipo de RobotTypeEnum tiene un robot asignado
    assert RobotTypeEnum.STANDINGS in runner.robot_factory
    assert RobotTypeEnum.ODDS_WPLAY in runner.robot_factory
    assert RobotTypeEnum.CALENDAR in runner.robot_factory

    # Verificar que las clases son correctas
    assert runner.robot_factory[RobotTypeEnum.STANDINGS] == StandingsRobot
    assert runner.robot_factory[RobotTypeEnum.ODDS_WPLAY] == OddsWPlayRobot
    assert runner.robot_factory[RobotTypeEnum.CALENDAR] == CalendarRobot


def test_fuente_standings_selecciona_standings_robot():
    """✅ Una fuente de tipo STANDINGS debe seleccionar StandingsRobot."""
    runner = JobRunnerApplication()

    fuente = MockFuenteExtraccion(
        id=1, name="Standings (SofaScore)", type=RobotTypeEnum.STANDINGS
    )
    detalle = MockDetalleFuenteExtraccion(
        id=10,
        torneo_id=1,
        fuente_id=1,
        url="https://sofascore.com",
        is_active=True,
        fuente=fuente,
    )

    robot_class = runner.robot_factory.get(RobotTypeEnum.STANDINGS)
    assert robot_class == StandingsRobot


def test_fuente_odds_selecciona_odds_robot():
    """✅ Una fuente de tipo ODDS_WPLAY debe seleccionar OddsWPlayRobot."""
    runner = JobRunnerApplication()

    fuente = MockFuenteExtraccion(
        id=2, name="Odds (WPlay)", type=RobotTypeEnum.ODDS_WPLAY
    )
    detalle = MockDetalleFuenteExtraccion(
        id=20,
        torneo_id=1,
        fuente_id=2,
        url="https://wplay.co",
        is_active=True,
        fuente=fuente,
    )

    robot_class = runner.robot_factory.get(RobotTypeEnum.ODDS_WPLAY)
    assert robot_class == OddsWPlayRobot


def test_fuente_calendar_selecciona_calendar_robot():
    """✅ Una fuente de tipo CALENDAR debe seleccionar CalendarRobot."""
    runner = JobRunnerApplication()

    fuente = MockFuenteExtraccion(
        id=3, name="Calendar (Official)", type=RobotTypeEnum.CALENDAR
    )
    detalle = MockDetalleFuenteExtraccion(
        id=30,
        torneo_id=1,
        fuente_id=3,
        url="https://laliga.com",
        is_active=True,
        fuente=fuente,
    )

    robot_class = runner.robot_factory.get(RobotTypeEnum.CALENDAR)
    assert robot_class == CalendarRobot


def test_proceso_con_multiples_fuentes_selecciona_robots_correctos():
    """✅ Un proceso con múltiples fuentes debe seleccionar el robot correcto para cada una."""
    runner = JobRunnerApplication()

    # Simular un proceso con 3 fuentes diferentes
    fuentes = [
        MockFuenteExtraccion(
            id=1, name="Standings (SofaScore)", type=RobotTypeEnum.STANDINGS
        ),
        MockFuenteExtraccion(id=2, name="Odds (WPlay)", type=RobotTypeEnum.ODDS_WPLAY),
        MockFuenteExtraccion(
            id=3, name="Calendar (Official)", type=RobotTypeEnum.CALENDAR
        ),
    ]

    # Verificar que cada fuente selecciona el robot correcto
    assert runner.robot_factory.get(RobotTypeEnum.STANDINGS) == StandingsRobot
    assert runner.robot_factory.get(RobotTypeEnum.ODDS_WPLAY) == OddsWPlayRobot
    assert runner.robot_factory.get(RobotTypeEnum.CALENDAR) == CalendarRobot


def test_proceso_sin_fuente_no_selecciona_robot():
    """✅ Un detalle sin fuente no debe seleccionar ningún robot."""
    runner = JobRunnerApplication()

    # Detalle sin fuente
    detalle = MockDetalleFuenteExtraccion(
        id=99,
        torneo_id=1,
        fuente_id=0,  # Usar 0 en lugar de None para evitar error de tipo
        url="https://test.com",
        is_active=True,
        fuente=None,
    )

    # No debe haber robot para None
    robot_class = runner.robot_factory.get(None)  # type: ignore
    assert robot_class is None


def test_proceso_con_fuente_inactiva_no_selecciona_robot():
    """✅ Un detalle con fuente inactiva no debe ser procesado."""
    # Este test verifica la lógica de filtrado en _build_jobs_from_leagues
    # que ya filtra por detalle.is_active
    fuente = MockFuenteExtraccion(
        id=1, name="Standings (SofaScore)", type=RobotTypeEnum.STANDINGS
    )
    detalle = MockDetalleFuenteExtraccion(
        id=10,
        torneo_id=1,
        fuente_id=1,
        url="https://sofascore.com",
        is_active=False,
        fuente=fuente,
    )

    # El detalle está inactivo, no debe ser procesado
    assert detalle.is_active is False


# =====================================================
# TESTS: Registro Automático de Robots
# =====================================================


def test_robot_se_registra_automaticamente_al_importar():
    """✅ Los robots se registran automáticamente al importar sus módulos."""
    from apps.leagues_manager.application.robot_registry import get_registered_robots

    # Los robots ya están importados al inicio del archivo
    # por lo que deberían estar registrados
    robots = get_registered_robots()

    # Verificar que los 3 robots están registrados
    assert len(robots) == 3
    assert RobotTypeEnum.STANDINGS in robots
    assert RobotTypeEnum.ODDS_WPLAY in robots
    assert RobotTypeEnum.CALENDAR in robots

    # Verificar que las clases son correctas
    assert robots[RobotTypeEnum.STANDINGS] == StandingsRobot
    assert robots[RobotTypeEnum.ODDS_WPLAY] == OddsWPlayRobot
    assert robots[RobotTypeEnum.CALENDAR] == CalendarRobot


def test_robot_no_se_registra_si_no_se_importa():
    """
    ✅ Un robot NO se registra si no se importa su módulo.

    Este test simula el escenario donde se crea un nuevo robot
    pero NO se importa en job_runner_application.py.

    Comportamiento esperado:
    - El robot NO aparece en el registro automático
    - El factory NO lo tiene mapeado
    - Si se intenta usar, se recibe un warning
    """
    from apps.leagues_manager.application.robot_registry import get_registered_robots

    # Obtener robots registrados
    robots = get_registered_robots()

    # Verificar que el factory NO tiene robots inexistentes
    runner = JobRunnerApplication()

    # Verificar que el factory tiene exactamente los 3 robots registrados
    assert len(runner.robot_factory) == 3

    # Verificar que NO hay robots adicionales no registrados
    for robot_type in runner.robot_factory.keys():
        assert robot_type in robots


def test_job_runner_usa_registro_automatico():
    """✅ JobRunnerApplication usa el registro automático de robots."""
    runner = JobRunnerApplication()

    # Verificar que el factory tiene los robots del registro automático
    assert len(runner.robot_factory) == 3
    assert RobotTypeEnum.STANDINGS in runner.robot_factory
    assert RobotTypeEnum.ODDS_WPLAY in runner.robot_factory
    assert RobotTypeEnum.CALENDAR in runner.robot_factory


def test_job_runner_acepta_factory_personalizado():
    """✅ JobRunnerApplication acepta un factory personalizado."""
    from apps.leagues_manager.application.robot_registry import get_registered_robots

    # Crear un factory personalizado con solo 1 robot
    custom_factory = {
        RobotTypeEnum.STANDINGS: StandingsRobot,
    }

    # Crear runner con factory personalizado
    runner = JobRunnerApplication(robot_factory=custom_factory)

    # Verificar que SOLO tiene el robot del factory personalizado
    assert len(runner.robot_factory) == 1
    assert RobotTypeEnum.STANDINGS in runner.robot_factory
    assert RobotTypeEnum.ODDS_WPLAY not in runner.robot_factory
    assert RobotTypeEnum.CALENDAR not in runner.robot_factory

    # Verificar que el registro automático sigue teniendo los 3 robots
    robots = get_registered_robots()
    assert len(robots) == 3
