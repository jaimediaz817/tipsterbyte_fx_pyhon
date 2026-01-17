from sqlalchemy.orm import Session
from apps.platform_config.domain.entities.scheduler_process_config import ScheduledProcessConfig
from apps.platform_config.domain.entities.process import Process
from apps.platform_config.domain.repositories.i_platform_config_repository import IPlatformConfigRepository
from apps.platform_config.infrastructure.models.sql.scheduled_process_config import ScheduledProcessConfig as ScheduledProcessConfigModel
from apps.platform_config.infrastructure.models.sql.process import Process as ProcessModel
from shared.utils.db.sql.sqlalchemy_utils import update_from_dict


class SQLPlatformConfigRepository(IPlatformConfigRepository):
    def __init__(self, db: Session):
        self.db = db

    # --- mappers ---
    def _to_scheduled_process_config(self, m: ScheduledProcessConfig) -> ScheduledProcessConfig:
        return ScheduledProcessConfig(
            process_name=m.process_name,
            cron_expression=m.cron_expression,
            enabled=m.enabled,
            description=m.description,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    def _to_process(self, m: ProcessModel) -> Process:
        return Process(
            id=m.id,
            code=m.code,
            name=m.name,
            is_active=m.is_active,
            description=m.description,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    # --- ScheduledProcessConfig ---
    def get_all_scheduled_process_configs(self, enabled_only: bool = False):
        q = self.db.query(ScheduledProcessConfigModel)
        if enabled_only:
            q = q.filter(ScheduledProcessConfigModel.enabled.is_(True))
        return [self._to_scheduled_process_config(m) for m in q.all()]

    def get_scheduled_process_config_by_name(self, process_name: str):
        m = self.db.query(ScheduledProcessConfigModel).filter(
            ScheduledProcessConfigModel.process_name == process_name
        ).first()
        return self._to_scheduled_process_config(m) if m else None

    def create_scheduled_process_config(self, process_name: str, cron_expression: str, enabled: bool, description: str | None):
        m = ScheduledProcessConfigModel(
            process_name=process_name,
            cron_expression=cron_expression,
            enabled=enabled,
            description=description,
        )
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._to_scheduled_process_config(m)

    def update_scheduled_process_config(self, process_name: str, data: dict):
        obj = self.db.query(ScheduledProcessConfigModel).filter(
            ScheduledProcessConfigModel.process_name == process_name
        ).first()
        if not obj:
            raise ValueError("ScheduledProcessConfig no encontrado")
        update_from_dict(obj, data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_scheduled_process_config(obj)

    # --- Process ---
    def get_all_processes(self, active_only: bool = False):
        q = self.db.query(ProcessModel)
        if active_only:
            q = q.filter(ProcessModel.is_active.is_(True))
        return [self._to_process(m) for m in q.all()]

    def get_process_by_code(self, code: str):
        m = self.db.query(ProcessModel).filter(ProcessModel.code == code).first()
        return self._to_process(m) if m else None

    def create_process(self, code: str, name: str, is_active: bool, description: str | None):
        m = ProcessModel(
            code=code,
            name=name,
            is_active=is_active,
            description=description,
        )
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._to_process(m)

    def update_process(self, code: str, data: dict):
        obj = self.db.query(ProcessModel).filter(ProcessModel.code == code).first()
        if not obj:
            raise ValueError("Process no encontrado")
        update_from_dict(obj, data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_process(obj)