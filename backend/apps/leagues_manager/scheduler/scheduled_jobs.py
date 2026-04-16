# from apps.cartera_sura.tasks.cruce_cartera_task import launch_cruce_cartera_task
import asyncio
import logging

from typing import cast, Awaitable
from core.scheduler.job_registry import register_job
from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
    launch_process_rastreo_data_fuentes_deportivas_task,
)
from shared.constants.process.process_codes import (
    PROCESS_EXTRACT_DATA_FUENTES,
    PROCESS_STANDINGS_EXTRACTION,
    PROCESS_ODDS_WPLAY_EXTRACTION,
    PROCESS_CALENDAR_EXTRACTION,
)

logger = logging.getLogger(__name__)


def create_job_function(process_code: str):
    """
    Factory que crea funciones de job dinámicamente.
    Elimina la duplicación de código al generar funciones idénticas
    que solo difieren en el process_code.
    """

    async def job_function():
        try:
            logger.info(f"🚀 Ejecutando tarea programada: {process_code}")
            await cast(
                Awaitable[None],
                launch_process_rastreo_data_fuentes_deportivas_task(
                    process_code=process_code
                ),
            )
        except Exception as e:
            logger.exception(f"❌ Error ejecutando {process_code}: {e}")

    return job_function


# Mapa de procesos programables asociados a este paquete
PROCESS_MAP = {
    PROCESS_EXTRACT_DATA_FUENTES: create_job_function(PROCESS_EXTRACT_DATA_FUENTES),
    PROCESS_STANDINGS_EXTRACTION: create_job_function(PROCESS_STANDINGS_EXTRACTION),
    PROCESS_ODDS_WPLAY_EXTRACTION: create_job_function(PROCESS_ODDS_WPLAY_EXTRACTION),
    PROCESS_CALENDAR_EXTRACTION: create_job_function(PROCESS_CALENDAR_EXTRACTION),
}

# ✅ REGISTRO AUTOMATICO EN EL SCHEDULER CENTRAL
# Los jobs se registran automaticamente al importar este modulo
# El core no necesita saber nada de esta aplicacion
for nombre_job, funcion_job in PROCESS_MAP.items():
    register_job(nombre_job)(funcion_job)

logger.debug(
    f"✅ Registrados {len(PROCESS_MAP)} jobs de leagues_manager automaticamente"
)
