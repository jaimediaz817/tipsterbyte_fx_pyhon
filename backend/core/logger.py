# TODO: tb-hu-refactors-block-01
# from loguru import logger
# import sys
# from core.config import settings
# from pathlib import Path

# # Sube dos niveles para llegar a la raíz de 'backend' y luego crea la carpeta 'logs'
# LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
# LOG_DIR.mkdir(exist_ok=True)

# def configure_logging():
#     logger.remove()
    
#     print(f"DEBUG:LOGGER >>>>>>>> Configurando logging. LOG_DIR: {Path(__file__).resolve().parent.parent}")

#     # Consola
#     logger.add(
#         sys.stdout,
#         level=settings.LOG_LEVEL,
#         format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{module}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
#         backtrace=True,
#         diagnose=True
#     )

#     # Archivo general
#     logger.add(
#         LOG_DIR / "app.log",
#         level=settings.LOG_LEVEL,
#         rotation="10 MB",
#         retention="10 days",
#         format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function} - {message}",
#         compression="zip",
#         enqueue=True
#     )

# import sys
# from pathlib import Path
# from loguru import logger
# from core.paths import LOGS_ROOT
# from core.config import settings

# # --- 1. DEFINICIÓN DE FILTROS ---
# # Cada función determina si un log pertenece a una categoría específica.

# def is_system_log(record):
#     """Filtro para logs generales del sistema (core, middleware, etc.)."""
#     return record["name"].startswith("core") and not record["name"].startswith("core.scheduler")

# def is_scheduler_log(record):
#     """Filtro para todos los logs relacionados con el scheduler."""
#     return "scheduler" in record["name"]

# def is_auth_log(record):
#     """Filtro para logs específicos del módulo de autenticación."""
#     return record["name"].startswith("apps.auth")

# def is_general_app_log(record):
#     """Filtro "cajón de sastre" para todo lo que no coincide con los filtros específicos."""
#     return not (
#         is_system_log(record)
#         or is_scheduler_log(record)
#         or is_auth_log(record)
#     )

# # --- 2. CONFIGURACIÓN CENTRALIZADA DE SINKS ---
# # Un "sink" es un destino para los logs (un archivo, la consola, etc.).

# LOGGING_CONFIG = {
#     "sinks": [
#         # Sink 1: Consola (para desarrollo, muestra todo con colores)
#         {
#             "sink": sys.stdout,
#             "level": settings.LOG_LEVEL.upper(),
#             "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>",
#             "colorize": True,
#         },
#         # Sink 2: Logs del Sistema (core, middleware, etc.)
#         {
#             "sink": LOGS_ROOT / "system.log",
#             "filter": is_system_log,
#             "level": "INFO",
#             "rotation": "10 MB",
#             "retention": "7 days",
#         },
#         # Sink 3: Logs del Scheduler (en su propia carpeta para máxima organización)
#         {
#             "sink": LOGS_ROOT / "scheduler/scheduler.log",
#             "filter": is_scheduler_log,
#             "level": "INFO",
#             "rotation": "5 MB",
#             "retention": "14 days",
#         },
#         # Sink 4: Logs de Autenticación (críticos para seguridad)
#         {
#             "sink": LOGS_ROOT / "auth.log",
#             "filter": is_auth_log,
#             "level": "INFO",
#             "rotation": "5 MB",
#             "retention": "30 days",
#         },
#         # Sink 5: Log General (para todo lo demás, como nuevos módulos no especificados)
#         {
#             "sink": LOGS_ROOT / "general_app.log",
#             "filter": is_general_app_log,
#             "level": "INFO",
#             "rotation": "20 MB",
#             "retention": "5 days",
#         },
#     ],
#     # Formato por defecto para los sinks de archivo si no especifican uno.
#     "default_format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
# }

# # --- 3. FUNCIÓN DE CONFIGURACIÓN PRINCIPAL ---

# def configure_logging():
#     """
#     Configura Loguru basándose en el diccionario LOGGING_CONFIG.
#     Esta es la única función que se debe llamar desde el resto de la aplicación.
#     """
#     logger.remove()  # Limpia configuraciones previas para evitar duplicados.
    
