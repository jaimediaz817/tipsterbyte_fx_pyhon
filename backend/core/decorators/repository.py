"""
✅ DIRECTIVA @Repository
✅ Implementacion oficial segun PLAN_REFACTOR_REPOSITORIOS_@Repository.md
✅ Arquitectura Hexagonal - Core Transversal
✅ Cero dependencias, cero magia, diccionario simple

✅ REGLA CLINE APLICADA: Proteccion anti BD para tests unitarios ANTES de cualquier import
"""

# ✅ PRIMERO: PROTECCION ANTES DE TODO LO DEMAS
import os

if os.environ.get("PYTEST_VERSION") is not None:
    # En modo tests no hacemos NADA. No se carga ningun registro.
    _registry = {}
else:
    # Registro global de implementaciones
    _registry = {}

from typing import TypeVar, Type, Optional


T = TypeVar("T")


def Repository(interface: Type):
    """
    ✅ Decorador oficial @Repository

    Registra automaticamente una implementacion con su interfaz correspondiente.
    No hay configuraciones, no hay bindings, no hay frameworks.

    ✅ USO:
    ```python
    @Repository(IUserRepository)
    class SqlUserRepository(IUserRepository):
        pass
    ```

    ✅ CARACTERISTICAS:
    - Cero magia. Simplemente un diccionario.
    - Cero overhead.
    - Thread safe.
    - Funciona en runtime y en tests.
    - En modo pytest NO SE CARGA NADA.
    """

    def decorator(cls: Type[T]) -> Type[T]:
        # Solo registramos si NO estamos en modo tests
        if os.environ.get("PYTEST_VERSION") is None:
            _registry[interface] = cls
            setattr(cls, "__interface__", interface)
        return cls

    return decorator


def get_implementation(interface: Type[T]) -> Type[T] | None:
    """
    Obtiene la implementacion registrada para una interfaz

    ✅ Retorna la clase, NO una instancia.
    ✅ Retorna None si no hay implementacion registrada.
    """
    from typing import cast

    return cast(Type[T] | None, _registry.get(interface))


def get_instance(interface: Type[T]) -> Optional[T]:
    """
    Obtiene una instancia nueva de la implementacion registrada

    ✅ Crea una nueva instancia cada vez.
    ✅ Retorna None si no hay implementacion registrada.
    """
    impl_class = _registry.get(interface)
    if impl_class:
        return impl_class()
    return None


def override_implementation(interface: Type, implementation: Type):
    """
    Override temporal de implementacion. USO EXCLUSIVO PARA TESTS.
    """
    _registry[interface] = implementation


def clear_registry():
    """
    Limpia todo el registro. USO EXCLUSIVO PARA TESTS.
    """
    _registry.clear()
