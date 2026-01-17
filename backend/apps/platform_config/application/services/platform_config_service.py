# from apps.platform_config.domain.repositories.i_platform_config_repository import IPlatformConfigRepository
# from apps.platform_config.domain.services.i_platform_config_service import IPlatformConfigService

# from apps.platform_config.application.dto.scheduled_process_config_create_dto import ScheduledProcessConfigCreateDTO
# from apps.platform_config.application.dto.scheduled_process_config_update_dto import ScheduledProcessConfigUpdateDTO
# from apps.platform_config.application.dto.scheduled_process_config_dto import ScheduledProcessConfigDTO

# from apps.platform_config.application.dto.process_create_dto import ProcessCreateDTO
# from apps.platform_config.application.dto.process_update_dto import ProcessUpdateDTO
# from apps.platform_config.application.dto.process_dto import ProcessDTO


from apps.platform_config.application.dto.process_create_dto import ProcessCreateDTO
from apps.platform_config.application.dto.process_dto import ProcessDTO
from apps.platform_config.application.dto.process_update_dto import ProcessUpdateDTO
from apps.platform_config.application.dto.scheduler_process_config_create_dto import ScheduledProcessConfigCreateDTO
from apps.platform_config.application.dto.scheduler_process_config_dto import ScheduledProcessConfigDTO
from apps.platform_config.application.dto.scheduler_process_config_update_dto import ScheduledProcessConfigUpdateDTO
from apps.platform_config.domain.repositories.i_platform_config_repository import IPlatformConfigRepository
from apps.platform_config.domain.services.i_platform_config_service import IPlatformConfigService
# from apps.platform_config.domain.services.i_platform_config_service import IPlatformConfigService


class PlatformConfigService(IPlatformConfigService):
    def __init__(self, repo: IPlatformConfigRepository):
        self.repo = repo

    # --- ScheduledProcessConfig ---
    def obtener_scheduled_process_configs(self, enabled_only: bool = False):
        configs = self.repo.get_all_scheduled_process_configs(enabled_only=enabled_only)
        return [ScheduledProcessConfigDTO(**c.__dict__) for c in configs]

    def obtener_scheduled_process_config(self, process_name: str):
        c = self.repo.get_scheduled_process_config_by_name(process_name)
        return ScheduledProcessConfigDTO(**c.__dict__) if c else None

    def registrar_scheduled_process_config(self, dto: ScheduledProcessConfigCreateDTO, update: bool = False):
        existing = self.repo.get_scheduled_process_config_by_name(dto.process_name)
        if existing:
            if update:
                updated = self.repo.update_scheduled_process_config(
                    dto.process_name, dto.model_dump()
                )
                return ScheduledProcessConfigDTO(**updated.__dict__)
            return ScheduledProcessConfigDTO(**existing.__dict__)
        created = self.repo.create_scheduled_process_config(
            dto.process_name, dto.cron_expression, dto.enabled, dto.description
        )
        return ScheduledProcessConfigDTO(**created.__dict__)

    def actualizar_scheduled_process_config(self, process_name: str, dto: ScheduledProcessConfigUpdateDTO):
        data = dto.model_dump(exclude_unset=True)
        updated = self.repo.update_scheduled_process_config(process_name, data)
        return ScheduledProcessConfigDTO(**updated.__dict__)

    # --- Process ---
    def obtener_processes(self, active_only: bool = False):
        processes = self.repo.get_all_processes(active_only=active_only)
        return [ProcessDTO(**p.__dict__) for p in processes]

    def obtener_process(self, code: str):
        p = self.repo.get_process_by_code(code)
        return ProcessDTO(**p.__dict__) if p else None

    def registrar_process(self, dto: ProcessCreateDTO, update: bool = False):
        existing = self.repo.get_process_by_code(dto.code)
        if existing:
            if update:
                updated = self.repo.update_process(dto.code, dto.model_dump())
                return ProcessDTO(**updated.__dict__)
            return ProcessDTO(**existing.__dict__)
        created = self.repo.create_process(dto.code, dto.name, dto.is_active, dto.description)
        return ProcessDTO(**created.__dict__)

    def actualizar_process(self, code: str, dto: ProcessUpdateDTO):
        data = dto.model_dump(exclude_unset=True)
        updated = self.repo.update_process(code, data)
        return ProcessDTO(**updated.__dict__)