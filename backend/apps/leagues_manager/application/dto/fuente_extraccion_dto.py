# filepath: c:\Users\jdiaz\Documents\JDiaz-PC-DESKTOP-2\proyectos_jdiaz_pc_local\TIPSTERBYTE\tipsterByte_fx\backend\apps\leagues_manager\application\dto\fuente_extraccion_dto.py
from datetime import datetime
from pydantic import BaseModel, Field
from apps.leagues_manager.domain.enums.robot_type_enum import (
    RobotTypeEnum,
)  # Importa el Enum


class FuenteExtraccionDTO(BaseModel):
    id: int
    name: str = Field(..., max_length=150)
    type: RobotTypeEnum
    descripcion: str | None = Field(None, max_length=255)
    is_active: bool
    created_at: datetime
    updated_at: datetime
