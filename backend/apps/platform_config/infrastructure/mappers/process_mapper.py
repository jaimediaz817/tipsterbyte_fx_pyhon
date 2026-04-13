from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from apps.platform_config.domain.entities.process import Process


def map_process_from_model(process_model: Optional[object]) -> Optional["Process"]:
    """
    Convierte un modelo SQL de Process a entidad de dominio
    """
    from apps.platform_config.domain.entities.process import Process

    if not process_model:
        return None

    return Process(
        id=(
            getattr(process_model, "id", 0)
            if getattr(process_model, "id", None) is not None
            else 0
        ),
        code=getattr(process_model, "code", ""),
        name=getattr(process_model, "name", ""),
        is_active=getattr(process_model, "is_active", False),
        description=getattr(process_model, "description", None),
        created_at=getattr(process_model, "created_at", None),
        updated_at=getattr(process_model, "updated_at", None),
    )
