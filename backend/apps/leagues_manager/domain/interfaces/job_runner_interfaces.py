from typing import Protocol, Optional, runtime_checkable
from apps.leagues_manager.domain.entities.fuente_extraccion import FuenteExtraccion


@runtime_checkable
class ITorneo(Protocol):
    """
    Interfaz para Torneo.
    Cualquier objeto que tenga estos atributos cumple con el contrato,
    sin importar si es modelo SQL, entidad de dominio o mock.
    """

    @property
    def nombre(self) -> str: ...


@runtime_checkable
class IDetalleFuenteExtraccion(Protocol):
    """
    Interfaz para DetalleFuenteExtraccion.
    Contrato minimo que necesita JobRunner para funcionar.
    """

    @property
    def id(self) -> Optional[int]: ...

    @property
    def process_id(self) -> Optional[int]: ...

    @property
    def fuente(self) -> Optional[FuenteExtraccion]: ...
