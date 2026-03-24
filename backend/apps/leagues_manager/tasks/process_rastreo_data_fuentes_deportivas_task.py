import asyncio
import json
import uuid
from datetime import datetime
from typing import cast
from loguru import logger
from apps.leagues_manager.infrastructure.models.sql.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion,
)
from apps.leagues_manager.infrastructure.models.sql.torneo import Torneo
from apps.leagues_manager.infrastructure.repositories.sql_platform_repository import (
    SqlPlatformRepository,
)
from apps.platform_config.infrastructure.repositories.sql_platform_config_repository import (
    SQLPlatformConfigRepository,
)
from core.config import settings
from core.db.sql.database_sql import SessionLocal
from shared.constants.process.process_codes import (
    SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS,
)
from shared.repositories.scheduler_repos.process_run_repository import (
    ProcessRunRepository,
)

# --- CAMBIO CLAVE: Importamos la CLASE JobRunner (no el singleton) ---
from apps.leagues_manager.application.job_runner_application import (
    JobRunnerApplication,
)
from apps.leagues_manager.tasks.utils import generate_run_id

# --- EXCEPCIONES PERSONALIZADAS ---
from core.exceptions import (
    ProcessNotFoundException,
    ProcessInactiveException,
    ProcessRunCreationException,
    NoActiveJobsException,
)

# --- CONFIGURACIÓN DE SEMÁFOROS DIFERENCIADOS ---
from core.config_semaphore import get_concurrency_for_robot_type
from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum

# --- LOGGING MEJORADO ---
from core.robot_logging import (
    LogSymbols,
    get_robot_emoji,
    log_semaphore_status,
)


def _build_jobs_from_leagues(
    leagues, target_process_id: int | None = None, is_general_orchestrator: bool = False
):
    """
    Filtra y construye la estructura de trabajos a partir de las ligas,
    filtrando opcionalmente por un process_id de DetalleFuenteExtraccion.

    Args:
        leagues: Lista de ligas con sus torneos y detalles de fuente
        target_process_id: Opcional, ID del proceso para filtrar los detalles de fuente.
        is_general_orchestrator: Si es True, ejecuta todos los trabajos sin filtrar por process_id.

    Returns:
        tuple: (flat_jobs_for_execution, grouped_jobs_for_display)
            - flat_jobs_for_execution: Lista plana de tuplas (torneo, detalle) para ejecución
            - grouped_jobs_for_display: Lista de diccionarios agrupados por torneo para visualización
    """
    flat_jobs_for_execution = []
    torneo_map_for_display = {}

    logger.info(f"📊 Ligas cargadas: {len(leagues)}")
    for league in leagues:
        if not league.is_active:
            logger.debug(f"   ⏭️  Liga inactiva: {league.nombre}")
            continue

        logger.info(f"   🏟️  Liga activa: {league.nombre} (ID: {league.id})")

        for torneo in league.torneos:
            if not torneo.is_active:
                logger.debug(f"      ⏭️  Torneo inactivo: {torneo.nombre}")
                continue

            # Prepara la entrada del torneo para la visualización si no existe
            if torneo.id not in torneo_map_for_display:
                torneo_map_for_display[torneo.id] = {
                    "id": torneo.id,
                    "nombre": torneo.nombre,
                    "fuentes": [],
                }

            logger.info(f"      🏆 Torneo activo: {torneo.nombre} (ID: {torneo.id})")
            logger.info(
                f"         📄 Detalles de fuente encontrados: {len(torneo.detalles_fuente)}"
            )

            for detalle in torneo.detalles_fuente:
                fuente_name = detalle.fuente.name if detalle.fuente else "Sin fuente"
                logger.debug(
                    f"         📋 Detalle ID={detalle.id} | Fuente: {fuente_name} | "
                    f"is_active={detalle.is_active} | process_id={detalle.process_id} | "
                    f"target_process_id={target_process_id}"
                )

                if detalle.is_active and detalle.fuente and detalle.fuente.is_active:
                    # --- Lógica de filtrado por process_id ---
                    # Si es el orquestador general, ejecutar TODOS los trabajos
                    # Si es un proceso específico, filtrar solo los que coincidan
                    if not is_general_orchestrator and target_process_id is not None:
                        if detalle.process_id != target_process_id:
                            logger.debug(
                                f"            ❌ FILTRADO: process_id={detalle.process_id} != target={target_process_id}"
                            )
                            continue  # Saltar este detalle si no coincide con el process_id objetivo
                        else:
                            logger.info(
                                f"            ✅ MATCH: process_id={detalle.process_id} == target={target_process_id}"
                            )
                    else:
                        logger.info(
                            f"            ✅ ORQUESTADOR GENERAL: Incluyendo todos los trabajos"
                        )

                    # Añadir a la lista plana para la ejecución
                    flat_jobs_for_execution.append((torneo, detalle))

                    # Añadir a la estructura agrupada para la visualización
                    torneo_map_for_display[torneo.id]["fuentes"].append(
                        {"type": detalle.fuente.type, "url": detalle.url}
                    )
                else:
                    logger.debug(
                        f"            ⏭️  Saltado: is_active={detalle.is_active}, tiene_fuente={detalle.fuente is not None}"
                    )

    # Convertir el mapa a la lista final de torneos para la visualización
    grouped_jobs_for_display = list(torneo_map_for_display.values())

    logger.info(
        f"📊 Resumen: {len(flat_jobs_for_execution)} trabajos seleccionados de {len(leagues)} ligas"
    )

    return flat_jobs_for_execution, grouped_jobs_for_display


