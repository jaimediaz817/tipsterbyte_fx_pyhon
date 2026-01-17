# from apps.cartera_sura.tasks.cruce_cartera_task import launch_cruce_cartera_task
import asyncio
import logging

from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import launch_process_rastreo_data_fuentes_deportivas_task
from shared.constants.process.process_codes import SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS

logger = logging.getLogger(__name__)

def process_rastreo_data_fuentes_deportivas_job():
    """
    Tarea programada para ejecutar el proceso de rastreo de datos de fuentes deportivas.
    Esta función se registra en el scheduler central mediante el PROCESS_MAP.
    Returns:
        None
    """
    try:
        logger.info("🚀 Ejecutando tarea programada: process_rastreo_data_fuentes_deportivas_job")
        # Lanzar la tarea asíncrona
        asyncio.run(launch_process_rastreo_data_fuentes_deportivas_task())
    except Exception as e:
        logger.exception(f"❌ Error ejecutando process_rastreo_data_fuentes_deportivas_job: {e}")

# TODO: pregunta: esto se puede unificar para todas las apps?
# Mapa de procesos programables asociados a este paquete

# TODO: pendiente debatir: process_rastreo_data_fuentes_deportivas <- ¿debe quedar así?
PROCESS_MAP = {
    SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS: process_rastreo_data_fuentes_deportivas_job,
}
