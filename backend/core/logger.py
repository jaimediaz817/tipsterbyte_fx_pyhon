import logging
import sys
from loguru import logger
from core.config import settings
from core.paths import BACKEND_ROOT, LOGS_ROOT
import os
from pathlib import Path


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

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def _safe_add_sink(sink_path: Path, **kwargs):
    """
    Agrega un sink de Loguru de manera segura, deshabilitando rotación si hay errores.
    """
    try:
        # Intentar agregar con rotación
        logger.add(sink=sink_path, **kwargs)
    except Exception as e:
        # Si hay error, intentar sin rotación
        logger.warning(f"⚠️ Error al configurar rotación para {sink_path.name}: {e}")
        logger.info(f"🔄 Deshabilitando rotación para {sink_path.name}")

        # Remover parámetros de rotación
        safe_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k not in ["rotation", "retention", "compression"]
        }

        try:
            logger.add(sink=sink_path, **safe_kwargs)
            logger.info(f"✅ Sink {sink_path.name} configurado sin rotación")
        except Exception as e2:
            logger.error(f"❌ Error crítico al configurar sink {sink_path.name}: {e2}")


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
    - Manejo robusto de errores de rotación en Windows.
    """
    logger.remove()
    LOGS_ROOT.mkdir(exist_ok=True)

    # Redirigir logging estándar
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Formatos
    console_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>"
    file_format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"

    # Agregar exception handler global para capturar errores de rotación en Windows
    def _global_exception_handler(message):
        """Captura errores de logging sin interrumpir la ejecución."""
        pass  # Silenciar errores de logging para no ensuciar la consola

    logger.add(
        sink=_global_exception_handler,
        format="",
        catch=True,
        level="ERROR",
    )

    # Consola SIEMPRE activa
    logger.add(
        sink=sys.stdout,
        level=settings.LOG_LEVEL.upper(),
        format=console_format,
        colorize=True,
    )

    # Archivos SOLO si FILE_LOGGING_ENABLED está habilitado
    if settings.FILE_LOGGING_ENABLED:
        # System (core, excluye scheduler)
        def system_filter(record):
            name = record["name"]
            return bool(name and name.startswith("core") and "scheduler" not in name)

        _safe_add_sink(
            sink_path=LOGS_ROOT / "system.log",
            level="INFO",
            format=file_format,
            filter=system_filter,
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True,
            delay=True,
            mode="a",
            catch=True,
        )

        # Scheduler
        (LOGS_ROOT / "scheduler").mkdir(exist_ok=True)

        def scheduler_filter(record):
            name = record["name"]
            return bool(name and "scheduler" in name)

        _safe_add_sink(
            sink_path=LOGS_ROOT / "scheduler" / "scheduler.log",
            level="INFO",
            format=file_format,
            filter=scheduler_filter,
            rotation="5 MB",
            retention="14 days",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True,
            delay=True,
            mode="a",
            catch=True,
        )

        # Robots de leagues_manager → robots.log
        def robots_filter(record):
            n = record["name"]
            # Coincide tanto con apps.leagues_manager.robots.* como apps.leagues_manager.domain.robots.*
            return bool(
                n
                and n.startswith("apps.leagues_manager")
                and (".robots." in n or n.endswith(".robots"))
            )

        _safe_add_sink(
            sink_path=LOGS_ROOT / "robots.log",
            level="INFO",
            format=file_format,
            filter=robots_filter,
            rotation="10 MB",
            retention="10 days",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True,
            delay=True,
            mode="a",
            catch=True,
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
                            return (
                                n.startswith(f"apps.{name}")
                                and ".robots." not in n
                                and not n.endswith(".robots")
                            )

                        return _f

                    _safe_add_sink(
                        sink_path=LOGS_ROOT / f"{module_name}.log",
                        level="INFO",
                        format=file_format,
                        filter=create_module_filter(module_name),
                        rotation="10 MB",
                        retention="10 days",
                        compression="zip",
                        enqueue=True,
                        backtrace=True,
                        diagnose=True,
                        delay=True,
                        mode="a",
                        catch=True,
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

        _safe_add_sink(
            sink_path=LOGS_ROOT / "general_app.log",
            level="INFO",
            format=file_format,
            filter=is_general_log,
            rotation="20 MB",
            retention="5 days",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True,
            delay=True,
            mode="a",
            catch=True,
        )

        logger.info(
            "✅ Logging dinámico y segmentado configurado con manejo robusto de errores."
        )
    else:
        logger.info("🔇 Logging en archivos DESHABILITADO. Solo consola activa.")