#     # Asegura que el directorio raíz de logs exista.
#     LOGS_ROOT.mkdir(exist_ok=True)

#     for config in LOGGING_CONFIG["sinks"]:
#         # Para los sinks de archivo, nos aseguramos de que su directorio padre exista.
#         # Esto crea 'logs/scheduler/' automáticamente.
#         if isinstance(config["sink"], Path):
#             config["sink"].parent.mkdir(exist_ok=True, parents=True)

#         logger.add(
#             sink=config["sink"],
#             level=config.get("level", "INFO"),
#             format=config.get("format", LOGGING_CONFIG["default_format"]),
#             filter=config.get("filter"),
#             rotation=config.get("rotation"),
#             retention=config.get("retention"),
#             colorize=config.get("colorize", False),
#             enqueue=True,      # Hace el logging asíncrono y no bloquea la aplicación.
#             backtrace=True,    # Muestra el stack trace completo en errores.
#             diagnose=True,     # Añade información de diagnóstico en excepciones.
#             compression="zip" if config.get("rotation") else None,
#         )
    
#     logger.info("✅ Logging configurado con múltiples sinks y filtros.")






# import sys
# from pathlib import Path
# from loguru import logger
# from core.paths import LOGS_ROOT, BACKEND_ROOT
# from core.config import settings

# def configure_logging():
#     """
#     Configura Loguru con un sistema de logging dinámico y robusto.
#     - Un sink para la consola.
#     - Sinks estáticos para 'system' y 'scheduler'.
#     - Sinks generados dinámicamente para cada módulo dentro de la carpeta 'apps'.
#     - Un sink "cajón de sastre" para todo lo demás.
#     """
#     logger.remove()  # Limpia configuraciones previas.
#     LOGS_ROOT.mkdir(exist_ok=True)

#     # --- Sink 1: Consola (para desarrollo) ---
#     logger.add(
#         sink=sys.stdout,
#         level=settings.LOG_LEVEL.upper(),
#         format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>",
#         colorize=True,
#     )

#     # --- Sinks Estáticos para Módulos Críticos ---
#     # Estos son fijos porque su lógica es bien conocida.
    
#     # Sink para System (core)
#     logger.add(
#         sink=LOGS_ROOT / "system.log",
#         level="INFO",
#         format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
#         filter=lambda record: record["name"].startswith("core") and "scheduler" not in record["name"],
#         rotation="10 MB", retention="7 days", compression="zip", enqueue=True, backtrace=True, diagnose=True
#     )

#     # Sink para Scheduler
#     (LOGS_ROOT / "scheduler").mkdir(exist_ok=True)
#     logger.add(
#         sink=LOGS_ROOT / "scheduler/scheduler.log",
#         level="INFO",
#         format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
#         filter=lambda record: "scheduler" in record["name"],
#         rotation="5 MB", retention="14 days", compression="zip", enqueue=True, backtrace=True, diagnose=True
#     )

#     # --- Sinks Dinámicos para Módulos en 'apps' ---
#     # Aquí está la magia: escaneamos la carpeta 'apps' y creamos un sink para cada módulo.
#     apps_dir = BACKEND_ROOT / "apps"
#     module_names = []
#     if apps_dir.exists():
#         for module_path in apps_dir.iterdir():
#             if module_path.is_dir() and (module_path / "__init__.py").exists():
#                 module_name = module_path.name
#                 module_names.append(module_name)
                
#                 log_dir = LOGS_ROOT / module_name
#                 log_dir.mkdir(exist_ok=True)
                
#                 logger.add(
#                     sink=log_dir / f"{module_name}.log",
#                     level="INFO",
#                     format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
#                     filter=lambda record, name=module_name: record["name"].startswith(f"apps.{name}"),
#                     rotation="10 MB", retention="10 days", compression="zip", enqueue=True, backtrace=True, diagnose=True
#                 )

#     # --- Sink Final: El "Cajón de Sastre" ---
#     # Captura todo lo que no fue capturado por los filtros anteriores.
#     def is_general_log(record):
#         name = record["name"]
#         if name.startswith("core") or "scheduler" in name:
#             return False
#         if any(name.startswith(f"apps.{mod_name}") for mod_name in module_names):
#             return False
#         return True

