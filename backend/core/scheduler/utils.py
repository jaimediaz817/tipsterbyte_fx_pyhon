import asyncio
from loguru import logger


def schedule_async_job(coro_func, *args, **kwargs):
    """
    Envuelve una función coroutine para ser ejecutada de forma asíncrona.
    Args:
        coro_func (coroutine function): La función coroutine a ejecutar.
        *args: Argumentos posicionales para la función coroutine.
        **kwargs: Argumentos nombrados para la función coroutine.
    Returns:
        function: Una función que al ser llamada, lanza la coroutine como una tarea asíncrona.

    Un claro ejemplo en el contexto de tipsterbyte es:
    @schedule_async_job
    async def mi_job():
        # lógica del job
        pass

    Esto permite que el job se ejecute de forma asíncrona sin bloquear el hilo principal del scheduler, y maneja automáticamente cualquier excepción que pueda ocurrir durante la ejecución del job, registrándola en los logs para facilitar la depuración.

    en resumen:
    - Permite ejecutar funciones coroutine de forma asíncrona sin bloquear el scheduler
    - Maneja excepciones de forma centralizada, registrándolas en los logs
    - Facilita la integración de jobs asíncronos en el sistema de scheduling sin necesidad de modificar la lógica interna del scheduler
    """

    def wrapper():
        try:
            logger.info(f"🚀 Lanzando job async: {coro_func.__name__}")
            asyncio.create_task(coro_func(*args, **kwargs))
        except Exception as e:
            logger.exception(f"❌ Error al lanzar job async: {e}")

    return wrapper
