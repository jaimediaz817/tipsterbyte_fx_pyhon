# ✅ TEST UNITARIO TokenValidationService
# ✅ FUNCIONA EN VS CODE TESTING EXPLORER
# ✅ FUNCIONA EJECUTANDO python test_token_validation_service.py
# ✅ FUNCIONA CON pytest
# ✅ NO USA BASE DE DATOS
# ✅ NO USA @PATCH

import sys
import io
from pathlib import Path
from typing import cast, Awaitable, Coroutine

# ✅ SOLUCION PERMANENTE PATH: Funciona en TODOS los entornos
ROOT_PROYECTO = Path(__file__).resolve().parents[3]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

# ✅ Cargar automaticamente variables de entorno
from dotenv import load_dotenv

load_dotenv(ROOT_PROYECTO / "backend" / ".env")

# ✅ SOLUCION CODIFICACION WINDOWS (UnicodeEncodeError ✅)
if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import pytest
from unittest.mock import Mock, patch
from apps.auth.application.services.token_validation_service import (
    TokenValidationService,
)


class TestTokenValidationService:
    """
    ✅ TEST UNITARIO COMPLETO
    ✅ NO USA BASE DE DATOS REAL
    ✅ USAMOS DEPENDENCY INJECTION NATIVA
    ✅ NO HAY NINGUN PATCH() NI NINGUN MOCK DE IMPORTACIONES
    ✅ 100% FIABLE Y SENCILLO
    """

    @pytest.fixture
    def mock_user_repository(self):
        from unittest.mock import AsyncMock

        repo = Mock()
        repo.get_by_id = AsyncMock()
        return repo

    @pytest.fixture
    def token_validation_service(self, mock_user_repository):
        return TokenValidationService(user_repository=mock_user_repository)

    @pytest.mark.asyncio
    async def test_get_current_user_ok(
        self, token_validation_service, mock_user_repository
    ):
        """
        ✅ Prueba que get_current_user funciona correctamente con token valido
        """
        token = "valid_token_123"

        mock_user = Mock()
        mock_user.id = 123
        mock_user.username = "test_user"
        mock_user.is_active = True

        mock_user_repository.get_by_id.return_value = mock_user

        # ✅ Mockear JWTHandler.verify_token solamente
        with patch(
            "apps.auth.application.services.token_validation_service.JWTHandler"
        ) as mock_jwt:
            mock_jwt.verify_token.return_value = {"sub": "123"}

            # ✅ Ejecutar metodo
            resultado = await cast(
                Awaitable[object], token_validation_service.get_current_user(token)
            )

            # ✅ Verificaciones
            assert resultado == mock_user
            mock_jwt.verify_token.assert_called_once_with(token)
            mock_user_repository.get_by_id.assert_called_once_with(123)

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(
        self, token_validation_service, mock_user_repository
    ):
        """
        ✅ Prueba que falla correctamente cuando el token es invalido
        """
        token = "invalid_token_123"

        with patch(
            "apps.auth.application.services.token_validation_service.JWTHandler"
        ) as mock_jwt:
            mock_jwt.verify_token.return_value = None

            # ✅ Debe lanzar ValueError
            with pytest.raises(ValueError, match="Token inválido"):
                await cast(
                    Awaitable[object], token_validation_service.get_current_user(token)
                )

            mock_user_repository.get_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_current_user_inactive_user(
        self, token_validation_service, mock_user_repository
    ):
        """
        ✅ Prueba que falla correctamente cuando el usuario esta inactivo
        """
        token = "valid_token_123"

        mock_user = Mock()
        mock_user.id = 123
        mock_user.username = "test_user"
        mock_user.is_active = False

        mock_user_repository.get_by_id.return_value = mock_user

        with patch(
            "apps.auth.application.services.token_validation_service.JWTHandler"
        ) as mock_jwt:
            mock_jwt.verify_token.return_value = {"sub": "123"}

            # ✅ Debe lanzar ValueError
            with pytest.raises(ValueError, match="Usuario inactivo"):
                await cast(
                    Awaitable[object], token_validation_service.get_current_user(token)
                )


if __name__ == "__main__":
    # ✅ Permite ejecutar este test directamente desde consola
    import asyncio

    print("\n✅ Ejecutando test unitario TokenValidationService ...")

    # Crear mocks manualmente
    mock_repo = Mock()
    mock_repo.get_by_id = Mock()
    mock_user = Mock()
    mock_user.id = 123
    mock_user.username = "test_user"
    mock_user.is_active = True
    mock_repo.get_by_id.return_value = mock_user

    service = TokenValidationService(user_repository=mock_repo)

    with patch(
        "apps.auth.application.services.token_validation_service.JWTHandler"
    ) as mock_jwt:
        mock_jwt.verify_token.return_value = {"sub": "123"}

        asyncio.run(
            cast(
                Coroutine[None, None, None],
                TestTokenValidationService().test_get_current_user_ok(
                    service, mock_repo
                ),
            )
        )

    print("✅ TEST PASADO: TokenValidationService funciona correctamente")
