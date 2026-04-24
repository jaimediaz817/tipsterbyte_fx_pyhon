from apps.platform_config.application.dto.scheduler_process_config_create_dto import (
    ScheduledProcessConfigCreateDTO,
)
from apps.platform_config.application.services.platform_config_service import (
    PlatformConfigService,
)
from apps.platform_config.infrastructure.repositories.sql_platform_config_repository import (
    SQLPlatformConfigRepository,
)
from apps.platform_config.application.dto.process_create_dto import ProcessCreateDTO
from scripts.db.seeders.base_seeder import BaseSeeder
from shared.constants.process.process_codes import (
    PROCESS_CALENDAR_EXTRACTION,
    PROCESS_EXTRACT_DATA_FUENTES,
    PROCESS_LOG_CLEANUP,
    PROCESS_ODDS_WPLAY_EXTRACTION,
    PROCESS_STANDINGS_EXTRACTION,
)


# Datos a poblar
SCHEDULED_PROCESSES = [
    {
        "process_name": PROCESS_EXTRACT_DATA_FUENTES,
        # "cron_expression": "0 */2 * * *", # Cada 2 horas
        "cron_expression": "* * * * *",  # Diariamente a medianoche
        "enabled": True,
        "description": "Proceso programado para extraer datos de fuentes deportivas (standings, odds, etc.).",
    },
    {
        "process_name": PROCESS_LOG_CLEANUP,
        "cron_expression": "* * * * *",  # Cada minuto (para testing)
        "enabled": True,
        "description": "Limpieza automática de logs: archiva >3 días, elimina >30 días. Auditoría en cleanup_history.json.",
    },
]

PROCESSES = [
    {
        "code": PROCESS_EXTRACT_DATA_FUENTES,
        "name": "Orquestador de Rastreo de Datos de Fuentes Deportivas (General)",
        "is_active": True,
        "description": "Proceso principal que orquesta la extracción de datos de diversas fuentes deportivas. Usado como proceso por defecto para detalles de fuentes.",
    },
    {
        "code": PROCESS_LOG_CLEANUP,
        "name": "Limpieza Automatica de Logs",
        "is_active": True,
        "description": "Proceso automatico que archiva logs antiguos y limpia el sistema de logging.",
    },
    {
        "code": PROCESS_STANDINGS_EXTRACTION,
        "name": "Extracción de Tablas de Posiciones",
        "is_active": True,
        "description": "Proceso dedicado a la extracción de datos de tablas de posiciones (standings) de diversas fuentes.",
    },
    {
        "code": PROCESS_ODDS_WPLAY_EXTRACTION,
        "name": "Extracción de Cuotas Deportivas (WPlay)",
        "is_active": True,
        "description": "Proceso dedicado a la extracción de cuotas de apuestas de la casa WPlay.",
    },
    {
        "code": PROCESS_CALENDAR_EXTRACTION,
        "name": "Extracción de Calendarios de Torneos",
        "is_active": True,
        "description": "Proceso dedicado a la extracción de calendarios de partidos y eventos de torneos.",
    },
]


class PlatformConfigSeeder(BaseSeeder):
    """Puebla la base de datos con configuraciones iniciales del módulo Platform Config."""

    def run(self, update: bool = False):
        self.logger.info("🌱 Ejecutando seeder del módulo Platform Config...")

        # ✅ VALIDACION AUTOMATICA DE CONSISTENCIA ANTES DE INSERTAR NADA
        for sp in SCHEDULED_PROCESSES:
            assert any(
                p["code"] == sp["process_name"] for p in PROCESSES
            ), f"❌ INCONSISTENCIA: Proceso {sp['process_name']} no existe en PROCESSES"

        import sys
        from shared.constants.process import process_codes

        for p in PROCESSES:
            constante_nombre = f"PROCESS_{p['code'].upper()}"
            assert hasattr(
                process_codes, constante_nombre
            ), f"❌ INCONSISTENCIA: Proceso {p['code']} no existe en process_codes.py (constante esperada: {constante_nombre})"

        try:
            repo = SQLPlatformConfigRepository(self.db)
            service = PlatformConfigService(repo)

            self._seed_processes(service, update=update)
            self._seed_scheduled_processes(service, update=update)

            self.db.commit()
            self.logger.success("✅ Seeder de Platform Config completado exitosamente.")
        except Exception as e:
            self.logger.error(f"❌ Error durante el seeder de Platform Config: {e}")
            self.db.rollback()
            raise

    def _seed_scheduled_processes(
        self, service: PlatformConfigService, update: bool = False
    ):
        self.logger.info(
            "Verificando y poblando configuraciones de procesos programados..."
        )
        for process_data in SCHEDULED_PROCESSES:
            dto = ScheduledProcessConfigCreateDTO(**process_data)
            service.registrar_scheduled_process_config(dto, update=update)

    def _seed_processes(self, service: PlatformConfigService, update: bool = False):
        self.logger.info("Verificando y poblando procesos...")
        for process_data in PROCESSES:
            dto = ProcessCreateDTO(**process_data)
            service.registrar_process(dto, update=update)
