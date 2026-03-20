# filepath: c:\Users\jdiaz\Documents\JDiaz-PC-DESKTOP-2\proyectos_jdiaz_pc_local\TIPSTERBYTE\tipsterByte_fx\backend\apps\leagues_manager\application\dto\detalle_fuente_extraccion_dto.py
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field


class DetalleFuenteExtraccionDTO(BaseModel):
    id: int
    torneo_id: int
    fuente_id: int
    url: HttpUrl
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # Puedes añadir campos para representar la 'fuente' o el 'torneo'
    # si necesitas datos anidados en este DTO. Por ejemplo:
    # fuente: FuenteExtraccionDTO # Requiere importar FuenteExtraccionDTO y manejar la recursión
    # torneo: TorneoDTO # Requiere importar TorneoDTO
