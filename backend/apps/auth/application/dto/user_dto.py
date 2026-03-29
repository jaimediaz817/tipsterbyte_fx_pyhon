"""
DTO para representación de usuario
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class UserDTO(BaseModel):
    """
    DTO para representación de usuario

    Attributes:
        id: ID del usuario
        username: Nombre de usuario
        email: Email del usuario
        is_active: Si el usuario está activo
        created_at: Fecha de creación
        roles: Lista de roles del usuario
    """

    id: int = Field(..., description="ID del usuario", examples=[1])

    username: str = Field(..., description="Nombre de usuario", examples=["john_doe"])

    email: str = Field(
        ..., description="Email del usuario", examples=["john@example.com"]
    )

    is_active: bool = Field(
        default=True, description="Si el usuario está activo", examples=[True]
    )

    created_at: datetime = Field(
        ...,
        description="Fecha de creación del usuario",
        examples=["2024-01-01T00:00:00"],
    )

    roles: List[str] = Field(
        default_factory=list,
        description="Lista de roles del usuario",
        examples=[["user", "admin"]],
    )

    class Config:
        """Configuración del schema"""

        from_attributes = True  # Permite crear desde modelos ORM
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "roles": ["user"],
            }
        }
