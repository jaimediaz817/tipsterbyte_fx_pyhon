"""
Excepciones relacionadas con procesos.

Estas excepciones se lanzan cuando hay errores relacionados
con la gestión y ejecución de procesos.
"""

from core.exceptions.base import TipsterByteException


class ProcessException(TipsterByteException):
    """Excepción base para errores de proceso."""

    pass


class ProcessNotFoundException(ProcessException):
    """Proceso no encontrado en base de datos."""

    def __init__(self, process_code: str):
        super().__init__(
            message=f"Proceso '{process_code}' no encontrado en base de datos",
            error_code="PROCESS_NOT_FOUND",
            status_code=404,
            context={"process_code": process_code},
            suggestion=f"Verifica que el proceso '{process_code}' exista en la tabla 'process'",
        )


class ProcessInactiveException(ProcessException):
    """Proceso está inactivo."""

    def __init__(self, process_code: str, process_id: int):
        super().__init__(
            message=f"Proceso '{process_code}' está INACTIVO",
            error_code="PROCESS_INACTIVE",
            status_code=400,
            context={
                "process_code": process_code,
                "process_id": process_id,
                "is_active": False,
            },
            suggestion=f"Marca is_active=True en la tabla 'process' para el código '{process_code}'",
        )


class ProcessRunCreationException(ProcessException):
    """No se pudo crear el ProcessRun."""

    def __init__(self, process_code: str, run_id: str):
        super().__init__(
            message=f"No se pudo crear ProcessRun para '{process_code}'",
            error_code="PROCESS_RUN_CREATION_FAILED",
            status_code=500,
            context={"process_code": process_code, "run_id": run_id},
            suggestion="Verifica que el proceso exista en BD y que la conexión sea válida",
        )


class NoActiveJobsException(ProcessException):
    """No hay trabajos activos para el proceso."""

    def __init__(self, process_code: str):
        super().__init__(
            message=f"No hay trabajos activos para el proceso '{process_code}'",
            error_code="NO_ACTIVE_JOBS",
            status_code=200,  # No es un error crítico, solo informativo
            context={"process_code": process_code},
            suggestion="Verifica que existan ligas, torneos y detalles activos para este proceso",
        )
