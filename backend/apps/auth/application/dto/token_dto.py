"""
DTO para respuesta de tokens JWT
"""

from pydantic import BaseModel, Field


class TokenDTO(BaseModel):
    """
    DTO para respuesta de tokens JWT

    Attributes:
        access_token: Token de acceso JWT
        refresh_token: Token de refresh JWT
        token_type: Tipo de token (bearer)
        expires_in: Segundos hasta expiración del access token
    """

    access_token: str = Field(
        ...,
        description="Token de acceso JWT",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )

    refresh_token: str = Field(
        ...,
        description="Token de refresh JWT (mayor duración)",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )

    token_type: str = Field(
        default="bearer", description="Tipo de token", examples=["bearer"]
    )

    expires_in: int = Field(
        default=1800,
        description="Segundos hasta expiración del access token (default: 30 min)",
        examples=[1800],
    )

    class Config:
        """Configuración del schema"""

        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwidHlwZSI6InJlZnJlc2giLCJpYXQiOjE1MTYyMzkwMjJ9.4Adcj3UFfjgOWJGLoXy8DEu5-7FYVlKPxRZjOXBXgBE",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        }
