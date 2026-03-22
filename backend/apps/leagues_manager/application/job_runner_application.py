from typing import TYPE_CHECKING, Dict, Type
from loguru import logger

from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum
from apps.leagues_manager.domain.robots.base_robot import BaseRobot
from apps.leagues_manager.infrastructure.models.sql.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion,
)
from apps.leagues_manager.infrastructure.models.sql.torneo import Torneo
from apps.leagues_manager.robots.standings_robot import StandingsRobot
from apps.leagues_manager.robots.odds_wplay_robot import OddsWPlayRobot
from apps.leagues_manager.robots.calendar_robot import CalendarRobot
from apps.leagues_manager.tests.mock_data_leagues import MockTorneo
from apps.leagues_manager.tests.mock_data_leagues import MockDetalleFuenteExtraccion
from shared.repositories.scheduler_repos.process_run_repository import (
    ProcessRunRepository,
)

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
        # Las claves ahora son los miembros del Enum
        self.robot_factory: Dict[RobotTypeEnum, Type[BaseRobot]] = (
            {  # <--- ¡CAMBIO DE TIPO EN EL DICCIONARIO!
                RobotTypeEnum.STANDINGS: StandingsRobot,  # <--- Usa el Enum
                RobotTypeEnum.ODDS_WPLAY: OddsWPlayRobot,  # <--- Usa el Enum
                RobotTypeEnum.CALENDAR: CalendarRobot,  # <--- Usa el Enum
                # ... aquí se añadirían nuevos robots, ej: RobotTypeEnum.ODDS_BETFAIR: BetfairRobot
            }
        )
        logger.trace("JobRunnerApplication inicializado con el mapeo de robots.")

    async def run_job(
        self,
        torneo: Torneo,
        detalle: DetalleFuenteExtraccion,
        run_id: str,
        repo: ProcessRunRepository,
    ):
        """
        Recibe un trabajo, encuentra el robot correcto, lo instancia y lo ejecuta.
        """
        if detalle.fuente is None or not hasattr(detalle.fuente, "type"):
            logger.warning(
                f"⚠️  'detalle.fuente' es None o no tiene atributo 'type' en '{torneo.nombre}'"
            )
            return

        # `detalle.fuente.type` ahora será un miembro de RobotTypeEnum,
        # que se puede usar directamente como clave.
        robot_type_enum_member = detalle.fuente.type
        robot_class = self.robot_factory.get(
            robot_type_enum_member
        )  # <--- Usar el miembro del Enum directamente

        if not robot_class:
            logger.warning(
                f"⚠️  No hay robot para tipo '{robot_type_enum_member.value}' en '{torneo.nombre}'"
            )
            return

        # Logging detallado: qué robot se ejecuta y para qué fuente
        fuente_name = (
            detalle.fuente.name if hasattr(detalle.fuente, "name") else "Sin nombre"
        )
        logger.info(
            f"🤖 Ejecutando robot: {robot_class.__name__} | "
            f"Fuente: '{fuente_name}' (tipo: {robot_type_enum_member.value}) | "
            f"Torneo: '{torneo.nombre}' | "
            f"Detalle ID: {detalle.id} | "
            f"process_id: {detalle.process_id}"
        )

        # --- PASAMOS repo al robot ---
        robot_instance = robot_class(torneo, detalle, run_id, repo)
        await robot_instance.run()

        logger.info(
            f"✅ Robot {robot_class.__name__} completado para fuente '{fuente_name}' en torneo '{torneo.nombre}'"
        )


# --- Punto de entrada para el Task (para mantenerlo simple) ---
# Creamos una única instancia del runner que será usada por el task.
job_runner = JobRunnerApplication()
