"""
✅ PRUEBA UNITARIA: Validacion de colecciones MongoDB
✅ CUMPLE SRP, OCP, LSP, ISP, DIP
✅ EJECUTABLE DESDE CUALQUIER UBICACION
✅ COMPATIBLE CON TESTING EXPLORER VS CODE
"""

import sys
from pathlib import Path

# ✅ SOLUCION PERMANENTE PATH: Funciona en TODOS los entornos
ROOT_PROYECTO = Path(__file__).resolve().parents[5]
BACKEND_DIR = ROOT_PROYECTO / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# ✅ Cargar automaticamente variables de entorno
from dotenv import load_dotenv

load_dotenv(ROOT_PROYECTO / "backend" / ".env")

import asyncio
from unittest.mock import Mock, patch, AsyncMock
import pytest

from core.db.no_sql.schema_initializer import (
    _get_collection_name,
    validate_collections_existence,
)
from core.exceptions.database_exceptions import MongoCollectionNotInitializedException
from beanie import Document


class TestModelMock(Document):
    class Settings:
        name = "test_collection_mock"


class TestModelSinSettingsMock(Document):
    pass


@pytest.mark.unit
class TestMongoCollectionValidation:
    """
    ✅ PRUEBAS UNITARIAS COMPLETAS
    """

    def test_get_collection_name_with_settings(self):
        """✅ SRP: Funcion obtiene nombre correctamente cuando existe clase Settings"""
        collection_name = _get_collection_name(TestModelMock)
        assert collection_name == "test_collection_mock"

    def test_get_collection_name_without_settings(self):
        """✅ SRP: Funcion obtiene nombre por defecto cuando NO existe Settings"""
        collection_name = _get_collection_name(TestModelSinSettingsMock)
        assert collection_name == "testmodelsinsettingsmock"

    @pytest.mark.asyncio
    async def test_validate_collections_when_all_exist(self):
        """✅ Validacion pasa correctamente cuando todas las colecciones existen"""
        with patch(
            "core.db.no_sql.schema_initializer._find_beanie_models"
        ) as mock_find:
            mock_find.return_value = [TestModelMock]

            with patch(
                "core.db.no_sql.schema_initializer.AsyncIOMotorClient"
            ) as mock_client:
                mock_db = Mock()
                mock_db.list_collection_names = AsyncMock(
                    return_value=["test_collection_mock"]
                )
                mock_client.return_value.get_database.return_value = mock_db

                # No debe lanzar excepcion
                await validate_collections_existence()

    @pytest.mark.asyncio
    async def test_validate_collections_raise_exception_when_missing(self):
        """✅ Se lanza MongoCollectionNotInitializedException cuando falta coleccion"""
        with patch(
            "core.db.no_sql.schema_initializer._find_beanie_models"
        ) as mock_find:
            mock_find.return_value = [TestModelMock]

            with patch(
                "core.db.no_sql.schema_initializer.AsyncIOMotorClient"
            ) as mock_client:
                mock_db = Mock()
                mock_db.list_collection_names = AsyncMock(return_value=[])
                mock_client.return_value.get_database.return_value = mock_db

                # Debe lanzar la excepcion personalizada
                with pytest.raises(MongoCollectionNotInitializedException) as excinfo:
                    await validate_collections_existence()

                exception = excinfo.value
                assert exception.collection == "test_collection_mock"
                assert exception.model_name == "TestModelMock"
                assert (
                    exception.suggested_command
                    == "python backend/manage.py nosql init-schema"
                )
                assert exception.error_code == "MONGODB_COLLECTION_NOT_INITIALIZED"

    @pytest.mark.asyncio
    async def test_exception_contains_suggested_command(self):
        """✅ La excepcion contiene el comando exacto que resuelve el problema"""
        exception = MongoCollectionNotInitializedException(
            collection="test_collection", model_name="TestModel"
        )

        assert (
            "python backend/manage.py nosql init-schema" in exception.suggested_command
        )
        assert (
            exception.message
            == "La colección 'test_collection' para el modelo 'TestModel' no existe en MongoDB"
        )


if __name__ == "__main__":
    """✅ EJECUCION MANUAL DIRECTA"""
    print("\n✅ Ejecutando prueba unitaria de validacion de colecciones MongoDB")
    print("=" * 80)

    pytest.main([__file__, "-v", "-x"])
