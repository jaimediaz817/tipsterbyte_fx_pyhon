"""
Excepciones relacionadas con concurrencia.

Estas excepciones se lanzan cuando hay errores relacionados
con la ejecución concurrente de tareas y semáforos.
"""

from core.exceptions.base import TipsterByteException


class ConcurrencyException(TipsterByteException):
    """Excepción base para errores de concurrencia."""

    pass


class SemaphoreTimeoutException(ConcurrencyException):
    """Timeout esperando semáforo."""

    def __init__(self, robot_type: str, wait_time: int):
        super().__init__(
            message=f"Timeout esperando semáforo para robot '{robot_type}'",
            error_code="SEMAPHORE_TIMEOUT",
            status_code=503,
            context={"robot_type": robot_type, "wait_time_seconds": wait_time},
            suggestion=f"Aumenta la concurrencia para '{robot_type}' o reduce la carga",
        )


class MaxRetriesExceededException(ConcurrencyException):
    """Se excedió el máximo de reintentos."""

    def __init__(self, robot_id: str, max_retries: int, last_error: Exception):
        super().__init__(
            message=f"Máximo de reintentos ({max_retries}) excedido para robot '{robot_id}'",
            error_code="MAX_RETRIES_EXCEEDED",
            status_code=500,
            context={
                "robot_id": robot_id,
                "max_retries": max_retries,
                "last_error_type": type(last_error).__name__,
                "last_error_message": str(last_error),
            },
            suggestion="Revisa los logs para entender por qué falló después de múltiples intentos",
        )


class SchedulerSemaphoreFullException(ConcurrencyException):
    """El semaforo del scheduler esta lleno, no se pueden ejecutar mas jobs."""

    def __init__(self, job_name: str, max_concurrent: int):
        super().__init__(
            message=f"Scheduler semaforo lleno. No se puede ejecutar job '{job_name}'",
            error_code="SCHEDULER_SEMAPHORE_FULL",
            status_code=503,
            context={
                "job_name": job_name,
                "max_concurrent_jobs": max_concurrent,
            },
            suggestion="El job se reprogramara automaticamente para ejecutarse mas tarde",
        )


class RobotAlreadyRunningException(ConcurrencyException):
    """El robot ya se esta ejecutando en este momento."""

    def __init__(self, robot_id: str):
        super().__init__(
            message=f"Robot '{robot_id}' ya se encuentra en ejecucion",
            error_code="ROBOT_ALREADY_RUNNING",
            status_code=409,
            context={"robot_id": robot_id},
            suggestion="Espera a que termine la ejecucion actual o cancela el proceso",
        )
