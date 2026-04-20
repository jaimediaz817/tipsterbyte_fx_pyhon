# ✅ TEST UNITARIO SessionManagementService
# ✅ FUNCIONA EN VS CODE TESTING EXPLORER
# ✅ FUNCIONA EJECUTANDO python test_session_management_service.py
# ✅ FUNCIONA CON pytest
# ✅ NO USA BASE DE DATOS
# ✅ NO USA @PATCH

import sys
import io
from pathlib import Path
from typing import cast, Awaitable, Coroutine, Any

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
from unittest.mock import Mock, AsyncMock
from apps.auth.application.services.session_management_service import (
    SessionManagementService,
)


class TestSessionManagementService:
    """
    ✅ TEST UNITARIO COMPLETO
    ✅ NO USA BASE DE DATOS REAL
    ✅ USAMOS DEPENDENCY INJECTION NATIVA
    ✅ NO HAY NINGUN PATCH() NI NINGUN MOCK DE IMPORTACIONES
    ✅ 100% FIABLE Y SENCILLO
    """

    @pytest.fixture
    def mock_session_log_service(self):
        service = Mock()
        service.log_action = AsyncMock()
        return service

    @pytest.fixture
    def session_management_service(self, mock_session_log_service):
        return SessionManagementService(session_log_service=mock_session_log_service)

    @pytest.mark.asyncio
    async def test_logout_ok(
        self, session_management_service, mock_session_log_service
    ):
        """
        ✅ Prueba que logout funciona correctamente
        ✅ Verifica que se registra la accion en el log
        """
        user_id = 123

        # ✅ Ejecutar metodo
        resultado = await cast(
            Awaitable[dict], session_management_service.logout(user_id)
        )

        # ✅ Verificaciones
        assert resultado == {"message": "Sesión cerrada exitosamente"}
        mock_session_log_service.log_action.assert_awaited_once()

        # ✅ Verificar parametros correctos
        args = mock_session_log_service.log_action.call_args
        assert args[1]["user_id"] == user_id
        assert args[1]["action"] == "logout"
        assert args[1]["status_code"] == 200


if __name__ == "__main__":
    # ✅ Permite ejecutar este test directamente desde consola
    import asyncio

    print("\n✅ Ejecutando test unitario SessionManagementService ...")

    # Crear mocks manualmente
    mock_log = Mock()
    mock_log.log_action = AsyncMock()

    service = SessionManagementService(session_log_service=mock_log)

    asyncio.run(
        cast(
            Coroutine[Any, Any, None],
            TestSessionManagementService().test_logout_ok(service, mock_log),
        )
    )

    print("✅ TEST PASADO: SessionManagementService funciona correctamente")
