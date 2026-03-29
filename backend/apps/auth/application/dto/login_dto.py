"""
DTO para solicitud de login
"""

from pydantic import BaseModel, Field


class LoginDTO(BaseModel):
    """
    DTO para solicitud de inicio de sesión

    Attributes:
        username: Nombre de usuario o email
        password: Contraseña del usuario
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nombre de usuario o email",
        examples=["john_doe", "john@example.com"],
    )

    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Contraseña del usuario",
        examples=["MiPassword123!"],
    )

    class Config:
        """Configuración del schema"""

        json_schema_extra = {
            "example": {"username": "john_doe", "password": "MiPassword123!"}
        }
