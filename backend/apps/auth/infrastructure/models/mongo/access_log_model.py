# filepath: c:\Users\JaimeIvanDiazGaona\Documents\proyectos_jdiaz\tipsterByte_fx\backend\apps\auth\infrastructure\models\mongo\access_log_model.py
from datetime import datetime, timezone
from uuid import UUID
from beanie import Document, Indexed
from pydantic import Field

from core.enums.enums_process_status import ProcessStatus

class AccessLog(Document):
    """
    Registra un evento de acceso de un usuario.
    Este documento vive en MongoDB y se relaciona con un usuario de PostgreSQL
    a través del campo 'user_id'.
    """
    user_id: UUID = Field(index=True)  # Clave foránea al ID del usuario en PostgreSQL. Indexado para búsquedas rápidas.
    ip_address: str
    user_agent: str
    process_name: str = Field(description="Nombre descriptivo del proceso o acción que se intenta guardar")
    # --- CAMBIO CLAVE: El tipo ahora es ProcessStatus y el default es el miembro del Enum ---
    process_status: ProcessStatus | None = Field(
        default=None,
        description="Estado del proceso (pending, completed, failed). Puede ser nulo"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "access_logs" # Nombre de la colección en MongoDB