from apps.platform_config.application.dto.scheduler_process_config_create_dto import ScheduledProcessConfigCreateDTO
from apps.platform_config.application.services.platform_config_service import PlatformConfigService
from apps.platform_config.infrastructure.repositories.sql_platform_config_repository import SQLPlatformConfigRepository
from apps.platform_config.application.dto.process_create_dto import ProcessCreateDTO
from scripts.db.seeders.base_seeder import BaseSeeder
from shared.constants.process.process_codes import (
    SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS,
    PROCESS_CUOTAS_WPLAY
)

# Datos a poblar
SCHEDULED_PROCESSES = [
    {
        "process_name": SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS,
        # "cron_expression": "0 */2 * * *", # Cada 2 horas
        "cron_expression": "* * * * *", # Diariamente a medianoche
        "enabled": True,
        "description": "Proceso programado para extraer datos de fuentes deportivas (standings, odds, etc.)."
    }
]

PROCESSES = [
    {
        "code": PROCESS_CUOTAS_WPLAY,
        "name": "Ingesta y procesamiento de cuotas WPlay",
        "is_active": True,
        "description": "Extrae cuotas WPlay, normaliza datos, calcula métricas y prepara salidas."
    },
]


class PlatformConfigSeeder(BaseSeeder):
    """Puebla la base de datos con configuraciones iniciales del módulo Platform Config."""

    def run(self, update: bool = False):
        self.logger.info("🌱 Ejecutando seeder del módulo Platform Config...")
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

    def _seed_scheduled_processes(self, service: PlatformConfigService, update: bool = False):
        self.logger.info("Verificando y poblando configuraciones de procesos programados...")
        for process_data in SCHEDULED_PROCESSES:
            dto = ScheduledProcessConfigCreateDTO(**process_data)
            service.registrar_scheduled_process_config(dto, update=update)
            
    def _seed_processes(self, service: PlatformConfigService, update: bool = False):
        self.logger.info("Verificando y poblando procesos...")
        for process_data in PROCESSES:
            dto = ProcessCreateDTO(**process_data)
            service.registrar_process(dto, update=update)   
                
# TODO: tb-hu-refactors-block-01: pendiente quitar:
    # """Puebla la base de datos con configuraciones iniciales para el módulo de gestión de ligas."""

    # def run(self,  update: bool = False):
    #     self.logger.info("🌱 Ejecutando seeder del módulo Leagues Manager...")
    #     try:
    #         self._seed_scheduled_processes(update=update)
    #         self.db.commit()
    #         self.logger.success("✅ Seeder de Leagues Manager completado exitosamente.")
    #     except Exception as e:
    #         self.logger.error(f"❌ Error durante el seeder de Leagues Manager: {e}")
    #         self.db.rollback()
    #         raise

    # def _seed_scheduled_processes(self, update=False):
        
    #     self.logger.info("Verificando y poblando configuraciones de procesos programados...")
    #     for process_data in SCHEDULED_PROCESSES:
    #         process = self.db.query(ScheduledProcessConfig).filter(ScheduledProcessConfig.process_name == process_data["process_name"]).first()
    #         if not process:
    #             new_process = ScheduledProcessConfig(**process_data)
    #             self.db.add(new_process)
    #             self.logger.info(f"Proceso programado '{process_data['process_name']}' creado.")

    #         # --- ¡LÓGICA DE ACTUALIZACIÓN SIMPLIFICADA! ---
    #         elif update:
    #             self.logger.info(f"Actualizando proceso programado '{process_data['process_name']}'...")
    #             update_from_dict(process, process_data)        
    #         else:
    #             self.logger.trace(f"Proceso programado '{process_data['process_name']}' ya existe, omitiendo.")
