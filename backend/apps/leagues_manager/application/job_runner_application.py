from typing import TYPE_CHECKING, Dict, Type
from loguru import logger

from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum
from apps.leagues_manager.domain.robots.base_robot import BaseRobot
from apps.leagues_manager.infrastructure.models.sql.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion,
)
from apps.leagues_manager.infrastructure.models.sql.torneo import Torneo
from apps.leagues_manager.tests.mock_data_leagues import MockTorneo
from apps.leagues_manager.tests.mock_data_leagues import MockDetalleFuenteExtraccion
from shared.repositories.scheduler_repos.process_run_repository import (
    ProcessRunRepository,
)

# --- EXCEPCIONES PERSONALIZADAS ---
from core.exceptions import (
    FuenteNotFoundException,
    RobotNotFoundException,
)

# ===================================================================
# IMPORTS DE ROBOTS (para que el decorador @register_robot se ejecute)
# ===================================================================
# Estos imports son necesarios para que los robots se registren automáticamente
# al importar este módulo. Sin estos imports, el decorador nunca se ejecutaría.
from apps.leagues_manager.robots.standings_robot import StandingsRobot  # noqa: F401
from apps.leagues_manager.robots.odds_wplay_robot import OddsWPlayRobot  # noqa: F401
from apps.leagues_manager.robots.calendar_robot import CalendarRobot  # noqa: F401

# ===================================================================
# REGISTRO AUTOMÁTICO DE ROBOTS (Patrón Decorador)
# ===================================================================
# Importar desde robot_registry.py para evitar importación circular
from apps.leagues_manager.application.robot_registry import (
    get_registered_robots,
)


# ===================================================================
# EL RUNNER (FACTORY/STRATEGY PARA SELECCIONAR EL ROBOT)
# ===================================================================


class JobRunnerApplication:
    """
    Clase responsable de recibir un trabajo y ejecutarlo
    usando el robot adecuado.
    """

    def __init__(
        self, robot_factory: Dict[RobotTypeEnum, Type[BaseRobot]] | None = None
    ):
        # --- MAPEO INTELIGENTE: Asocia un 'tipo' de fuente con una clase de Robot ---
        # Si se proporciona un factory, úsalo; de lo contrario, usa el factory por defecto
        self.robot_factory = robot_factory or self._default_factory()
        logger.trace("JobRunnerApplication inicializado con el mapeo de robots.")

    @staticmethod
    def _default_factory() -> Dict[RobotTypeEnum, Type[BaseRobot]]:
        """Retorna el factory por defecto con todos los robots registrados automáticamente."""
        # ✅ Usa el registro automático de robots
        # Los robots se registran con @register_robot al importar sus módulos
        return get_registered_robots()

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
            raise FuenteNotFoundException(detalle.id)

        # `detalle.fuente.type` ahora será un miembro de RobotTypeEnum,
        # que se puede usar directamente como clave.
        robot_type_enum_member = detalle.fuente.type
        robot_class = self.robot_factory.get(
            robot_type_enum_member
        )  # <--- Usar el miembro del Enum directamente

        if not robot_class:
            raise RobotNotFoundException(robot_type_enum_member.value)

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
# NOTA: El singleton global se eliminó en Fase 2.
# Ahora se crea localmente donde se necesite:
# job_runner = JobRunnerApplication()  # Sin argumentos usa el factory por defecto
# job_runner = JobRunnerApplication(custom_factory)  # Con factory personalizado
