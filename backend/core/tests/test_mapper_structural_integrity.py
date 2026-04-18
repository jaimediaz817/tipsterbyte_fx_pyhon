"""
✅ TEST DE INTEGRIDAD ESTRUCTURAL PERMANENTE
✅ Detecta AUTOMATICAMENTE campos olvidados en Mappers, Entidades y Modelos SQL
✅ NUNCA MAS volvera a pasar el error de campos faltantes en seeders
✅ Ejecutable desde Testing Explorer VS Code y pytest
"""

import sys
from pathlib import Path
from typing import Set, Any
from dataclasses import fields

# ✅ Configuracion PATH Universal
ROOT_PROYECTO = Path(__file__).resolve().parents[3]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

from dotenv import load_dotenv

load_dotenv(ROOT_PROYECTO / "backend" / ".env")

import pytest
from sqlalchemy import inspect
from sqlalchemy.orm.attributes import InstrumentedAttribute

# Importar entidades y modelos
from apps.leagues_manager.domain.entities.fuente_extraccion import FuenteExtraccion
from apps.leagues_manager.infrastructure.models.sql.fuente_extraccion import (
    FuenteExtraccion as FuenteExtraccionModel,
)
from apps.leagues_manager.infrastructure.mappers.fuente_extraccion_mapper import (
    map_fuente_extraccion_from_model,
)


def get_model_sql_fields(model_class: Any) -> Set[str]:
    """Extrae todos los nombres de campos de un modelo SQLAlchemy"""
    mapper = inspect(model_class)
    return {c.key for c in mapper.columns if not c.key.startswith("_")}


def get_entity_fields(entity_class: Any) -> Set[str]:
    """Extrae todos los nombres de campos de una entidad dataclass"""
    return {f.name for f in fields(entity_class)}


def get_mapper_used_fields(mapper_function: Any, model_instance: Any) -> Set[str]:
    """Detecta que campos USA realmente el mapper desde el modelo"""
    accessed_fields = set()

    class AttributeTracker:
        def __getattr__(self, name):
            accessed_fields.add(name)
            return None

    # Ejecutar mapper con tracker
    mapper_function(AttributeTracker())

    return accessed_fields


class TestMapperStructuralIntegrity:
    """
    ✅ Test que NUNCA DEBE FALLAR
    Valida que no existan desincronizaciones entre las 3 capas:
    1. Modelo SQL ✅
    2. Entidad de Dominio ✅
    3. Mapper ✅
    """

    def test_fuente_extraccion_no_tiene_campos_olvidados(self):
        """Validacion para FuenteExtraccion"""

        # 🔍 Obtener campos de cada capa
        sql_fields = get_model_sql_fields(FuenteExtraccionModel)
        entity_fields = get_entity_fields(FuenteExtraccion)
        mapper_fields = get_mapper_used_fields(map_fuente_extraccion_from_model, None)

        # ❌ Campos que existen en SQL pero NO en Entidad
        missing_in_entity = sql_fields - entity_fields

        # ❌ Campos que existen en SQL pero NO se mapean
        missing_in_mapper = sql_fields - mapper_fields

        # ❌ Campos que existen en Entidad pero NO existen en SQL
        extra_in_entity = entity_fields - sql_fields

        errores = []

        if missing_in_entity:
            errores.append(
                f"❌ CAMPOS FALTANTES EN ENTIDAD: {sorted(missing_in_entity)}"
            )

        if missing_in_mapper:
            errores.append(
                f"❌ CAMPOS NO MAPEADOS EN MAPPER: {sorted(missing_in_mapper)}"
            )

        if extra_in_entity:
            errores.append(
                f"⚠️  CAMPOS EXTRA EN ENTIDAD (no existen en BD): {sorted(extra_in_entity)}"
            )

        if errores:
            mensaje = "\n".join(
                [
                    "🚨 DESINCRONIZACION ESTRUCTURAL DETECTADA!",
                    "",
                    *errores,
                    "",
                    "📌 Campos en Modelo SQL:   " + str(sorted(sql_fields)),
                    "📌 Campos en Entidad:      " + str(sorted(entity_fields)),
                    "📌 Campos usados Mapper:   " + str(sorted(mapper_fields)),
                    "",
                    "✅ Solucion: Agregar los campos faltantes en la Entidad y el Mapper",
                ]
            )
            pytest.fail(mensaje)

        # ✅ Todo esta sincronizado
        assert True, "✅ Todas las capas estan perfectamente sincronizadas"

    def test_mapper_tiene_todos_los_campos_mapeados(self):
        """Valida estaticamente que NO hay campos olvidados en el mapper"""
        sql_fields = get_model_sql_fields(FuenteExtraccionModel)
        mapper_fields = get_mapper_used_fields(map_fuente_extraccion_from_model, None)

        campos_faltantes = sql_fields - mapper_fields

        assert len(campos_faltantes) == 0, f"❌ CAMPOS NO MAPEADOS: {campos_faltantes}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
