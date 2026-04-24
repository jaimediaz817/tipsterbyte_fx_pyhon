import importlib
import inspect
import sys
from pathlib import Path
from loguru import logger


# ✅ USAR MECANISMO OFICIAL CENTRALIZADO DEL PROYECTO
# Este es el MISMO patron que usa core/config.py, core/logger.py y TODO el sistema
# No usar parents[n] nunca mas, usar la busqueda inteligente por ancla
def _find_project_root(anchor_file: str = "pyproject.toml") -> Path:
    current_path = Path(__file__).resolve()
    while not (current_path / anchor_file).exists():
        if current_path.parent == current_path:
            raise FileNotFoundError(
                f"No se pudo encontrar la raíz del proyecto (buscando '{anchor_file}')."
            )
        current_path = current_path.parent
    return current_path


PROJECT_ROOT = _find_project_root()

# ✅ DEBEMOS AGREGAR LA RAIZ DEL PROYECTO, NO LA CARPETA BACKEND
# Esta es la razon 100% del error. Todas las importaciones son relativas a la raiz, no a backend.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
            # ✅ GARANTIZAR que la ruta existe ANTES de cada import dinamico
            if str(PROJECT_ROOT) not in sys.path:
                sys.path.insert(0, str(PROJECT_ROOT))

            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseSeeder) and obj is not BaseSeeder:
                    all_seeder_classes.append(obj)
        except ImportError as e:
            logger.error(f"No se pudo importar el módulo de seeder {module_name}: {e}")
            logger.error(f"   sys.path actual: {sys.path[:3]}")
            logger.error(f"   PROJECT_ROOT: {PROJECT_ROOT}")
            logger.error(f"   Existe en sys.path: {str(PROJECT_ROOT) in sys.path}")

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
