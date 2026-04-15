from typing import TYPE_CHECKING, Dict, Type, overload, cast
from loguru import logger
import warnings

from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum
from apps.leagues_manager.domain.robots.base_robot import BaseRobot
from apps.leagues_manager.domain.interfaces.job_runner_interfaces import (
    ITorneo,
    IDetalleFuenteExtraccion,
)
from shared.repositories.scheduler_repos import IProcessRunRepository

# ✅ Modelos SQL solo para chequeo de tipos, NO se importan en RUNTIME
# ✅ Cumplimiento 100% Clean Architecture: No hay dependencias en ejecucion
if TYPE_CHECKING:
    from apps.leagues_manager.infrastructure.models.sql.detalle_fuente_extraccion import (
        DetalleFuenteExtraccion,
    )
    from apps.leagues_manager.infrastructure.models.sql.torneo import Torneo

from apps.leagues_manager.tests.mock_data_leagues import MockTorneo
from apps.leagues_manager.tests.mock_data_leagues import MockDetalleFuenteExtraccion

# --- EXCEPCIONES PERSONALIZADAS ---
from core.exceptions import (
    FuenteNotFoundException,
    RobotNotFoundException,
)

# --- LOGGING MEJORADO ---
from core.robot_logging import (
    log_robot_start,
    log_robot_end,
    get_robot_emoji,
    LogSymbols,
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

    @overload
    async def run_job(
        self,
        torneo: Torneo,
        detalle: DetalleFuenteExtraccion,
        run_id: str,
        repo: IProcessRunRepository,
    ) -> None: ...

    @overload
    async def run_job(
        self,
        torneo: ITorneo,
        detalle: IDetalleFuenteExtraccion,
        run_id: str,
        repo: IProcessRunRepository,
    ) -> None: ...

    async def run_job(
        self,
        torneo: ITorneo | Torneo,
        detalle: IDetalleFuenteExtraccion | DetalleFuenteExtraccion,
        run_id: str,
        repo: IProcessRunRepository,
    ):
        """
        ✅ IMPLEMENTACION CLEAN ARCHITECTURE
        Recibe un trabajo, encuentra el robot correcto, lo instancia y lo ejecuta.

        Acepta tanto modelos SQL antiguos como nuevas entidades/implementaciones
        que cumplan con las interfaces ITorneo e IDetalleFuenteExtraccion.

        Retrocompatible 100% con codigo existente.
        """
        # Aviso deprecacion solo cuando se usan modelos SQL directamente
        if isinstance(torneo, Torneo) and isinstance(detalle, DetalleFuenteExtraccion):
            warnings.warn(
                "⚠️ DEPRECATED: Usar modelos SQL directamente en run_job() esta deprecado. "
                "Usar entidades de dominio o objetos que implementen ITorneo e IDetalleFuenteExtraccion.",
                DeprecationWarning,
                stacklevel=2,
            )
        if detalle.fuente is None or not hasattr(detalle.fuente, "type"):
            raise FuenteNotFoundException(detalle.id)

        # `detalle.fuente.type` ahora será un miembro de RobotTypeEnum,
        # que se puede usar directamente como clave.
        robot_type_enum_member = cast(RobotTypeEnum, detalle.fuente.type)
        robot_class = self.robot_factory.get(
            robot_type_enum_member
        )  # <--- Usar el miembro del Enum directamente

        if not robot_class:
            raise RobotNotFoundException(robot_type_enum_member.value)

        # Logging detallado: qué robot se ejecuta y para qué fuente
        fuente_name = (
            detalle.fuente.name if hasattr(detalle.fuente, "name") else "Sin nombre"
        )

        # Log de inicio con formato mejorado
        emoji = get_robot_emoji(robot_type_enum_member.value)
        short_run_id = run_id[:8]
        logger.info(
            f"\n"
            f"{'='*60}\n"
            f"{LogSymbols.START} INICIANDO EJECUCIÓN DE ROBOT\n"
            f"{'='*60}\n"
            f"  {emoji} Robot: {robot_class.__name__}\n"
            f"  {LogSymbols.RUN_ID} Run ID: {short_run_id}...\n"
            f"  {LogSymbols.TORNEO} Torneo: {torneo.nombre}\n"
            f"  {LogSymbols.FUENTE} Fuente: {fuente_name}\n"
            f"  📋 Tipo: {robot_type_enum_member.value}\n"
            f"  📋 Detalle ID: {detalle.id}\n"
            f"  📋 Process ID: {detalle.process_id}\n"
            f"{'='*60}"
        )

        # --- PASAMOS repo al robot ---
        robot_instance = robot_class(torneo, detalle, run_id, repo)
        await robot_instance.run()

        # Log de finalización con formato mejorado
        logger.info(
            f"\n"
            f"{'='*60}\n"
            f"{LogSymbols.SUCCESS} ROBOT COMPLETADO EXITOSAMENTE\n"
            f"{'='*60}\n"
            f"  {emoji} Robot: {robot_class.__name__}\n"
            f"  {LogSymbols.RUN_ID} Run ID: {short_run_id}...\n"
            f"  {LogSymbols.TORNEO} Torneo: {torneo.nombre}\n"
            f"  {LogSymbols.FUENTE} Fuente: {fuente_name}\n"
            f"{'='*60}\n"
        )


# --- Punto de entrada para el Task (para mantenerlo simple) ---
# NOTA: El singleton global se eliminó en Fase 2.
# Ahora se crea localmente donde se necesite:
# job_runner = JobRunnerApplication()  # Sin argumentos usa el factory por defecto
# job_runner = JobRunnerApplication(custom_factory)  # Con factory personalizado
