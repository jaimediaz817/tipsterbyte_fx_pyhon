"""
✅ Cargador Automatico de Tareas por Descubrimiento
Patron Strategy + Discovery. Cumplimiento OCP - Open/Closed Principle
"""

import sys
import importlib
from pathlib import Path
from typing import List, Type, Optional
from loguru import logger

ROOT_PROYECTO = Path(__file__).resolve().parents[2]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

from inspecciones_llm.domain.interfaces.i_tarea_agente import ITareaAgente


class CargadorTareas:
    """
    📦 Cargador automatico de tareas

    ✅ Descubre automaticamente TODAS las tareas que implementan ITareaAgente
    ✅ No hay que registrar nada manualmente
    ✅ Si agregas un nuevo archivo en /tareas/ se carga solo
    ✅ Cumplimiento estricto OCP: Abierto para extender, cerrado para modificar
    ✅ Si una tarea falla, el resto siguen cargandose
    """

    RUTA_TAREAS = Path(__file__).resolve().parents[0] / ".." / "tareas"

    @classmethod
    def cargar_todas_las_tareas(cls) -> List[ITareaAgente]:
        """Carga y devuelve todas las tareas encontradas en el sistema"""
        tareas: List[ITareaAgente] = []

        logger.info("🔍 Buscando tareas disponibles...")

        # Buscar todos los archivos python en la carpeta tareas
        for archivo in cls.RUTA_TAREAS.glob("*.py"):
            if archivo.name.startswith("_"):
                continue

            try:
                tarea = cls._cargar_tarea_desde_archivo(archivo)
                if tarea is not None:
                    tareas.append(tarea)
                    logger.success(f"✅ Tarea cargada: {tarea.nombre} [{tarea.id}]")

            except Exception as e:
                logger.error(f"❌ Error cargando tarea {archivo.name}: {str(e)}")
                continue

        logger.info(f"📋 Total tareas cargadas correctamente: {len(tareas)}")
        return tareas

    @classmethod
    def _cargar_tarea_desde_archivo(cls, ruta_archivo: Path) -> Optional[ITareaAgente]:
        """Intenta cargar una tarea desde un archivo python"""
        nombre_modulo = f"inspecciones_llm.tareas.{ruta_archivo.stem}"

        modulo = importlib.import_module(nombre_modulo)

        # Buscar todas las clases en el modulo que implementen ITareaAgente
        for nombre_atributo in dir(modulo):
            atributo = getattr(modulo, nombre_atributo)

            try:
                if (
                    isinstance(atributo, type)
                    and issubclass(atributo, ITareaAgente)
                    and atributo != ITareaAgente
                ):
                    # Encontramos una tarea valida, instanciarla
                    return atributo()
            except TypeError:
                continue

        return None


# ✅ Instancia global
cargador_tareas = CargadorTareas()
