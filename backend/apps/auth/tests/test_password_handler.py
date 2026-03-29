"""Tests para Password Handler v2.0 (Argon2id + bcrypt legacy)"""

import bcrypt
import pytest

from apps.auth.infrastructure.security.password_handler import PasswordHandler


class TestPasswordHandlerArgon2id:
    """Tests para hash con Argon2id (algoritmo principal)"""

    def test_hash_password_argon2id(self):
        """Test hash de contraseña con Argon2id"""
        password = "MiPassword123!"
        hashed = PasswordHandler.hash_password(password)
        assert hashed is not None
        assert hashed != password
        assert hashed.startswith("$argon2")

    def test_verify_password_argon2id_correct(self):
        """Test verificación correcta con Argon2id"""
        password = "MiPassword123!"
        hashed = PasswordHandler.hash_password(password)
        assert PasswordHandler.verify_password(password, hashed) is True

    def test_verify_password_argon2id_incorrect(self):
        """Test verificación incorrecta con Argon2id"""
        password = "MiPassword123!"
        hashed = PasswordHandler.hash_password(password)
        assert PasswordHandler.verify_password("Wrong123!", hashed) is False


class TestPasswordHandlerBcryptLegacy:
    """Tests para compatibilidad con hashes bcrypt legacy"""

    def test_verify_bcrypt_hash_still_works(self):
        """Test que hashes bcrypt existentes siguen funcionando"""
        password = "LegacyPassword123!"
        salt = bcrypt.gensalt()
        bcrypt_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
        assert PasswordHandler.verify_password(password, bcrypt_hash) is True

    def test_verify_bcrypt_wrong_password(self):
        """Test verificación incorrecta con hash bcrypt"""
        password = "LegacyPassword123!"
        salt = bcrypt.gensalt()
        bcrypt_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
        assert PasswordHandler.verify_password("WrongPassword!", bcrypt_hash) is False


class TestPasswordHandlerNeedsRehash:
    """Tests para detección de hashes que necesitan migración"""

    def test_needs_rehash_bcrypt(self):
        """Test que hash bcrypt necesita re-hash"""
        password = "TestPassword123!"
        salt = bcrypt.gensalt()
        bcrypt_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
        assert PasswordHandler.needs_rehash(bcrypt_hash) is True

    def test_needs_rehash_argon2id_current_config(self):
        """Test que hash Argon2id actual NO necesita re-hash"""
        password = "TestPassword123!"
        hashed = PasswordHandler.hash_password(password)
        assert PasswordHandler.needs_rehash(hashed) is False


class TestPasswordHandlerGetAlgorithm:
    """Tests para identificación de algoritmo"""

    def test_get_algorithm_argon2id(self):
        """Test identificación de Argon2id"""
        hashed = PasswordHandler.hash_password("Test123!")
        algo = PasswordHandler.get_hash_algorithm(hashed)
        assert algo == "argon2id"

    def test_get_algorithm_bcrypt(self):
        """Test identificación de bcrypt"""
        salt = bcrypt.gensalt()
        bcrypt_hash = bcrypt.hashpw(b"Test123!", salt).decode("utf-8")
        algo = PasswordHandler.get_hash_algorithm(bcrypt_hash)
        assert algo == "bcrypt"


class TestPasswordHandlerStrengthValidation:
    """Tests para validación de fortaleza de contraseña"""

    def test_is_strong_password_valid(self):
        """Test contraseña fuerte"""
        is_strong, errors = PasswordHandler.is_strong_password("MyStr0ng!Pass")
        assert is_strong is True
        assert len(errors) == 0

    def test_is_strong_password_too_short(self):
        """Test contraseña corta"""
        is_strong, errors = PasswordHandler.is_strong_password("Ab1!")
        assert is_strong is False
        assert any("8 caracteres" in e for e in errors)


class TestPasswordHandlerMigration:
    """Tests para flujo de migración bcrypt -> Argon2id"""

    def test_migration_flow(self):
        """Test flujo completo de migración"""
        password = "UserPassword123!"
        salt = bcrypt.gensalt()
        old_bcrypt_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

        # Login verifica correctamente con bcrypt
        assert PasswordHandler.verify_password(password, old_bcrypt_hash) is True
        # Sistema detecta que necesita migración
        assert PasswordHandler.needs_rehash(old_bcrypt_hash) is True

        # Sistema genera nuevo hash con Argon2id
        new_argon2id_hash = PasswordHandler.hash_password(password)
        assert new_argon2id_hash.startswith("$argon2")
        assert PasswordHandler.needs_rehash(new_argon2id_hash) is False
        assert PasswordHandler.verify_password(password, new_argon2id_hash) is True
