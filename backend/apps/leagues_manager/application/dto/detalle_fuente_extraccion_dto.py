# filepath: c:\Users\jdiaz\Documents\JDiaz-PC-DESKTOP-2\proyectos_jdiaz_pc_local\TIPSTERBYTE\tipsterByte_fx\backend\apps\leagues_manager\application\dto\detalle_fuente_extraccion_dto.py
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field, ConfigDict


class DetalleFuenteExtraccionDTO(BaseModel):
    # id: int
    # torneo_id: int
    # fuente_id: int
    # url: HttpUrl
    # is_active: bool
    # created_at: datetime
    # updated_at: datetime
    id: int
    torneo_id: int
    fuente_id: int
    url: str = Field(..., max_length=500)
    is_active: bool
    process_id: int  # Campo para el ID del proceso
    created_at: datetime
    updated_at: datetime

    # Opcional: si quieres incluir los objetos relacionados
    # torneo: Optional[TorneoDTO] = None
    # fuente: Optional[FuenteExtraccionDTO] = None
    # process: Optional[ProcessDTO] = None

    model_config = ConfigDict(from_attributes=True)

    # Puedes añadir campos para representar la 'fuente' o el 'torneo'
    # si necesitas datos anidados en este DTO. Por ejemplo:
    # fuente: FuenteExtraccionDTO # Requiere importar FuenteExtraccionDTO y manejar la recursión
    # torneo: TorneoDTO # Requiere importar TorneoDTO
