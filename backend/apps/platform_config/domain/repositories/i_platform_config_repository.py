from abc import ABC, abstractmethod
from typing import Optional, List

from apps.platform_config.domain.entities.scheduler_process_config import ScheduledProcessConfig
from apps.platform_config.domain.entities.process import Process


class IPlatformConfigRepository(ABC):
    # ScheduledProcessConfig
    @abstractmethod
    def get_all_scheduled_process_configs(self, enabled_only: bool = False) -> List[ScheduledProcessConfig]: pass

    @abstractmethod
    def get_scheduled_process_config_by_name(self, process_name: str) -> Optional[ScheduledProcessConfig]: pass

    @abstractmethod
    def create_scheduled_process_config(self, process_name: str, cron_expression: str, enabled: bool, description: str | None) -> ScheduledProcessConfig: pass

    @abstractmethod
    def update_scheduled_process_config(self, process_name: str, data: dict) -> ScheduledProcessConfig: pass

    # Process
    @abstractmethod
    def get_all_processes(self, active_only: bool = False) -> List[Process]: pass

    @abstractmethod
    def get_process_by_code(self, code: str) -> Optional[Process]: pass

    @abstractmethod
    def create_process(self, code: str, name: str, is_active: bool, description: str | None) -> Process: pass

    @abstractmethod
    def update_process(self, code: str, data: dict) -> Process: pass