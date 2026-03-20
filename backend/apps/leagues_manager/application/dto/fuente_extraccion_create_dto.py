# filepath: c:\Users\jdiaz\Documents\JDiaz-PC-DESKTOP-2\proyectos_jdiaz_pc_local\TIPSTERBYTE\tipsterByte_fx\backend\apps\leagues_manager\application\dto\fuente_extraccion_create_dto.py
from pydantic import BaseModel, Field
from apps.leagues_manager.domain.enums.robot_type_enum import (
    RobotTypeEnum,
)  # Importa el Enum


class FuenteExtraccionCreateDTO(BaseModel):
    name: str = Field(..., max_length=150)
    type: RobotTypeEnum  # Usa el Enum directamente
    descripcion: str | None = Field(None, max_length=255)
    is_active: bool = True
