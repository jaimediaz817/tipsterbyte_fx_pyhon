"""
DTO para solicitud de registro de usuario
"""

from pydantic import BaseModel, Field, EmailStr


class RegisterDTO(BaseModel):
    """
    DTO para solicitud de registro de nuevo usuario

    Attributes:
        username: Nombre de usuario único
        email: Email del usuario
        password: Contraseña del usuario
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nombre de usuario único",
        examples=["john_doe"],
    )

    email: EmailStr = Field(
        ..., description="Email del usuario", examples=["john@example.com"]
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Contraseña del usuario (mínimo 8 caracteres)",
        examples=["MiPassword123!"],
    )

    class Config:
        """Configuración del schema"""

        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "MiPassword123!",
            }
        }
