import argparse
import asyncio
from loguru import logger
from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
    launch_process_rastreo_data_fuentes_deportivas_task,
)
from shared.constants.process.process_codes import (
    PROCESS_CALENDAR_EXTRACTION,
    PROCESS_CUOTAS_WPLAY,
    PROCESS_ODDS_WPLAY_EXTRACTION,
    PROCESS_STANDINGS_EXTRACTION,
    SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS,
)
from core.logger import configure_logging

# Procesos disponibles que usan la misma función de tarea
AVAILABLE_PROCESSES = {
    SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS: launch_process_rastreo_data_fuentes_deportivas_task,
    PROCESS_STANDINGS_EXTRACTION: launch_process_rastreo_data_fuentes_deportivas_task,
    PROCESS_ODDS_WPLAY_EXTRACTION: launch_process_rastreo_data_fuentes_deportivas_task,
    PROCESS_CALENDAR_EXTRACTION: launch_process_rastreo_data_fuentes_deportivas_task,
}


if __name__ == "__main__":
    configure_logging()

    parser = argparse.ArgumentParser(description="Launcher de tareas programadas")
    parser.add_argument(
        "--process", required=True, help="Código del proceso a ejecutar"
    )
    args = parser.parse_args()

    task = AVAILABLE_PROCESSES.get(args.process)
    logger.info(f"Task: {task}")

    print(">>>>>>>>> task:_ " + str(task))

    if not task:
        logger.error(f"❌ Proceso '{args.process}' no reconocido.")
        logger.info(f"Procesos disponibles: {', '.join(AVAILABLE_PROCESSES.keys())}")
    else:
        logger.info(f"▶️ Ejecutando proceso: {args.process}")
        # Pasar el process_code específico a la función de tarea
        asyncio.run(task(process_code=args.process))
