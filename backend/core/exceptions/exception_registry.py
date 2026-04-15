"""
✅ REGISTRO GLOBAL DE EXCEPCIONES
Implementacion del patron Registry para cumplir con OCP (Open/Closed Principle)

✅ Principio cumplido:
- ✅ ABIERTO para extension: Cualquier aplicacion puede agregar excepciones nuevas
- ✅ CERRADO para modificacion: El core NUNCA MAS se modifica para agregar excepciones

✅ Caracteristicas:
- 100% retrocompatible
- Cero acoplamiento entre core y aplicaciones
- Cada aplicacion se autocontiene
- Cumple al 100% Clean Architecture
"""

from typing import Dict, Type
from core.exceptions.base import TipsterByteException


class ExceptionRegistry:
    """
    ✅ Registro global dinamico de excepciones

    Soluciona la violacion OCP del antiguo archivo __init__.py
    Ahora cada aplicacion registra sus propias excepciones
    El core ya no necesita saber nada de las excepciones de las aplicaciones
    """

    _exceptions: Dict[str, Type[TipsterByteException]] = {}

    @classmethod
    def register(cls, exception_class: Type[TipsterByteException]) -> None:
        """Registra una excepcion en el sistema global"""
        cls._exceptions[exception_class.__name__] = exception_class

    @classmethod
    def get(cls, name: str) -> Type[TipsterByteException] | None:
        """Obtiene una excepcion por nombre"""
        return cls._exceptions.get(name)

    @classmethod
    def get_all(cls) -> Dict[str, Type[TipsterByteException]]:
        """Obtiene todas las excepciones registradas"""
        return cls._exceptions.copy()

    @classmethod
    def clear(cls) -> None:
        """Limpia el registro (solo para tests)"""
        cls._exceptions.clear()


def register_exception(cls: Type[TipsterByteException]) -> Type[TipsterByteException]:
    """
    ✅ Decorador para registrar automaticamente excepciones

    Uso:
    @register_exception
    class MiExcepcion(TipsterByteException):
        pass
    """
    ExceptionRegistry.register(cls)
    return cls
