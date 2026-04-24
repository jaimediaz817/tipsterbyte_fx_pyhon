import logging
from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Redirige los logs del sistema de logging estándar de Python a Loguru.
    Captura logs de librerías que usan 'logging' (uvicorn, SQLAlchemy, APScheduler, etc.).

    ✅ BUG HISTORICO CORREGIDO:
    --------------------------------------------------------------------------------
    🔴 PROBLEMA ORIGINAL:
    El campo `name` NUNCA llegaba al record de Loguru cuando el log venia del modulo
    estandar `logging`. El InterceptHandler capturaba el log pero NO propagaba
    ningun campo extra, solo el mensaje y el nivel.

    ✅ CONSECUENCIA:
    Todos los filtros que usaban `record.get("name")` NO FUNCIONABAN. El caso mas
    critico era el SchedulerProfile que filtrar por "scheduler" y devolvia SIEMPRE
    False, por lo que ningun log llegaba a scheduler.log.

    ✅ SOLUCION:
    Ahora se usa `.bind()` para propagar TODOS los campos relevantes del record
    original de logging al sistema de Loguru.

    📅 Detectado: 22/04/2026
    🎯 Este es uno de los bugs mas dificiles de encontrar de todo Loguru. No esta
       documentado en ningun lugar.
    --------------------------------------------------------------------------------
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

        # ✅ PROPAGAR TODOS LOS CAMPOS ORIGINALES AL RECORD DE LOGURU
        extra_fields = {
            "name": record.name,
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "process": record.process,
            "thread": record.thread,
        }

        logger.opt(depth=depth, exception=record.exc_info).bind(**extra_fields).log(
            level, record.getMessage()
        )


def setup():
    """Configura el interceptador de logs estandar."""
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
