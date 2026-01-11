from typing import TYPE_CHECKING, Dict, Type
from loguru import logger

from apps.leagues_manager.domain.robots.base_robot import BaseRobot
from apps.leagues_manager.robots.standings_robot import StandingsRobot
from apps.leagues_manager.robots.odds_wplay_robot import OddsWPlayRobot
from apps.leagues_manager.robots.calendar_robot import CalendarRobot
from apps.leagues_manager.tests.mock_data_leagues import MockTorneo
from apps.leagues_manager.tests.mock_data_leagues import MockDetalleFuenteExtraccion

# ===================================================================
# EL RUNNER (FACTORY/STRATEGY PARA SELECCIONAR EL ROBOT)
# ===================================================================

class JobRunnerApplication:
    """
    Clase responsable de recibir un trabajo y ejecutarlo
    usando el robot adecuado.
    """
    def __init__(self):
        # --- MAPEO INTELIGENTE: Asocia un 'tipo' de fuente con una clase de Robot ---
        self.robot_factory: Dict[str, Type[BaseRobot]] = {
            "standings": StandingsRobot,
            "odds_wplay": OddsWPlayRobot,
            "calendar": CalendarRobot,
            # ... aquí se añadirían nuevos robots, ej: "odds_betfair": BetfairRobot
        }
        logger.trace("JobRunnerApplication inicializado con el mapeo de robots.")

    async def run_job(self, torneo: 'MockTorneo', detalle: 'MockDetalleFuenteExtraccion'):
        """
        Recibe un trabajo, encuentra el robot correcto, lo instancia y lo ejecuta.
        """
        robot_type = detalle.fuente.type
        
        # Busca la clase del robot en el factory
        robot_class = self.robot_factory.get(robot_type)

        if not robot_class:
            logger.warning(f"⚠️  No se encontró un robot para el tipo '{robot_type}' en el trabajo para '{torneo.name}'")
            return

        # Crea una instancia del robot específico y lo ejecuta
        robot_instance = robot_class(torneo, detalle)
        await robot_instance.run()

# --- Punto de entrada para el Task (para mantenerlo simple) ---
# Creamos una única instancia del runner que será usada por el task.
job_runner = JobRunnerApplication()