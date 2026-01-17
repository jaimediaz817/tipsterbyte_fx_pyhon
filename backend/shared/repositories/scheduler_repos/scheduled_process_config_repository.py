from sqlalchemy.orm import Session
from apps.platform_config.infrastructure.models.sql.scheduled_process_config import ScheduledProcessConfig
from loguru import logger
# from db.models.scheduled_process_config import ScheduledProcessConfig

class ScheduledProcessConfigRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_enabled(self) -> list[ScheduledProcessConfig]:
        """Obtiene todas las configuraciones de procesos programados que están habilitadas.

        Returns:
            list[ScheduledProcessConfig]: Lista de configuraciones habilitadas.
        """
        
        # Retorna todas las configuraciones de procesos programados que están habilitadas
        # TODO: PENDIENTE: Corregir si es necesario
        # return self.db.query(ScheduledProcessConfig).filter(ScheduledProcessConfig.enabled == True).all()
        enabled_jobs = self.db.query(ScheduledProcessConfig).filter(ScheduledProcessConfig.enabled).all()
        logger.success(f"✅ Se encontraron {len(enabled_jobs)} jobs habilitados en la base de datos.")
        return enabled_jobs