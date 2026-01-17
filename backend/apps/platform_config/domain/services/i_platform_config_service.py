from abc import ABC, abstractmethod
from typing import List, Optional

from apps.platform_config.application.dto.process_create_dto import ProcessCreateDTO
from apps.platform_config.application.dto.process_dto import ProcessDTO
from apps.platform_config.application.dto.process_update_dto import ProcessUpdateDTO
from apps.platform_config.application.dto.scheduler_process_config_create_dto import ScheduledProcessConfigCreateDTO
from apps.platform_config.application.dto.scheduler_process_config_dto import ScheduledProcessConfigDTO
from apps.platform_config.application.dto.scheduler_process_config_update_dto import ScheduledProcessConfigUpdateDTO


class IPlatformConfigService(ABC):
    # ScheduledProcessConfig
    @abstractmethod
    def obtener_scheduled_process_configs(self, enabled_only: bool = False) -> List[ScheduledProcessConfigDTO]: pass

    @abstractmethod
    def obtener_scheduled_process_config(self, process_name: str) -> Optional[ScheduledProcessConfigDTO]: pass

    @abstractmethod
    def registrar_scheduled_process_config(self, dto: ScheduledProcessConfigCreateDTO, update: bool = False) -> ScheduledProcessConfigDTO: pass

    @abstractmethod
    def actualizar_scheduled_process_config(self, process_name: str, dto: ScheduledProcessConfigUpdateDTO) -> ScheduledProcessConfigDTO: pass

    # Process
    @abstractmethod
    def obtener_processes(self, active_only: bool = False) -> List[ProcessDTO]: pass

    @abstractmethod
    def obtener_process(self, code: str) -> Optional[ProcessDTO]: pass

    @abstractmethod
    def registrar_process(self, dto: ProcessCreateDTO, update: bool = False) -> ProcessDTO: pass

    @abstractmethod
    def actualizar_process(self, code: str, dto: ProcessUpdateDTO) -> ProcessDTO: pass