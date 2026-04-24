"""
✅ Tarea especializada: Monitoreo Automatico VPS
Delegada exclusivamente al Agente Supervisor
"""

import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

ROOT_PROYECTO = Path(__file__).resolve().parents[2]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

from backend.apps.platform_config.application.services.remote_vps_health_check_service import (
    RemoteVpsHealthCheckService,
)
from backend.apps.platform_config.infrastructure.repositories.mongo_vps_health_check_repository import (
    MongoVpsHealthCheckRepository,
)

from inspecciones_llm.domain.interfaces.i_tarea_agente import ITareaAgente


class MonitoreoVpsAutomatico(ITareaAgente):
    """
    🩺 Doctor del VPS
    Esta es la tarea que delegamos completamente al tercer miembro del equipo

    Responsabilidades:
    ✅ Ejecutar Health Check automaticamente cada 5 minutos
    ✅ Guardar metricas en MongoDB
    ✅ Controlar tamaño de la coleccion
    ✅ Crear backups automaticos cuando supere umbral
    ✅ Solicitar aprobacion antes de limpiar
    ✅ Mantener historial completo
    """

    UMBRAL_REGISTROS_ALERTA = 10000
    UMBRAL_MB_ALERTA = 50

    @property
    def id(self) -> str:
        return "monitoreo_vps_automatico"

    @property
    def nombre(self) -> str:
        return "Monitoreo Automatico VPS Principal"

    @property
    def descripcion(self) -> str:
        return "Ejecuta Health Check cada 5 minutos, guarda metricas y controla tamaño de coleccion MongoDB"

    @property
    def intervalo_segundos(self) -> int:
        return 300  # 5 minutos

    def __init__(self):
        self.servicio = RemoteVpsHealthCheckService()
        self.repositorio = MongoVpsHealthCheckRepository()
        self.ultimo_aviso = None
        self.intervalo_aviso_horas = 24

    async def ejecutar(self) -> None:
        """Ejecuta un ciclo completo de monitoreo"""
        logger.info("🔍 Iniciando ciclo de monitoreo VPS automatico")

        try:
            # 1. Ejecutar Health Check contra VPS
            resultado = await self.servicio.execute_on_remote_vps()

            if not resultado.success:
                logger.warning("⚠️ Health Check reporto anomalias en el VPS")

            # 2. Verificar estado de la coleccion MongoDB
            await self._verificar_tamano_coleccion()

            logger.success("✅ Ciclo monitoreo VPS completado correctamente")

        except Exception as e:
            logger.exception(f"🔥 Error en ciclo de monitoreo VPS: {str(e)}")

    async def _verificar_tamano_coleccion(self) -> None:
        """Verifica el tamaño actual de la coleccion y actua segun corresponda"""
        total_registros = await self.repositorio.contar_total()
        tamano_mb = await self.repositorio.obtener_tamano_mb()

        logger.debug(
            f"📊 Estado coleccion Health Check: {total_registros} registros | {tamano_mb:.2f} MB"
        )

        # Verificar si superamos los umbrales
        supera_umbral = (
            total_registros >= self.UMBRAL_REGISTROS_ALERTA
            or tamano_mb >= self.UMBRAL_MB_ALERTA
        )

        if supera_umbral:
            await self._manejar_coleccion_saturada(total_registros, tamano_mb)

    async def _manejar_coleccion_saturada(
        self, registros: int, tamano_mb: float
    ) -> None:
        """Maneja el caso cuando la coleccion ha alcanzado el limite"""

        # ✅ PASO 1: Crear backup automaticamente SIN PREGUNTAR
        ruta_backup = await self._crear_backup_automatico()

        # ✅ PASO 2: Verificar si ya avisamos recientemente
        ahora = datetime.now()
        if self.ultimo_aviso is not None:
            horas_desde_ultimo_aviso = (
                ahora - self.ultimo_aviso
            ).total_seconds() / 3600
            if horas_desde_ultimo_aviso < self.intervalo_aviso_horas:
                logger.debug(
                    f"⏱️  Ya se envio aviso hace {horas_desde_ultimo_aviso:.1f} horas, se volvera a avisar despues"
                )
                return

        self.ultimo_aviso = ahora

        # ✅ PASO 3: Avisar al desarrollador y esperar aprobacion
        logger.warning("\n" + "=" * 80)
        logger.warning("⚠️  ALERTA COLECCION MONGODB SATURADA")
        logger.warning(f"📊 Registros: {registros} / {self.UMBRAL_REGISTROS_ALERTA}")
        logger.warning(f"💾 Tamaño: {tamano_mb:.2f} MB / {self.UMBRAL_MB_ALERTA} MB")
        logger.warning(f"✅ Backup creado automaticamente en: {ruta_backup}")
        logger.warning(
            "\n❓ ¿Deseas vaciar la coleccion y mantener solo los ultimos 30 dias?"
        )
        logger.warning(
            "👉 Responde 'SI' para confirmar, cualquier otra respuesta se ignora"
        )
        logger.warning("=" * 80 + "\n")

        # Aqui implementaremos el flujo de aprobacion interactivo
        # Por ahora queda pendiente la confirmacion manual

    async def _crear_backup_automatico(self) -> Path:
        """Crea un backup comprimido automatico de la coleccion"""
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"backup_vps_health_check_{fecha}.json.gz"
        ruta_backup = ROOT_PROYECTO / "data" / "backups" / nombre_archivo

        ruta_backup.parent.mkdir(parents=True, exist_ok=True)

        await self.repositorio.exportar_backup(ruta_backup)
        logger.success(f"📦 Backup automatico creado: {nombre_archivo}")

        return ruta_backup


# ✅ Instancia global para el agente
tarea_monitoreo_vps = MonitoreoVpsAutomatico()
