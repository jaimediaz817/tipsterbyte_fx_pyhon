"""
Password Handler v2.0 - Hash seguro de contraseñas
Usa Argon2id (OWASP recomendado) con soporte para migración de bcrypt legacy
"""

import os
from typing import Tuple

import bcrypt
from argon2 import PasswordHasher, Type
from argon2.exceptions import (
    HashingError,
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)
from loguru import logger


# ============================================================
# Configuración Argon2id (OWASP 2024 recomendado)
# ============================================================
ARGON2_TIME_COST = int(os.getenv("ARGON2_TIME_COST", "3"))  # Iteraciones
ARGON2_MEMORY_COST = int(os.getenv("ARGON2_MEMORY_COST", "65536"))  # 64MB
ARGON2_PARALLELISM = int(os.getenv("ARGON2_PARALLELISM", "4"))  # Hilos
ARGON2_HASH_LEN = 32  # 256 bits
ARGON2_SALT_LEN = 16  # 128 bits

# Instancia global del hasher Argon2id
_argon2_hasher = PasswordHasher(
    time_cost=ARGON2_TIME_COST,
    memory_cost=ARGON2_MEMORY_COST,
    parallelism=ARGON2_PARALLELISM,
    hash_len=ARGON2_HASH_LEN,
    salt_len=ARGON2_SALT_LEN,
    type=Type.ID,  # Argon2id - modo híbrido recomendado
)


