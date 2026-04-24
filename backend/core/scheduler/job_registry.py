"""
✅ REGISTRO GLOBAL DE JOBS PROGRAMADOS
Implementacion del patron Registry para cumplir con DIP (Dependency Inversion Principle)

✅ Como funciona:
- El core NUNCA busca jobs hacia afuera
- Cada job se registra a si mismo usando el decorador @register_job
- El core solo consulta este registro
- Cero acoplamiento entre core y aplicaciones

✅ Uso:
@register_job("nombre_mi_job")
async def mi_job():
    pass
"""

from typing import Callable, Dict, Awaitable, Any
from loguru import logger


class JobRegistry:
    """Singleton que actua como registro global de jobs programados.
    Las aplicaciones registran sus jobs aqui, y el scheduler los consulta para programarlos.
    """

    _instance = None
    _jobs: Dict[str, Callable[..., Awaitable[Any]]] = {}

    def __new__(cls):
        """
        Implementacion del patron Singleton para asegurar que solo exista una instancia del registro
        en toda la aplicacion, y que sea accesible globalmente.
        """

        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, name: str, func: Callable) -> None:
        """Registra una funcion como job programado
        Si ya existe un job con el mismo nombre, se sobrescribe y se registra una advertencia en los logs.
        """
        if name in cls._jobs:
            logger.warning(f"⚠️ Job '{name}' ya estaba registrado, sobrescribiendo.")

        cls._jobs[name] = func
        logger.trace(f"✅ Job '{name}' registrado exitosamente.")

    @classmethod
    def get(cls, name: str) -> Callable | None:
        """Obtiene un job por su nombre"""
        return cls._jobs.get(name)

    @classmethod
    def get_all(cls) -> Dict[str, Callable]:
        """Obtiene todos los jobs registrados"""
        return cls._jobs.copy()

    @classmethod
    def clear(cls) -> None:
        """Limpia el registro (solo para tests)"""
        cls._jobs.clear()


def register_job(name: str):
    """
    Decorador para registrar automaticamente una funcion como job programado

    Ejemplo:
    @register_job("actualizar_noticias")
    async def actualizar_noticias():
        pass
    """

    def decorator(
        func: Callable[..., Awaitable[Any]],
    ) -> Callable[..., Awaitable[Any]]:
        JobRegistry.register(name, func)
        return func

    return decorator
