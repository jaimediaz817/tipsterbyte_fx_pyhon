"""
Excepciones relacionadas con fuentes y detalles.

Estas excepciones se lanzan cuando hay errores relacionados
con fuentes de extracción y sus detalles asociados.
"""

from typing import Optional
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


class AdapterClassNotFoundException(FuenteException):
    """Clase de adaptador no encontrada en el sistema."""

    def __init__(self, adapter_class: str, detalle_id: int):
        super().__init__(
            message=f"Adaptador '{adapter_class}' no existe o no se puede cargar",
            error_code="ADAPTER_CLASS_NOT_FOUND",
            status_code=500,
            context={"adapter_class": adapter_class, "detalle_id": detalle_id},
            suggestion="Verifica que la clase este declarada y sea importable correctamente",
        )


class AdapterInvalidContractException(FuenteException):
    """El adaptador no implementa la interfaz IFuenteExtraccionAdapter."""

    def __init__(self, adapter_class: str, detalle_id: int):
        super().__init__(
            message=f"Adaptador '{adapter_class}' no implementa el contrato IFuenteExtraccionAdapter",
            error_code="ADAPTER_INVALID_CONTRACT",
            status_code=500,
            context={
                "adapter_class": adapter_class,
                "detalle_id": detalle_id,
                "required_interface": "IFuenteExtraccionAdapter",
            },
            suggestion="Implementa todos los metodos abstractos de la interfaz",
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


class DetalleFuenteInvalidoException(FuenteException):
    """Detalle de fuente tiene datos invalidos o incompletos."""

    def __init__(self, detalle_id: int, campo: str, valor: Optional[str] = None):
        context = {
            "detalle_id": detalle_id,
            "campo_invalido": campo,
        }

        if valor:
            context["valor_recibido"] = str(valor)

        super().__init__(
            message=f"Detalle ID={detalle_id} tiene valor invalido en campo '{campo}'",
            error_code="DETALLE_FUENTE_INVALIDO",
            status_code=400,
            context=context,
            suggestion="Verifica que todos los campos obligatorios del detalle esten correctamente configurados",
        )
