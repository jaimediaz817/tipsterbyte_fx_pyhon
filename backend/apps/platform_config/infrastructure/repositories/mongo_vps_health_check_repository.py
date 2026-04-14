"""
✅ IMPLEMENTACION CONCRETA REPOSITORIO MONGODB
✅ CUMPLE CONTRATO IVpsHealthCheckRepository
✅ FIRE AND FORGET: NO FALLA NUNCA
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from loguru import logger

from backend.apps.platform_config.domain.entities.vps_health_check import VpsHealthCheck
from backend.apps.platform_config.domain.repositories.i_vps_health_check_repository import (
    IVpsHealthCheckRepository,
)
from backend.apps.platform_config.infrastructure.models.mongo.vps_health_check_model import (
    VpsHealthCheckModel,
)


class MongoVpsHealthCheckRepository(IVpsHealthCheckRepository):
    """
    Implementacion concreta del repositorio usando MongoDB.

    ✅ Cumplimiento estricto del contrato de la interfaz
    ✅ Patrón Fire and Forget: Si la base de datos se cae NO FALLA la operacion principal
    ✅ Todas las excepciones son capturadas y logueadas
    ✅ Nunca rompe el flujo principal aunque no se pueda guardar
    """

    async def save(self, health_check: VpsHealthCheck) -> None:
        """
        Guarda el resultado de health check.
        NUNCA LANZA EXCEPCIONES. Siempre falla silenciosamente y loguea.
        """
        try:
            model = VpsHealthCheckModel(
                id=health_check.id,
                hostname=health_check.hostname,
                success=health_check.success,
                exit_code=health_check.exit_code,
                stdout=health_check.stdout,
                stderr=health_check.stderr,
                execution_time_seconds=health_check.execution_time_seconds,
                executed_at=health_check.executed_at,
                created_at=health_check.created_at,
                # ✅ NUEVO FORMATO ESTRUCTURADO
                ram=health_check.ram.__dict__,
                disk=health_check.disk.__dict__,
                cpu=health_check.cpu.__dict__,
                system_load=health_check.system_load.__dict__,
                process_count=health_check.process_count,
                uptime_seconds=health_check.uptime_seconds,
            )

            await model.save()
            logger.debug(f"💾 Guardado registro health check: {health_check}")

        except Exception as e:
            logger.error("❌ ❌ ❌ FALLO REPOSITORIO MONGODB ❌ ❌ ❌")
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Mensaje completo: {str(e)}")
            import traceback

            logger.error(f"Stacktrace: {traceback.format_exc()}")
            logger.error("⚠️  El registro NO SE GUARDÓ en MongoDB")
            # ✅ NUNCA propagamos la excepcion. El health check ya termino bien,
            #    que no se pueda guardar el log no es motivo para fallar la operacion.

    async def get_by_id(self, health_check_id: UUID) -> Optional[VpsHealthCheck]:
        try:
            model = await VpsHealthCheckModel.find_one(
                VpsHealthCheckModel.id == health_check_id
            )
            if not model:
                return None

            return self._map_to_entity(model)
        except Exception as e:
            logger.error(f"❌ Error consultando health check por id: {str(e)}")
            return None

    async def get_latest_for_hostname(
        self, hostname: str, limit: int = 10
    ) -> List[VpsHealthCheck]:
        try:
            models = (
                await VpsHealthCheckModel.find(VpsHealthCheckModel.hostname == hostname)
                .sort("-executed_at")
                .limit(limit)
                .to_list()
            )

            return [self._map_to_entity(model) for model in models]
        except Exception as e:
            logger.error(f"❌ Error consultando ultimos health check: {str(e)}")
            return []

    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime, hostname: Optional[str] = None
    ) -> List[VpsHealthCheck]:
        try:
            query = VpsHealthCheckModel.find(
                VpsHealthCheckModel.executed_at >= start_date,
                VpsHealthCheckModel.executed_at <= end_date,
            )

            if hostname:
                query = query.find(VpsHealthCheckModel.hostname == hostname)

            models = await query.sort("-executed_at").to_list()
            return [self._map_to_entity(model) for model in models]
        except Exception as e:
            logger.error(f"❌ Error consultando rango de fechas: {str(e)}")
            return []

    async def count_failures_last_hours(self, hostname: str, hours: int = 24) -> int:
        try:
            cutoff_date = datetime.utcnow() - timedelta(hours=hours)

            return await VpsHealthCheckModel.find(
                VpsHealthCheckModel.hostname == hostname,
                VpsHealthCheckModel.success == False,
                VpsHealthCheckModel.executed_at >= cutoff_date,
            ).count()
        except Exception as e:
            logger.error(f"❌ Error contando fallos: {str(e)}")
            return 0

    @staticmethod
    def _map_to_entity(model: VpsHealthCheckModel) -> VpsHealthCheck:
        """
        Mapea modelo de infraestructura a entidad de dominio
        """
        from backend.apps.platform_config.domain.entities.vps_health_check import (
            RamMetrics,
            DiskMetrics,
            CpuMetrics,
            SystemLoadMetrics,
        )

        # ✅ Construir Value Objects desde ESTRUCTURA ANIDADA NUEVA
        ram = RamMetrics(**model.ram) if model.ram else RamMetrics()
        disk = DiskMetrics(**model.disk) if model.disk else DiskMetrics()
        cpu = CpuMetrics(**model.cpu) if model.cpu else CpuMetrics()
        system_load = (
            SystemLoadMetrics(**model.system_load)
            if model.system_load
            else SystemLoadMetrics()
        )

        return VpsHealthCheck(
            id=UUID(str(model.id)),
            hostname=model.hostname,
            success=model.success,
            exit_code=model.exit_code,
            stdout=model.stdout,
            stderr=model.stderr,
            execution_time_seconds=model.execution_time_seconds,
            executed_at=model.executed_at,
            created_at=model.created_at,
            ram=ram,
            disk=disk,
            cpu=cpu,
            system_load=system_load,
            process_count=model.process_count,
            uptime_seconds=model.uptime_seconds,
        )
