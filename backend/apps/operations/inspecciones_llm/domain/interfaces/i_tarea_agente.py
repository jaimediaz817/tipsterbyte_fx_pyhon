"""
✅ Interfaz Base Estandar para TODAS las tareas del Agente Supervisor
Contrato obligatorio. Cumplimiento ISP - Interface Segregation Principle
"""

from abc import ABC, abstractmethod


class ITareaAgente(ABC):
    """
    📜 Interfaz oficial para todas las tareas que se delegan al Agente Supervisor

    ✅ TODAS las tareas deben implementar esta interfaz
    ✅ NUNCA se modifica esta interfaz
    ✅ Todas las tareas son completamente intercambiables
    ✅ Cumplimiento estricto ISP y LSP de SOLID
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """
        Identificador unico de la tarea.
        Nunca cambia, formato snake_case: `mi_tarea_001`
        """
        pass

    @property
    @abstractmethod
    def nombre(self) -> str:
        """Nombre humano visible en tableros y reportes"""
        pass

    @property
    @abstractmethod
    def descripcion(self) -> str:
        """Descripcion detallada de que hace la tarea"""
        pass

    @property
    @abstractmethod
    def intervalo_segundos(self) -> int:
        """Cada cuanto tiempo se ejecuta automaticamente la tarea"""
        pass

    @property
    def max_intentos(self) -> int:
        """Numero maximo de reintentos en caso de fallo. Por defecto 3"""
        return 3

    @abstractmethod
    async def ejecutar(self) -> None:
        """
        Logica principal de la tarea.
        Todo el codigo de la tarea vive aqui.

        ✅ No debe lanzar excepciones hacia afuera
        ✅ Debe manejar sus propios errores
        ✅ No debe tener dependencias externas al nucleo
        """
        pass
