import importlib
import inspect
from pathlib import Path
from loguru import logger

from scripts.db.seeders.base_seeder import BaseSeeder
from core.db.sql.database_sql import get_db_context
from core.logger import configure_logging

# from base_seeder import BaseSeeder


def run_seeders(specific_seeder: str | None = None, update_existing: bool = False):
    """
    Descubre y ejecuta dinámicamente todos los seeders SQL o uno específico.
    """
    configure_logging()

    if update_existing:
        logger.warning(
            "🔥 Modo de actualización activado. Los registros existentes se sobrescribirán."
        )

    logger.info("🚀 Iniciando orquestador de seeders SQL...")

    seeder_dir = Path(__file__).parent / "sql"
    all_seeder_classes = []

    # Descubrir todas las clases de seeder
    for file in seeder_dir.glob("*_seeder.py"):
        module_name = f"scripts.db.seeders.sql.{file.stem}"

        print(f"🔍 Descubriendo seeder en módulo: {module_name}")
        try:
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseSeeder) and obj is not BaseSeeder:
                    all_seeder_classes.append(obj)
        except ImportError as e:
            logger.error(f"No se pudo importar el módulo de seeder {module_name}: {e}")

    # Ordenar seeders para asegurar dependencias correctas
    # platform_config_seeder debe ejecutarse primero porque leagues_manager depende de él
    # geografia_seeder debe ejecutarse antes de leagues_manager_seeder porque crea los países/continentes
    def get_seeder_priority(seeder_class):
        name = seeder_class.__name__.lower()
        if "platform_config" in name:
            return 0  # Primero
        elif "auth" in name:
            return 1  # Segundo
        elif "geografia" in name:
            return 2  # Tercero (crea países y continentes)
        elif "leagues_manager" in name:
            return 3  # Cuarto (depende de platform_config y geografia)
        else:
            return 4  # Otros

    all_seeder_classes.sort(key=get_seeder_priority)

    if not all_seeder_classes:
        logger.warning("No se encontraron clases de seeder para ejecutar.")
        return

    seeders_to_run = []
    if specific_seeder:
        # Ejecutar un seeder específico
        seeder_name_lower = specific_seeder.lower()
        found_seeder = next(
            (
                cls
                for cls in all_seeder_classes
                if cls.__name__.lower() == seeder_name_lower
            ),
            None,
        )
        if found_seeder:
            seeders_to_run.append(found_seeder)
        else:
            logger.error(f"Seeder específico '{specific_seeder}' no encontrado.")
            logger.info(
                f"Seeders disponibles: {[cls.__name__ for cls in all_seeder_classes]}"
            )
            return
    else:
        # Ejecutar todos los seeders
        seeders_to_run = all_seeder_classes

    # Ejecutar los seeders seleccionados
    with get_db_context() as db:
        for seeder_class in seeders_to_run:
            try:
                seeder_instance = seeder_class(db)
                seeder_instance.run(update=update_existing)
            except Exception as e:
                logger.error(f"Falló la ejecución de {seeder_class.__name__}: {e}")
                # La transacción se revierte gracias al context manager get_db_context

    logger.success("🏁 Orquestador de seeders finalizado.")
