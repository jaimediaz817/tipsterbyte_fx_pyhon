# filepath: c:\Users\JaimeIvanDiazGaona\Documents\proyectos_jdiaz\tipsterByte_fx\backend\apps\auth\infrastructure\models\mongo\access_log_model.py
from datetime import datetime
from uuid import UUID
from beanie import Document, Indexed
from pydantic import Field

class AccessLog(Document):
    """
    Registra un evento de acceso de un usuario.
    Este documento vive en MongoDB y se relaciona con un usuario de PostgreSQL
    a través del campo 'user_id'.
    """
    user_id: UUID = Field(index=True)  # Clave foránea al ID del usuario en PostgreSQL. Indexado para búsquedas rápidas.
    ip_address: str
    user_agent: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "access_logs" # Nombre de la colección en MongoDB