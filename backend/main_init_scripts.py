import argparse
import asyncio
from loguru import logger
from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
    launch_process_rastreo_data_fuentes_deportivas_task,
)
from shared.constants.process.process_codes import SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS
from core.logger import configure_logging

AVAILABLE_PROCESSES = {
    SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS: launch_process_rastreo_data_fuentes_deportivas_task,
    # "proceso_otros_distintos...": proceso_otros_distintos_task,
}

if __name__ == "__main__":
    configure_logging()

    parser = argparse.ArgumentParser(description="Launcher de tareas programadas")
    parser.add_argument("--process", required=True, help="Código del proceso a ejecutar")
    args = parser.parse_args()

    task = AVAILABLE_PROCESSES.get(args.process)
    logger.info(f"Task: {task}")

    if not task:
        logger.error(f"❌ Proceso '{args.process}' no reconocido.")
        logger.info(f"Procesos disponibles: {', '.join(AVAILABLE_PROCESSES.keys())}")
    else:
        logger.info(f"▶️ Ejecutando proceso: {args.process}")
        asyncio.run(task())
        