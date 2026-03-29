"""
DTOs (Data Transfer Objects) para el módulo de autenticación
Define los esquemas de entrada y salida para los endpoints de auth
"""

from .login_dto import LoginDTO
from .register_dto import RegisterDTO
from .token_dto import TokenDTO
from .user_dto import UserDTO

__all__ = [
    "LoginDTO",
    "RegisterDTO",
    "TokenDTO",
    "UserDTO",
]
