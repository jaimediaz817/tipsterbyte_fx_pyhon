import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from apps.leagues_manager.infrastructure.repositories.sql_platform_repository import (
    SqlPlatformRepository,
)
from apps.leagues_manager.domain.entities.liga import (
    Liga,
)  # Asegúrate de que la importación sea correcta


class TestSqlPlatformRepository(unittest.TestCase):
    def test_create_repository(self):
        # Crear un mock de la sesión de la base de datos
        db_session_mock = MagicMock(spec=Session)

        # Crear una instancia del repositorio
        repository = SqlPlatformRepository(db_session_mock)

        # Verificar que la instancia se crea sin errores
        self.assertIsInstance(repository, SqlPlatformRepository)


if __name__ == "__main__":
    unittest.main()
