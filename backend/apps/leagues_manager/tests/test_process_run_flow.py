import pytest
from datetime import datetime

# from apps.leagues_manager.robots.odds_wplay_robot import OddsWPlayRobot
# from apps.leagues_manager.tests.mock_data_leagues import (
#     MockTorneo,
#     MockDetalleFuenteExtraccion,
#     MockFuenteExtraccion,
# )
from apps.leagues_manager.robots.standings_robot import StandingsRobot
from apps.leagues_manager.tests.mock_data_leagues import (
    MockDetalleFuenteExtraccion,
    MockFuenteExtraccion,
    MockTorneo,
)
from apps.leagues_manager.robots.odds_wplay_robot import OddsWPlayRobot


# =====================================================
# MOCK REPOSITORY (sin BD)
# =====================================================
class MockProcessRunRepository:
    def __init__(self):
        self.runs: dict = {}
        self.logs: list = []

    def create_run(self, run_id: str, process_code: str):
        self.runs[run_id] = {
            "run_id": run_id,
            "process_code": process_code,
            "status": "in_progress",
            "started_at": datetime.now(),
            "ended_at": None,
        }
        return self.runs[run_id]

    def write_log(
        self,
        run_id,
        step,
        level,
        message,
        detalle_fuente_extraccion_id=None,
        input=None,
        output=None,
    ):
        self.logs.append(
            {
                "run_id": run_id,
                "step": step,
                "level": level,
                "message": message,
                "detalle_fuente_extraccion_id": detalle_fuente_extraccion_id,
                "input": input,
                "output": output,
                "timestamp": datetime.now(),
            }
        )

    def complete_run(self, run_id: str):
        if run_id in self.runs:
            self.runs[run_id]["status"] = "success"
            self.runs[run_id]["ended_at"] = datetime.now()

    def fail_run(self, run_id: str):
        if run_id in self.runs:
            self.runs[run_id]["status"] = "failed"
            self.runs[run_id]["ended_at"] = datetime.now()

    # --- Helpers para assertions ---
    def get_logs_by_step(self, step: str) -> list:
        return [l for l in self.logs if l["step"] == step]

    def get_logs_by_detalle_id(self, detalle_id: int) -> list:
        return [l for l in self.logs if l["detalle_fuente_extraccion_id"] == detalle_id]

    def get_logs_by_run_id(self, run_id: str) -> list:
        return [l for l in self.logs if l["run_id"] == run_id]


# =====================================================
# FIXTURES
# =====================================================
@pytest.fixture
def mock_repo():
    return MockProcessRunRepository()


@pytest.fixture
def mock_standings_detalle():
    fuente = MockFuenteExtraccion(id=1, name="Standings (SofaScore)", type="standings")
    return MockDetalleFuenteExtraccion(
        id=10,
        torneo_id=1,
        fuente_id=1,
        url="https://sofascore.com/laliga",
        is_active=True,
        fuente=fuente,
    )


@pytest.fixture
def mock_odds_detalle():
    fuente = MockFuenteExtraccion(id=2, name="Odds (WPlay)", type="odds_wplay")
    return MockDetalleFuenteExtraccion(
        id=20,
        torneo_id=1,
        fuente_id=2,
        url="https://wplay.co/laliga",
        is_active=True,
        fuente=fuente,
    )


@pytest.fixture
def mock_torneo():
    return MockTorneo(id=1, nombre="LaLiga 2025-2026", is_active=True)


# =====================================================
# TESTS
# =====================================================
@pytest.mark.asyncio
async def test_standings_robot_escribe_logs_start_y_end(
    mock_repo, mock_torneo, mock_standings_detalle
):
    """✅ El StandingsRobot debe escribir logs START y END correctamente."""
    run_id = "runid_test_standings_001"
    robot = StandingsRobot(mock_torneo, mock_standings_detalle, run_id, mock_repo)

    await robot.run()

    # ¿Escribió START?
    start_logs = mock_repo.get_logs_by_step("START")
    assert len(start_logs) == 1, "Debe haber exactamente 1 log de START"
    assert start_logs[0]["run_id"] == run_id
    assert start_logs[0]["detalle_fuente_extraccion_id"] == 10

    # ¿Escribió END?
    end_logs = mock_repo.get_logs_by_step("END")
    assert len(end_logs) == 1, "Debe haber exactamente 1 log de END"

    # ¿No hubo errores?
    error_logs = mock_repo.get_logs_by_step("ERROR")
    assert len(error_logs) == 0, "No debe haber logs de ERROR"


@pytest.mark.asyncio
async def test_run_id_propagado_correctamente_en_logs(
    mock_repo, mock_torneo, mock_standings_detalle
):
    """✅ Todos los logs deben contener el run_id correcto."""
    run_id = "runid_test_propagacion_002"
    robot = StandingsRobot(mock_torneo, mock_standings_detalle, run_id, mock_repo)

    await robot.run()

    todos_los_logs = mock_repo.get_logs_by_run_id(run_id)
    assert len(todos_los_logs) > 0, "Debe haber al menos un log"
    for log in todos_los_logs:
        assert log["run_id"] == run_id, f"Log con run_id incorrecto: {log}"


@pytest.mark.asyncio
async def test_detalle_id_diferente_por_robot(
    mock_repo, mock_torneo, mock_standings_detalle, mock_odds_detalle
):
    """✅ Robots distintos deben escribir logs con detalle_id distintos."""
    run_id = "runid_test_multi_robot_003"

    robot_standings = StandingsRobot(
        mock_torneo, mock_standings_detalle, run_id, mock_repo
    )
    robot_odds = OddsWPlayRobot(mock_torneo, mock_odds_detalle, run_id, mock_repo)

    await robot_standings.run()
    await robot_odds.run()

    logs_standings = mock_repo.get_logs_by_detalle_id(10)
    logs_odds = mock_repo.get_logs_by_detalle_id(20)

    assert len(logs_standings) > 0, "Debe haber logs para detalle_id=10 (Standings)"
    assert len(logs_odds) > 0, "Debe haber logs para detalle_id=20 (Odds)"

    # ¿Los IDs no se mezclan?
    for log in logs_standings:
        assert log["detalle_fuente_extraccion_id"] == 10
    for log in logs_odds:
        assert log["detalle_fuente_extraccion_id"] == 20
