import sys
from loguru import logger
from core.config import settings
from core.paths import LOGS_ROOT

# Componentes especializados SRP
from core.logging.intercept_handler import setup as setup_intercept_handler
from core.logging.intercept_handler import InterceptHandler
from core.logging.sink_manager import safe_add_sink
from core.logging.global_exception_handler import (
    setup as setup_global_exception_handler,
)
from core.logging.format_provider import console_format, file_format
from core.logging.profile_loader import load_all as load_log_profiles
from core.logging.dynamic_module_sink_loader import scan_and_load as load_dynamic_sinks


def configure_logging():
    """
    Configura el sistema de logging completo.
    ✅ UNICA RESPONSABILIDAD: Orquestar los componentes.
    ✅ CUMPLE SRP 100%
    """
    logger.remove()
    LOGS_ROOT.mkdir(exist_ok=True)

    # Configurar componentes individuales
    setup_intercept_handler()
    setup_global_exception_handler()

    # Consola SIEMPRE activa
    logger.add(
        sink=sys.stdout,
        level=settings.LOG_LEVEL.upper(),
        format=console_format,
        colorize=True,
    )

    # Archivos SOLO si FILE_LOGGING_ENABLED esta habilitado
    if settings.FILE_LOGGING_ENABLED:
        load_log_profiles()
        load_dynamic_sinks()

        logger.info(
            "✅ Logging dinámico y segmentado configurado con manejo robusto de errores."
        )
    else:
        logger.info("🔇 Logging en archivos DESHABILITADO. Solo consola activa.")


# ✅ RETROCOMPATIBILIDAD 100% - Exportar simbolos antiguos
# Para que ningun test ni codigo existente se rompa
_safe_add_sink = safe_add_sink

__all__ = [
    "configure_logging",
    "InterceptHandler",
    "safe_add_sink",
    "_safe_add_sink",
    "console_format",
    "file_format",
]