class PasswordHandler:
    """
    Handler profesional para operaciones con contraseñas

    Funcionalidades:
    - Hash de contraseñas con Argon2id (OWASP recomendado)
    - Verificación de contraseñas con soporte multi-algoritmo
    - Migración automática de hashes bcrypt legacy
    - Validación de fortaleza de contraseña

    Algoritmos soportados:
    - Argon2id (principal) - $argon2id$...
    - bcrypt (legacy) - $2b$... / $2a$...
    """

    # ============================================================
    # Métodos públicos
    # ============================================================

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Genera un hash Argon2id de la contraseña

        Args:
            password: Contraseña en texto plano

        Returns:
            Hash de la contraseña como string (formato $argon2id$...)

        Raises:
            ValueError: Si la contraseña está vacía
            HashingError: Si ocurre un error durante el hashing

        Example:
            hashed = PasswordHandler.hash_password("mi_contraseña_segura")
        """
        if not password:
            raise ValueError("La contraseña no puede estar vacía")

        try:
            hashed = _argon2_hasher.hash(password)
            logger.debug("✅ Contraseña hasheada exitosamente con Argon2id")
            return hashed

        except HashingError as e:
            logger.error(f"❌ Error al hashear contraseña con Argon2id: {e}")
            raise

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash

        Soporta tanto Argon2id (nuevo) como bcrypt (legacy).
        Si detecta un hash bcrypt válido, lo verifica y retorna True,
        permitiendo la migración transparente en el siguiente login.

        Args:
            plain_password: Contraseña en texto plano
            hashed_password: Hash almacenado en la base de datos

        Returns:
            True si la contraseña coincide, False en caso contrario

        Example:
            is_valid = PasswordHandler.verify_password("mi_password", hashed)
        """
        if not plain_password or not hashed_password:
            logger.warning("⚠️ Contraseña o hash vacío en verificación")
            return False

        # Detectar tipo de hash y verificar
        if PasswordHandler._is_bcrypt_hash(hashed_password):
            return PasswordHandler._verify_bcrypt(plain_password, hashed_password)

        # Hash Argon2id (formato actual)
        return PasswordHandler._verify_argon2id(plain_password, hashed_password)

    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        """
        Verifica si un hash necesita ser actualizado

        Útil para migración progresiva: si el hash es de bcrypt,
        indica que debe ser re-hasheado con Argon2id en el próximo login.

        Args:
            hashed_password: Hash almacenado en la base de datos

        Returns:
            True si el hash necesita ser actualizado

        Example:
            if PasswordHandler.needs_rehash(stored_hash):
                new_hash = PasswordHandler.hash_password(password)
                # Actualizar en BD
        """
        if not hashed_password:
            return True

        # Hash bcrypt necesita migración
        if PasswordHandler._is_bcrypt_hash(hashed_password):
            logger.debug("🔄 Hash bcrypt detectado - necesita migración a Argon2id")
            return True

        # Verificar si el hash Argon2id cumple con la configuración actual
        try:
            return _argon2_hasher.check_needs_rehash(hashed_password)
        except InvalidHashError:
            logger.warning("⚠️ Hash inválido detectado - necesita re-hash")
            return True

    @staticmethod
    def is_strong_password(password: str) -> Tuple[bool, list[str]]:
        """
        Verifica si una contraseña cumple con criterios de seguridad

        Args:
            password: Contraseña a verificar

        Returns:
            Tupla (es_fuerte, lista_de_errores)

        Example:
            is_strong, errors = PasswordHandler.is_strong_password("abc123")
            if not is_strong:
                print(errors)  # ['Mínimo 8 caracteres', 'Incluir mayúsculas']
        """
        errors = []

        # Longitud mínima
        if len(password) < 8:
            errors.append("Mínimo 8 caracteres")

        # Al menos una mayúscula
        if not any(c.isupper() for c in password):
            errors.append("Incluir al menos una letra mayúscula")

        # Al menos una minúscula
        if not any(c.islower() for c in password):
            errors.append("Incluir al menos una letra minúscula")

        # Al menos un número
        if not any(c.isdigit() for c in password):
            errors.append("Incluir al menos un número")

        # Al menos un carácter especial
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            errors.append("Incluir al menos un carácter especial (!@#$%^&*...)")

        is_strong = len(errors) == 0

        if is_strong:
            logger.debug("✅ Contraseña cumple criterios de seguridad")
        else:
            logger.warning(f"⚠️ Contraseña débil: {', '.join(errors)}")

        return is_strong, errors

    @staticmethod
    def get_hash_algorithm(hashed_password: str) -> str:
        """
        Identifica el algoritmo usado para generar un hash

        Args:
            hashed_password: Hash almacenado en la base de datos

        Returns:
            Nombre del algoritmo: 'argon2id', 'bcrypt', o 'unknown'

        Example:
            algo = PasswordHandler.get_hash_algorithm(stored_hash)
            # 'argon2id' o 'bcrypt'
        """
        if not hashed_password:
            return "unknown"

        if hashed_password.startswith("$argon2"):
            return "argon2id"

        if PasswordHandler._is_bcrypt_hash(hashed_password):
            return "bcrypt"

        return "unknown"

    # ============================================================
    # Métodos privados
    # ============================================================

    @staticmethod
    def _is_bcrypt_hash(hashed_password: str) -> bool:
        """Detecta si un hash es de tipo bcrypt"""
        return hashed_password.startswith(("$2b$", "$2a$", "$2y$"))

    @staticmethod
    def _verify_argon2id(plain_password: str, hashed_password: str) -> bool:
        """Verifica contraseña contra hash Argon2id"""
        try:
            _argon2_hasher.verify(hashed_password, plain_password)
            logger.debug("✅ Contraseña verificada correctamente con Argon2id")
            return True

        except VerifyMismatchError:
            logger.warning("⚠️ Contraseña incorrecta (Argon2id)")
            return False

        except (VerificationError, InvalidHashError) as e:
            logger.error(f"❌ Error al verificar contraseña Argon2id: {e}")
            return False

    @staticmethod
    def _verify_bcrypt(plain_password: str, hashed_password: str) -> bool:
        """Verifica contraseña contra hash bcrypt (legacy)"""
        try:
            is_valid = bcrypt.checkpw(
                plain_password.encode("utf-8"), hashed_password.encode("utf-8")
            )

            if is_valid:
                logger.info(
                    "✅ Contraseña verificada con bcrypt (legacy) - "
                    "considerar migración a Argon2id"
                )
            else:
                logger.warning("⚠️ Contraseña incorrecta (bcrypt legacy)")

            return is_valid

        except Exception as e:
            logger.error(f"❌ Error al verificar contraseña bcrypt: {e}")
            return False
