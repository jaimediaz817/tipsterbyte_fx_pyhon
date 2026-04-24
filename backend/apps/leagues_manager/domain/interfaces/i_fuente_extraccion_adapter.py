from abc import ABC, abstractmethod
from typing import Any, Dict, List
from apps.leagues_manager.domain.entities.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion,
)


class IFuenteExtraccionAdapter(ABC):
    """
    ✅ INTERFACE CONTRATO PARA TODAS LAS FUENTES DE EXTRACCION
    Todas las fuentes: API, Web Scraping, FTP, etc. DEBEN implementar este contrato.

    Esta es la unica forma en la que el sistema se comunica con las fuentes externas.
    Ningun otro componente del sistema sabe nada de la implementacion interna.
    """

    @abstractmethod
    def __init__(self, detalle_fuente: DetalleFuenteExtraccion):
        """
        Todo adaptador recibe unicamente la entidad DetalleFuenteExtraccion
        Contiene absolutamente toda la configuracion necesaria para conectarse
        """
        pass

    @abstractmethod
    async def obtener_ligas(self) -> List[Dict[str, Any]]:
        """Obtiene listado de ligas disponibles en la fuente"""
        pass

    @abstractmethod
    async def obtener_torneos(self, liga_externa_id: str) -> List[Dict[str, Any]]:
        """Obtiene torneos de una liga especifica"""
        pass

    @abstractmethod
    async def obtener_partidos(self, torneo_externo_id: str) -> List[Dict[str, Any]]:
        """Obtiene partidos de un torneo especifico"""
        pass

    @abstractmethod
    async def obtener_cuotas(self, partido_externo_id: str) -> List[Dict[str, Any]]:
        """Obtiene cuotas de un partido especifico"""
        pass
