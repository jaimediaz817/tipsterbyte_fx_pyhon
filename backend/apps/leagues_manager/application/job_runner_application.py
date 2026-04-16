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

    async def run_full_orchestrator(
        self,
        process_code: str,
        platform_repo=None,
        process_run_repo=None,
        league_repo=None,
    ):
        """
        ✅ METODO UNICO DE ORQUESTACION
        ✅ TODA LA LOGICA AQUI. UNA SOLA VEZ.
        ✅ Esta es la UNICA fuente de verdad de toda la orquestacion
        ✅ Las Tasks SOLO llaman a este metodo. Nada mas.
        """
        from apps.leagues_manager.tasks.utils import generate_run_id
        from core.db.sql.database_sql import SessionLocal
        from apps.platform_config.infrastructure.repositories.sql_platform_config_repository import (
            SQLPlatformConfigRepository,
        )
        from apps.leagues_manager.infrastructure.repositories.sql_platform_repository import (
            SqlPlatformRepository,
        )
        from shared.repositories.scheduler_repos import ProcessRunRepositoryFactory
        from core.config_semaphore import get_semaphore_for_robot_type
        from core.exceptions import (
            ProcessNotFoundException,
            ProcessInactiveException,
            ProcessRunCreationException,
            NoActiveJobsException,
        )
        import asyncio
        from datetime import datetime

        run_id = generate_run_id()
        short_run_id = run_id[:8]

        logger.info(
            f"\n"
            f"{'='*70}\n"
            f"{LogSymbols.START} INICIANDO ORQUESTADOR DE PROCESO\n"
            f"{'='*70}\n"
            f"  {LogSymbols.RUN_ID} Run ID: {short_run_id}...\n"
            f"  📋 Process Code: {process_code}\n"
            f"  {LogSymbols.TIME} Timestamp: {datetime.now().isoformat()}\n"
            f"{'='*70}"
        )

        with SessionLocal() as session:
            repo = process_run_repo or ProcessRunRepositoryFactory.get_repository(
                db=session
            )
            platform_config_repo = platform_repo or SQLPlatformConfigRepository(session)

            process_entity = platform_config_repo.get_process_by_code(process_code)
            if not process_entity:
                raise ProcessNotFoundException(process_code)

            is_active: bool = cast(bool, process_entity.is_active)
            if not bool(is_active):
                raise ProcessInactiveException(
                    process_code, cast(int, process_entity.id)
                )

            logger.info(f"✅ Proceso '{process_code}' esta ACTIVO. Procediendo...")

            run = repo.create_run(run_id, process_code)
            if not run:
                raise ProcessRunCreationException(process_code, run_id)

            target_process_id: int | None = cast(int, process_entity.id)
            is_general_orchestrator = process_code == "PROCESS_EXTRACT_DATA_FUENTES"

            leagues = league_repo or SqlPlatformRepository(session)
            leagues = leagues.get_all_leagues_with_full_details()

            logger.info("🔍 Generando lista de trabajos...")

            # ✅ Logica de construccion de jobs aqui (la movemos desde la Task)
            flat_jobs_for_execution = []
            torneo_map_for_display = {}

            for league in leagues:
                if not cast(bool, league.is_active):
                    continue
                for torneo in league.torneos:
                    if not cast(bool, torneo.is_active):
                        continue
                    for detalle in torneo.detalles_fuente:
                        if (
                            cast(bool, detalle.is_active)
                            and detalle.fuente
                            and cast(bool, detalle.fuente.is_active)
                        ):
                            if (
                                not is_general_orchestrator
                                and target_process_id is not None
                            ):
                                if detalle.process_id != target_process_id:
                                    continue
                            flat_jobs_for_execution.append((torneo, detalle))

            if not flat_jobs_for_execution:
                repo.complete_run(run_id)
                raise NoActiveJobsException(process_code)

            logger.info(
                f"⚙️  {len(flat_jobs_for_execution)} trabajos listos para proceso '{process_code}'"
            )

            async def run_job_with_semaphore_wrapper(torneo, detalle):
                robot_type = detalle.fuente.type
                try:
                    robot_enum = RobotTypeEnum(robot_type)
                    semaphore = get_semaphore_for_robot_type(robot_enum)
                except ValueError:
                    semaphore = get_semaphore_for_robot_type(RobotTypeEnum.STANDINGS)

                async with semaphore:
                    await self.run_job(torneo, detalle, run_id, repo)

            tasks = [
                run_job_with_semaphore_wrapper(torneo, detalle)
                for torneo, detalle in flat_jobs_for_execution
            ]

            try:
                await asyncio.gather(*tasks)
                repo.complete_run(run_id)

                logger.success(
                    f"\n"
                    f"{'='*70}\n"
                    f"{LogSymbols.SUCCESS} ORQUESTADOR COMPLETADO EXITOSAMENTE\n"
                    f"{'='*70}\n"
                    f"  {LogSymbols.RUN_ID} Run ID: {short_run_id}...\n"
                    f"  📋 Process Code: {process_code}\n"
                    f"  ✅ Trabajos ejecutados: {len(flat_jobs_for_execution)}\n"
                    f"  {LogSymbols.TIME} Finalizado: {datetime.now().isoformat()}\n"
                    f"{'='*70}\n"
                )
            except Exception as e:
                repo.fail_run(run_id)
                logger.error(
                    f"\n"
                    f"{'='*70}\n"
                    f"{LogSymbols.ERROR} ORQUESTADOR FALLÓ\n"
                    f"{'='*70}\n"
                    f"  {LogSymbols.RUN_ID} Run ID: {short_run_id}...\n"
                    f"  📋 Process Code: {process_code}\n"
                    f"  {LogSymbols.ERROR} Error: {e}\n"
                    f"  {LogSymbols.TIME} Falló: {datetime.now().isoformat()}\n"
                    f"{'='*70}\n"
                )
                raise


# --- Punto de entrada para el Task (para mantenerlo simple) ---
# NOTA: El singleton global se eliminó en Fase 2.
# Ahora se crea localmente donde se necesite:
# job_runner = JobRunnerApplication()  # Sin argumentos usa el factory por defecto
# job_runner = JobRunnerApplication(custom_factory)  # Con factory personalizado
