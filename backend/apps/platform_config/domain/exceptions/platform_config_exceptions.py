"""
✅ EXCEPCIONES ESPECIFICAS PARA EL DOMINIO PLATFORM_CONFIG
✅ Siguen el patron estandar del proyecto
✅ Incluyen contexto util para depuracion
✅ No son sobreingenieria, son exactamente lo necesario
"""

from __future__ import annotations


class PlatformConfigException(Exception):
    """
    ✅ Excepcion BASE para todo el modulo platform_config

    Todas las excepciones de este bounded context heredan de esta.
    Permite capturar de forma general todos los errores de este dominio.
    """

    pass


class VpsHealthCheckError(PlatformConfigException):
    """
    ❌ Error relacionado con la ejecucion o procesamiento de Health Check de VPS

    Esta excepcion se lanza cuando:
    - No se puede conectar al servidor remoto
    - El script remoto falla
    - La respuesta no es valida
    - Errores de parseo del resultado
    """

    pass


class SchedulerProcessConfigError(PlatformConfigException):
    """
    ❌ Error relacionado con la configuracion de procesos programados
    """

    pass


class ProcessConfigError(PlatformConfigException):
    """
    ❌ Error relacionado con la configuracion general de procesos
    """

    pass
