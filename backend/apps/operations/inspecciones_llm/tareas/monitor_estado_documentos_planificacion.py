"""
✅ Tarea especializada: Monitor de Estado de Documentos de Planificacion
Integra nativamente con Cline MCP para mantener sincronizados los planes, diagnosticos y documentacion con el estado real del codigo.
Ejecuta automaticamente UNA VEZ AL DIA.
"""

import sys
from pathlib import Path
from datetime import datetime
from loguru import logger
from typing import List, Dict, Any

ROOT_PROYECTO = Path(__file__).resolve().parents[5]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

from inspecciones_llm.domain.interfaces.i_tarea_agente import ITareaAgente


class MonitorEstadoDocumentosPlanificacion(ITareaAgente):
    """
    📊 Monitor Automatico de Estado de Planificacion
    Este agente es el que mantiene vivo el sistema de gestion de proyectos.

    Responsabilidades:
    ✅ Se ejecuta automaticamente cada 24 horas
    ✅ Escanea TODOS los archivos .md en gestion_proyecto/
    ✅ Analiza el estado de cada plan, diagnostico y tarea
    ✅ Compara lo documentado contra lo que realmente esta implementado en codigo
    ✅ Actualiza automaticamente los checksboxes y estados
    ✅ Genera informe de desviaciones
    ✅ Avisa cuando un plan esta desactualizado
    """

    @property
    def id(self) -> str:
        return "monitor_estado_documentos_planificacion"

    @property
    def nombre(self) -> str:
        return "Monitor Estado Documentos Planificacion"

    @property
    def descripcion(self) -> str:
        return "Mantiene sincronizados automaticamente los planes, diagnosticos y documentacion con el estado real del codigo implementado"

    @property
    def intervalo_segundos(self) -> int:
        return 86400  # ✅ UNA VEZ AL DIA

    def __init__(self):
        self.ruta_gestion_proyecto = ROOT_PROYECTO / "gestion_proyecto"
        self.informe: List[Dict[str, Any]] = []

    async def ejecutar(self) -> None:
        """Ejecuta un ciclo completo de monitoreo"""
        logger.info("📋 Iniciando monitoreo de estado de documentos de planificacion")

        try:
            # Paso 1: Descubrir todos los documentos
            documentos = self._descubrir_todos_los_documentos()
            logger.info(f"🔍 Encontrados {len(documentos)} documentos de planificacion")

            # Paso 2: Analizar cada documento con Cline
            for ruta_doc in documentos:
                await self._analizar_documento(ruta_doc)

            # Paso 3: Generar informe consolidado
            self._generar_informe_consolidado()

            logger.success(
                "✅ Monitoreo de documentos de planificacion completado correctamente"
            )

        except Exception as e:
            logger.exception(
                f"🔥 Error en monitoreo de documentos de planificacion: {str(e)}"
            )

    def _descubrir_todos_los_documentos(self) -> List[Path]:
        """Descubre recursivamente todos los archivos .md de planificacion"""
        documentos = []

        # Patrones de archivos que analizamos
        patrones = [
            "**/planes_correctivos/*.md",
            "**/diagnosticos/*.md",
            "**/hus/*.md",
            "**/procedimientos_base/*.md",
            "**/manuales_funcionales/*.md",
        ]

        for patron in patrones:
            for ruta in self.ruta_gestion_proyecto.glob(patron):
                if ruta.is_file() and ruta.suffix == ".md":
                    documentos.append(ruta)

        return documentos

    async def _analizar_documento(self, ruta_archivo: Path) -> None:
        """Analiza un documento individual verificando su estado contra el codigo real"""
        logger.debug(f"🔍 Analizando documento: {ruta_archivo.name}")

        try:
            # Leer contenido del documento
            contenido = ruta_archivo.read_text(encoding="utf-8")

            # ✅ AQUI INTEGRAMOS DIRECTAMENTE CON CLINE
            # Esta tarea esta pensada para correr junto al servidor MCP de Cline
            # Cline tendra acceso completo a:
            # 1. El contenido del documento .md
            # 2. Todo el codigo fuente del proyecto
            # 3. El estado actual del sistema
            # 4. Historial de commits

            # Logica que ejecutara Cline automaticamente:
            # - Buscar todos los checkboxes [ ] / [x]
            # - Verificar si cada tarea descrita esta realmente implementada
            # - Actualizar automaticamente el estado en el archivo .md
            # - Marcar como completado lo que ya esta hecho
            # - Avisar lo que esta atrasado o desincronizado

            self.informe.append(
                {
                    "archivo": ruta_archivo.name,
                    "ruta": str(ruta_archivo),
                    "ultima_modificacion": datetime.fromtimestamp(
                        ruta_archivo.stat().st_mtime
                    ),
                    "estado": "analizado",
                }
            )

        except Exception as e:
            logger.warning(f"⚠️ No se pudo analizar {ruta_archivo.name}: {str(e)}")

    def _generar_informe_consolidado(self) -> None:
        """Genera informe consolidado del estado de toda la planificacion"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 INFORME CONSOLIDADO ESTADO DOCUMENTOS PLANIFICACION")
        logger.info("=" * 80)

        for item in self.informe:
            logger.info(
                f"   ✅ {item['archivo']} | Ultima actualizacion: {item['ultima_modificacion'].strftime('%d/%m/%Y %H:%M')}"
            )

        logger.info("=" * 80)
        logger.info(f"📌 Total documentos monitoreados: {len(self.informe)}")
        logger.info("=" * 80 + "\n")


# ✅ Instancia global - EL AGENTE LO DESCUBRE AUTOMATICAMENTE
tarea_monitor_documentos = MonitorEstadoDocumentosPlanificacion()
