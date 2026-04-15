from loguru import logger


def _global_exception_handler(message):
    """Captura errores de logging sin interrumpir la ejecución."""
    pass  # Silenciar errores de logging para no ensuciar la consola


def setup():
    """Configura el manejador global de excepciones de logging."""
    logger.add(
        sink=_global_exception_handler,
        format="",
        catch=True,
        level="ERROR",
    )
