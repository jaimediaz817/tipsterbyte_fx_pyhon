from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.platform_config.domain.entities.scheduler_process_config import (
        ScheduledProcessConfig,
    )


def map_scheduled_process_config_from_model(model: object) -> "ScheduledProcessConfig":
    """
    Convierte un modelo SQL de ScheduledProcessConfig a entidad de dominio
    """
    from apps.platform_config.domain.entities.scheduler_process_config import (
        ScheduledProcessConfig,
    )

    return ScheduledProcessConfig(
        process_name=getattr(model, "process_name", ""),
        cron_expression=getattr(model, "cron_expression", ""),
        enabled=getattr(model, "enabled", False),
        description=getattr(model, "description", None),
        created_at=getattr(model, "created_at", None),
        updated_at=getattr(model, "updated_at", None),
    )
