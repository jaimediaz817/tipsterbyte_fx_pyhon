from loguru import logger
from core.paths import LOGS_ROOT
from core.logging import LOG_PROFILES
from core.logging.format_provider import file_format
from core.logging.sink_manager import safe_add_sink


def load_all():
    """Carga todos los perfiles de log configurados."""
    (LOGS_ROOT / "scheduler").mkdir(exist_ok=True)

    # Configurar sinks usando perfiles (Strategy Pattern)
    for profile in LOG_PROFILES.values():
        safe_add_sink(
            sink_path=profile.sink_path,
            level=profile.level,
            format=file_format,
            filter=profile.filter,
            rotation=profile.rotation,
            retention=profile.retention,
            compression=profile.compression,
            enqueue=True,
            backtrace=True,
            diagnose=True,
            delay=True,
            mode="a",
            catch=True,
        )
