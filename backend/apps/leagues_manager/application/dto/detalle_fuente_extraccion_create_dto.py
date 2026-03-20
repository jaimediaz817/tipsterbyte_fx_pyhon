# filepath: c:\Users\jdiaz\Documents\JDiaz-PC-DESKTOP-2\proyectos_jdiaz_pc_local\TIPSTERBYTE\tipsterByte_fx\backend\apps\leagues_manager\application\dto\detalle_fuente_extraccion_create_dto.py
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field


class DetalleFuenteExtraccionCreateDTO(BaseModel):
    torneo_id: int
    fuente_id: int
    url: HttpUrl  # Asume que es una URL válida
    is_active: bool = True
    # Puedes añadir otros campos como fecha_ultima_extraccion si es necesario en el futuro
