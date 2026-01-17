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
    """
    def wrapper():
        try:
            logger.info(f"🚀 Lanzando job async: {coro_func.__name__}")
            asyncio.create_task(coro_func(*args, **kwargs))
        except Exception as e:
            logger.exception(f"❌ Error al lanzar job async: {e}")
    return wrapper
