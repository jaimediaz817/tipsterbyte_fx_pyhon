# from apps.cartera_sura.tasks.cruce_cartera_task import launch_cruce_cartera_task
import asyncio
import logging

from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
    launch_process_rastreo_data_fuentes_deportivas_task,
)
from shared.constants.process.process_codes import (
    SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS,
    PROCESS_STANDINGS_EXTRACTION,  # ¡NUEVA IMPORTACIÓN!
    PROCESS_ODDS_WPLAY_EXTRACTION,  # ¡NUEVA IMPORTACIÓN!
    PROCESS_CALENDAR_EXTRACTION,  # ¡NUEVA IMPORTACIÓN!
)

logger = logging.getLogger(__name__)


def process_rastreo_data_fuentes_deportivas_general_job():  # Renombrado para más claridad
    """
    Tarea programada para ejecutar el proceso de rastreo de datos de fuentes deportivas (GENERAL).
    """
    try:
        logger.info(f"🚀 Ejecutando tarea programada: Orquestador General")
        asyncio.run(
            launch_process_rastreo_data_fuentes_deportivas_task(
                process_code=SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS  # Pasar el código
            )
        )
    except Exception as e:
        logger.exception(f"❌ Error ejecutando Orquestador General: {e}")


def process_standings_job():  # ¡NUEVA FUNCIÓN DE TAREA!
    """
    Tarea programada para ejecutar la extracción de tablas de posiciones.
    """
    try:
        logger.info(
            f"🚀 Ejecutando tarea programada: Extracción de Tablas de Posiciones"
        )
        asyncio.run(
            launch_process_rastreo_data_fuentes_deportivas_task(
                process_code=PROCESS_STANDINGS_EXTRACTION  # Pasar el código específico
            )
        )
    except Exception as e:
        logger.exception(f"❌ Error ejecutando Extracción de Tablas de Posiciones: {e}")


def process_odds_wplay_job():  # ¡NUEVA FUNCIÓN DE TAREA!
    """
    Tarea programada para ejecutar la extracción de cuotas de WPlay.
    """
    try:
        logger.info(f"🚀 Ejecutando tarea programada: Extracción de Cuotas WPlay")
        asyncio.run(
            launch_process_rastreo_data_fuentes_deportivas_task(
                process_code=PROCESS_ODDS_WPLAY_EXTRACTION  # Pasar el código específico
            )
        )
    except Exception as e:
        logger.exception(f"❌ Error ejecutando Extracción de Cuotas WPlay: {e}")


def process_calendar_job():  # ¡NUEVA FUNCIÓN DE TAREA!
    """
    Tarea programada para ejecutar la extracción de calendarios de torneos.
    """
    try:
        logger.info(f"🚀 Ejecutando tarea programada: Extracción de Calendarios")
        asyncio.run(
            launch_process_rastreo_data_fuentes_deportivas_task(
                process_code=PROCESS_CALENDAR_EXTRACTION  # Pasar el código específico
            )
        )
    except Exception as e:
        logger.exception(f"❌ Error ejecutando Extracción de Calendarios: {e}")


# Mapa de procesos programables asociados a este paquete
PROCESS_MAP = {
    # Mapea el proceso general a su función
    SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS: process_rastreo_data_fuentes_deportivas_general_job,
    # Mapea los nuevos procesos específicos a sus funciones
    PROCESS_STANDINGS_EXTRACTION: process_standings_job,
    PROCESS_ODDS_WPLAY_EXTRACTION: process_odds_wplay_job,
    PROCESS_CALENDAR_EXTRACTION: process_calendar_job,
}