async def launch_process_rastreo_data_fuentes_deportivas_task(
    process_code: str = SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS,
):  # ¡NUEVO PARÁMETRO CON DEFAULT!
    """
    Orquesta el proceso de rastreo. Genera una lista de todos los trabajos
    de extracción individuales y los ejecuta de forma concurrente,
    filtrando por un código de proceso específico.

    Args:
        process_code: El código del proceso que debe orquestar esta ejecución.
                      Por defecto, usa el orquestador general.
    """
    run_id = generate_run_id()
    short_run_id = run_id[:8]

    # Log de inicio mejorado con formato visual
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

    # ✅ FASE 4: Semáforos diferenciados por tipo de robot
    # Crear un semáforo global como fallback
    global_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_CLIENTS)

    # Diccionario para almacenar semáforos por tipo de robot
    semaphores_by_type: dict[str, asyncio.Semaphore] = {}

    def get_semaphore_for_robot_type(robot_type: str) -> asyncio.Semaphore:
        """
        Retorna el semáforo apropiado para un tipo de robot específico.
        Si no hay configuración específica, usa el semáforo global.
        """
        if robot_type not in semaphores_by_type:
            # Obtener concurrencia específica para este tipo de robot
            # Convertir string a RobotTypeEnum
            try:
                robot_enum = RobotTypeEnum(robot_type)
                concurrency = get_concurrency_for_robot_type(robot_enum)
            except ValueError:
                # Si el tipo no existe en el enum, usar concurrencia global
                concurrency = settings.MAX_CONCURRENT_CLIENTS
                logger.warning(
                    f"⚠️ Tipo de robot '{robot_type}' no encontrado en enum, usando concurrencia global"
                )
            semaphores_by_type[robot_type] = asyncio.Semaphore(concurrency)
            logger.info(
                f"🔧 Semáforo creado para tipo '{robot_type}': {concurrency} concurrencia máxima"
            )
        return semaphores_by_type[robot_type]

    # ✅ Crear instancia local de JobRunner (Fase 2: Inyección de dependencias)
    job_runner = JobRunnerApplication()

    with SessionLocal() as session:
        # --- CONECTAR ProcessRunRepository ---
        repo = ProcessRunRepository(db=session)

        # PRIMERO: Verificar si el proceso existe y está activo ANTES de crear el ProcessRun
        platform_config_repo = SQLPlatformConfigRepository(session)
        process_entity = platform_config_repo.get_process_by_code(process_code)
        if not process_entity:
            raise ProcessNotFoundException(process_code)

        # Validar si el proceso está activo
        is_active: bool = cast(bool, process_entity.is_active)
        if not is_active:
            raise ProcessInactiveException(process_code, cast(int, process_entity.id))

        logger.info(
            f"✅ Proceso '{process_code}' está ACTIVO (is_active=True). Procediendo con la ejecución..."
        )

        # SOLO crear ProcessRun si el proceso está activo
        run = repo.create_run(run_id, process_code)
        if not run:
            raise ProcessRunCreationException(process_code, run_id)

        target_process_id: int | None = cast(
            int, process_entity.id
        )  # Este es el ID que usaremos para filtrar

        # Verificar si es el orquestador general (debe ejecutar TODOS los trabajos)
        is_general_orchestrator = (
            process_code == SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS
        )

        # Obtener todas las ligas (la filtración por process_id se hará en _build_jobs_from_leagues)
        leagues = SqlPlatformRepository(session).get_all_leagues_with_full_details()

        logger.info("🔍 Generando lista de trabajos...")
        flat_jobs_for_execution, grouped_jobs_for_display = _build_jobs_from_leagues(
            leagues, target_process_id, is_general_orchestrator
        )

        if not flat_jobs_for_execution:
            repo.complete_run(run_id)
            raise NoActiveJobsException(process_code)

        # Resumen de fuentes por tipo
        fuentes_por_tipo = {}
        for torneo, detalle in flat_jobs_for_execution:
            if detalle.fuente and hasattr(detalle.fuente, "type"):
                tipo = (
                    detalle.fuente.type.value
                    if hasattr(detalle.fuente.type, "value")
                    else str(detalle.fuente.type)
                )
                if tipo not in fuentes_por_tipo:
                    fuentes_por_tipo[tipo] = 0
                fuentes_por_tipo[tipo] += 1

        logger.info(
            f"⚙️  {len(flat_jobs_for_execution)} trabajos listos para proceso '{process_code}'. Concurrencia: {settings.MAX_CONCURRENT_CLIENTS}"
        )
        logger.info(f"📊 Distribución de fuentes por tipo: {fuentes_por_tipo}")

        logger.info(">>>>>>>>>>>>>>>>>>>>>> JOBS (AGRUPADOS):")
        logger.info(
            json.dumps(
                {"torneos": grouped_jobs_for_display}, indent=2, ensure_ascii=False
            )
        )

        async def run_job_with_semaphore_wrapper(
            torneo: Torneo, detalle: DetalleFuenteExtraccion
        ):
            """
            Wrapper que adquiere el semáforo y delega la ejecución de UN trabajo al runner.
            """
            fuente_name = (
                detalle.fuente.name if detalle.fuente is not None else "Sin fuente"
            )
            job_info = f"Trabajo para '{torneo.nombre}' (Fuente: {fuente_name})"

            # Obtener el tipo de robot para este detalle
            robot_type = (
                detalle.fuente.type.value
                if hasattr(detalle.fuente.type, "value")
                else str(detalle.fuente.type)
            )

            # Obtener el semáforo específico para este tipo de robot
            semaphore = get_semaphore_for_robot_type(robot_type)

            if semaphore.locked():
                logger.info(
                    f"⏳ Cliente en espera: {job_info} (esperando cupo disponible...)"
                )

            async with semaphore:
                await job_runner.run_job(torneo, detalle, run_id, repo)

        tasks = [
            run_job_with_semaphore_wrapper(torneo, detalle)
            for torneo, detalle in flat_jobs_for_execution
        ]

        try:
            await asyncio.gather(*tasks)
            repo.complete_run(run_id)

            # Log de finalización exitosa con formato mejorado
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

            # Log de error con formato mejorado
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
