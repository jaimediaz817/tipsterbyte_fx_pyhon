"""
Excepciones relacionadas con fuentes y detalles.

Estas excepciones se lanzan cuando hay errores relacionados
con fuentes de extracción y sus detalles asociados.
"""

from core.exceptions.base import TipsterByteException


class FuenteException(TipsterByteException):
    """Excepción base para errores de fuente."""

    pass


class FuenteNotFoundException(FuenteException):
    """Fuente no encontrada o es None."""

    def __init__(self, detalle_id):
        super().__init__(
            message=f"Detalle ID={detalle_id} no tiene fuente asociada",
            error_code="FUENTE_NOT_FOUND",
            status_code=400,
            context={"detalle_id": str(detalle_id)},
            suggestion="Verifica que el detalle tenga una fuente_id válida",
        )


class FuenteInactiveException(FuenteException):
    """Fuente está inactiva."""

    def __init__(self, fuente_id: int, fuente_name: str):
        super().__init__(
            message=f"Fuente '{fuente_name}' (ID: {fuente_id}) está INACTIVA",
            error_code="FUENTE_INACTIVE",
            status_code=400,
            context={
                "fuente_id": fuente_id,
                "fuente_name": fuente_name,
                "is_active": False,
            },
            suggestion=f"Activa la fuente '{fuente_name}' usando el endpoint /api/v1/leagues/fuentes/{fuente_id}/resume",
        )


class DetalleInactiveException(FuenteException):
    """Detalle está inactivo."""

    def __init__(self, detalle_id: int, torneo_nombre: str, fuente_name: str):
        super().__init__(
            message=f"Detalle '{torneo_nombre}' + '{fuente_name}' (ID: {detalle_id}) está INACTIVO",
            error_code="DETALLE_INACTIVE",
            status_code=400,
            context={
                "detalle_id": detalle_id,
                "torneo_nombre": torneo_nombre,
                "fuente_name": fuente_name,
                "is_active": False,
            },
            suggestion=f"Activa el detalle usando el endpoint /api/v1/leagues/detalles/{detalle_id}/resume",
        )