#     logger.add(
#         sink=LOGS_ROOT / "general_app.log",
#         level="INFO",
#         format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
#         filter=is_general_log,
#         rotation="20 MB", retention="5 days", compression="zip", enqueue=True, backtrace=True, diagnose=True
#     )

#     logger.info("✅ Logging dinámico y estático configurado.")





import logging
import sys
from loguru import logger
from core.config import settings
from core.paths import BACKEND_ROOT, LOGS_ROOT

class InterceptHandler(logging.Handler):
    """
    Redirige los logs del sistema de logging estándar de Python a Loguru.
    Captura logs de librerías que usan 'logging' (uvicorn, SQLAlchemy, APScheduler, etc.).
    """
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def configure_logging():
    """
    Configura Loguru con:
    - Redirección de logging estándar de Python.
    - Sink de consola.
    - Sinks estáticos para 'core/system' y 'core/scheduler'.
    - Sink específico para robots de leagues_manager.
    - Sinks dinámicos por cada módulo en 'backend/apps' (excluyendo robots).
    - Sink 'general_app.log' que excluye explícitamente 'core', 'scheduler' y TODOS los 'apps.*'
      para evitar duplicados con los sinks de apps/robots.
    """
    logger.remove()
    LOGS_ROOT.mkdir(exist_ok=True)

    # Redirigir logging estándar
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Formatos
    console_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>"
    file_format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"

    # Consola
    logger.add(
        sink=sys.stdout,
        level=settings.LOG_LEVEL.upper(),
        format=console_format,
        colorize=True,
    )

    # System (core, excluye scheduler)
    logger.add(
        sink=LOGS_ROOT / "system.log",
        level="INFO",
        format=file_format,
        filter=lambda r: r["name"].startswith("core") and "scheduler" not in r["name"],
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    # Scheduler
    (LOGS_ROOT / "scheduler").mkdir(exist_ok=True)
    logger.add(
        sink=LOGS_ROOT / "scheduler" / "scheduler.log",
        level="INFO",
        format=file_format,
        filter=lambda r: "scheduler" in r["name"],
        rotation="5 MB",
        retention="14 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    # Robots de leagues_manager → robots.log
    def robots_filter(record):
        n = record["name"]
        # Coincide tanto con apps.leagues_manager.robots.* como apps.leagues_manager.domain.robots.*
        return n.startswith("apps.leagues_manager") and (".robots." in n or n.endswith(".robots"))

    logger.add(
        sink=LOGS_ROOT / "robots.log",
        level="INFO",
        format=file_format,
        filter=robots_filter,
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    # Sinks dinámicos por módulo en apps (excluyendo robots)
    apps_dir = BACKEND_ROOT / "apps"
    module_names: list[str] = []
    if apps_dir.exists():
        for module_path in apps_dir.iterdir():
            if module_path.is_dir() and (module_path / "__init__.py").exists():
                module_name = module_path.name
                module_names.append(module_name)

                def create_module_filter(name: str):
                    def _f(record):
                        n = record["name"]
                        return n.startswith(f"apps.{name}") and ".robots." not in n and not n.endswith(".robots")
                    return _f

                logger.add(
                    sink=LOGS_ROOT / f"{module_name}.log",
                    level="INFO",
                    format=file_format,
                    filter=create_module_filter(module_name),
                    rotation="10 MB",
                    retention="10 days",
                    compression="zip",
                    enqueue=True,
                    backtrace=True,
                    diagnose=True,
                )

    # General: excluye core, scheduler y TODOS los apps.*
    # Esto evita duplicados de robots y de módulos de apps en general_app.log.
    def is_general_log(record):
        name = record["name"]
        if name.startswith("core") or "scheduler" in name:
            return False
        # Excluye cualquier logger bajo apps.*
        if name.startswith("apps."):
            return False
        return True

    logger.add(
        sink=LOGS_ROOT / "general_app.log",
        level="INFO",
        format=file_format,
        filter=is_general_log,
        rotation="20 MB",
        retention="5 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    logger.info("✅ Logging dinámico y segmentado configurado.")