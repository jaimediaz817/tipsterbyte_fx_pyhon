from __future__ import annotations
import importlib
from typing import Type
from loguru import logger

from core.exceptions.fuente_exceptions import (
    AdapterClassNotFoundException,
    AdapterInvalidContractException,
)
from apps.leagues_manager.domain.entities.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion,
)
from apps.leagues_manager.domain.interfaces.i_fuente_extraccion_adapter import (
    IFuenteExtraccionAdapter,
)


class FuenteExtraccionAdapterFactory:
    """
    ✅ FABRICA DE ADAPTADORES DE FUENTES DE EXTRACCION
    Crea automaticamente la instancia correcta del adaptador segun el campo adapter_class
    No sabe nada de la implementacion interna de ningun adaptador.
    """

    @staticmethod
    def crear(detalle_fuente: DetalleFuenteExtraccion) -> IFuenteExtraccionAdapter:
        """
        Crea una instancia del adaptador correcto para esta fuente de extraccion

        ✅ Si no tiene adapter_class definido usa el adaptador por defecto
        ✅ Si la clase no existe lanza error claro
        ✅ Si la clase no implementa el contrato lanza error
        """

        if not detalle_fuente.adapter_class:
            # ✅ Adaptador por defecto para compatibilidad hacia atras
            from apps.leagues_manager.infrastructure.adapters.api_football_adapter import (
                ApiFootballAdapter,
            )

            logger.warning(
                f"⚠️  No hay adaptador definido para fuente id: {detalle_fuente.id}"
            )
            logger.warning("Usando ApiFootballAdapter por defecto")
            return ApiFootballAdapter(detalle_fuente)

        try:
            # Cargar la clase dinamicamente desde el string
            module_name, class_name = detalle_fuente.adapter_class.rsplit(".", 1)
            module = importlib.import_module(module_name)
            adapter_class = getattr(module, class_name)

        except (ValueError, ImportError, AttributeError) as e:
            logger.error(
                f"❌ Error cargando adaptador {detalle_fuente.adapter_class}: {str(e)}"
            )
            from typing import cast

            raise AdapterClassNotFoundException(
                adapter_class=detalle_fuente.adapter_class,
                detalle_id=cast(int, detalle_fuente.id),
            ) from e

        # Verificar que implemente el contrato
        if not issubclass(adapter_class, IFuenteExtraccionAdapter):
            logger.error(
                f"❌ El adaptador {detalle_fuente.adapter_class} no implementa IFuenteExtraccionAdapter"
            )
            from typing import cast

            raise AdapterInvalidContractException(
                adapter_class=detalle_fuente.adapter_class,
                detalle_id=cast(int, detalle_fuente.id),
            )

        logger.debug(
            f"✅ Adaptador {detalle_fuente.adapter_class} cargado correctamente"
        )
        return adapter_class(detalle_fuente)
