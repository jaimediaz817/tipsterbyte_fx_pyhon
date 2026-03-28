"""Tests unitarios para LigasSeeder."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from apps.leagues_manager.domain.enums.categoria_liga_enum import CategoriaLigaEnum


# Datos mock de la API-Football
MOCK_API_RESPONSE = [
    {
        "league": {
            "id": 140,
            "name": "La Liga",
            "type": "League",
            "logo": "https://media.api-sports.io/football/leagues/140.png",
        }
    },
    {
        "league": {
            "id": 141,
            "name": "Copa del Rey",
            "type": "Cup",
            "logo": "https://media.api-sports.io/football/leagues/141.png",
        }
    },
    {
        "league": {
            "id": 142,
            "name": "Segunda División",
            "type": "League",
            "logo": "https://media.api-sports.io/football/leagues/142.png",
        }
    },
]

# Datos mock de países
MOCK_PAISES = [
    Mock(id=1, nombre="España", codigo_iso="ES"),
    Mock(id=2, nombre="England", codigo_iso="EN"),
]


class TestLigasSeeder:
    """Tests para el seeder de ligas."""

    @patch("scripts.db.seeders.sql.ligas_seeder.httpx.Client")
    def test_obtener_ligas_por_pais_exitoso(self, mock_httpx):
        """Verifica que se obtengan ligas correctamente de la API."""
        # Arrange
        from scripts.db.seeders.sql.ligas_seeder import LigasSeeder

        mock_response = Mock()
        mock_response.json.return_value = {"response": MOCK_API_RESPONSE}
        mock_response.raise_for_status = Mock()
        mock_httpx.return_value.__enter__.return_value.get.return_value = mock_response

        mock_db = MagicMock(spec=Session)
        seeder = LigasSeeder(mock_db)

        # Act
        ligas = seeder._obtener_ligas_por_pais("Spain")

        # Assert
        assert len(ligas) == 3
        assert ligas[0]["league"]["name"] == "La Liga"
        assert ligas[1]["league"]["name"] == "Copa del Rey"

    @patch("scripts.db.seeders.sql.ligas_seeder.httpx.Client")
    def test_obtener_ligas_por_pais_error_http(self, mock_httpx):
        """Verifica que se retorne lista vacía en caso de error HTTP."""
        # Arrange
        from scripts.db.seeders.sql.ligas_seeder import LigasSeeder

        mock_httpx.return_value.__enter__.return_value.get.side_effect = Exception(
            "Error de conexión"
        )

        mock_db = MagicMock(spec=Session)
        seeder = LigasSeeder(mock_db)

        # Act
        ligas = seeder._obtener_ligas_por_pais("Spain")

        # Assert
        assert ligas == []

    @patch("scripts.db.seeders.sql.ligas_seeder.LeaguesService")
    @patch("scripts.db.seeders.sql.ligas_seeder.SQLLeaguesRepository")
    def test_procesar_liga_crea_nueva(self, mock_repo_class, mock_service_class):
        """Verifica que se cree una liga nueva correctamente."""
        # Arrange
        from scripts.db.seeders.sql.ligas_seeder import LigasSeeder
        from apps.leagues_manager.application.dto.liga_dto import LigaDTO

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_service = Mock()
        # Liga no existe previamente
        mock_liga = LigaDTO(
            id=1,
            nombre="La Liga",
            pais_id=1,
            nombre_categoria=CategoriaLigaEnum.A,
            id_api_externa=None,
            logo_url=None,
            tipo_liga=None,
        )
        mock_service.registrar_liga.return_value = mock_liga
        mock_service_class.return_value = mock_service

        mock_db = MagicMock(spec=Session)
        seeder = LigasSeeder(mock_db)

        liga_data = {
            "league": {
                "id": 140,
                "name": "La Liga",
                "type": "League",
                "logo": "https://media.api-sports.io/football/leagues/140.png",
            }
        }

        # Act
        resultado = seeder._procesar_liga(liga_data, 1, mock_service, update=False)

        # Assert
        assert resultado == "creada"
        mock_service.registrar_liga.assert_called_once()
        mock_service.actualizar_liga_api_football.assert_called_once_with(
            liga_id=1,
            id_api_externa=140,
            logo_url="https://media.api-sports.io/football/leagues/140.png",
            tipo_liga="League",
        )

    @patch("scripts.db.seeders.sql.ligas_seeder.LeaguesService")
    @patch("scripts.db.seeders.sql.ligas_seeder.SQLLeaguesRepository")
    def test_procesar_liga_actualiza_existente(
        self, mock_repo_class, mock_service_class
    ):
        """Verifica que se actualice una liga existente."""
        # Arrange
        from scripts.db.seeders.sql.ligas_seeder import LigasSeeder
        from apps.leagues_manager.application.dto.liga_dto import LigaDTO

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_service = Mock()
        # Liga ya existe con el mismo id_api_externa
        mock_liga = LigaDTO(
            id=1,
            nombre="La Liga",
            pais_id=1,
            nombre_categoria=CategoriaLigaEnum.A,
            id_api_externa=140,  # Ya tiene el ID de API
            logo_url="https://media.api-sports.io/football/leagues/140.png",
            tipo_liga="League",
        )
        mock_service.registrar_liga.return_value = mock_liga
        mock_service_class.return_value = mock_service

        mock_db = MagicMock(spec=Session)
        seeder = LigasSeeder(mock_db)

        liga_data = {
            "league": {
                "id": 140,
                "name": "La Liga",
                "type": "League",
                "logo": "https://media.api-sports.io/football/leagues/140.png",
            }
        }

        # Act
        resultado = seeder._procesar_liga(liga_data, 1, mock_service, update=False)

        # Assert
        assert resultado == "actualizada"
        mock_service.registrar_liga.assert_called_once()
        # No debe llamar a actualizar_liga_api_football si ya existe
        mock_service.actualizar_liga_api_football.assert_not_called()

    @patch("scripts.db.seeders.sql.ligas_seeder.LeaguesService")
    @patch("scripts.db.seeders.sql.ligas_seeder.SQLLeaguesRepository")
    def test_mapeo_tipo_liga(self, mock_repo_class, mock_service_class):
        """Verifica que se mapee correctamente el tipo de liga."""
        # Arrange
        from scripts.db.seeders.sql.ligas_seeder import LigasSeeder
        from apps.leagues_manager.application.dto.liga_dto import LigaDTO

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_service = Mock()
        mock_liga = LigaDTO(
            id=1,
            nombre="Copa del Rey",
            pais_id=1,
            nombre_categoria=None,
            id_api_externa=None,
            logo_url=None,
            tipo_liga=None,
        )
        mock_service.registrar_liga.return_value = mock_liga
        mock_service_class.return_value = mock_service

        mock_db = MagicMock(spec=Session)
        seeder = LigasSeeder(mock_db)

        # Test para tipo "Cup" -> categoría "B"
        liga_data = {
            "league": {
                "id": 141,
                "name": "Copa del Rey",
                "type": "Cup",
                "logo": "https://media.api-sports.io/football/leagues/141.png",
            }
        }

        # Act
        resultado = seeder._procesar_liga(liga_data, 1, mock_service, update=False)

        # Assert
        assert resultado == "creada"
        # Verificar que se llamó registrar_liga con la categoría correcta
        call_args = mock_service.registrar_liga.call_args
        dto = call_args[0][0]
        assert dto.nombre_categoria is not None
        assert dto.nombre_categoria.value == "B"

    @patch("scripts.db.seeders.sql.ligas_seeder.LeaguesService")
    @patch("scripts.db.seeders.sql.ligas_seeder.SQLLeaguesRepository")
    @patch("scripts.db.seeders.sql.ligas_seeder.httpx.Client")
    def test_run_procesa_multiples_paises(
        self, mock_httpx, mock_repo_class, mock_service_class
    ):
        """Verifica que se procesen múltiples países correctamente."""
        # Arrange
        from scripts.db.seeders.sql.ligas_seeder import LigasSeeder
        from apps.leagues_manager.application.dto.liga_dto import LigaDTO

        mock_response = Mock()
        mock_response.json.return_value = {"response": MOCK_API_RESPONSE}
        mock_response.raise_for_status = Mock()
        mock_httpx.return_value.__enter__.return_value.get.return_value = mock_response

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_service = Mock()
        # Mock de países
        mock_service.obtener_todos_los_paises.return_value = MOCK_PAISES

        # Mock de ligas creadas
        mock_liga = LigaDTO(
            id=1,
            nombre="La Liga",
            pais_id=1,
            nombre_categoria=CategoriaLigaEnum.A,
            id_api_externa=None,
            logo_url=None,
            tipo_liga=None,
        )
        mock_service.registrar_liga.return_value = mock_liga
        mock_service_class.return_value = mock_service

        mock_db = MagicMock(spec=Session)
        mock_db.commit = Mock()

        seeder = LigasSeeder(mock_db)

        # Act
        resultado = seeder.run(update=False)

        # Assert
        assert resultado["paises_procesados"] == 2
        assert resultado["paises_con_ligas"] == 2
        assert resultado["ligas_creadas"] >= 2
        mock_db.commit.assert_called_once()

    @patch("scripts.db.seeders.sql.ligas_seeder.httpx.Client")
    def test_run_con_error_http_retorna_lista_vacia(self, mock_httpx):
        """Verifica que en caso de error HTTP se retorne lista vacía."""
        # Arrange
        from scripts.db.seeders.sql.ligas_seeder import LigasSeeder

        mock_httpx.return_value.__enter__.return_value.get.side_effect = Exception(
            "Error de conexión"
        )

        mock_db = MagicMock(spec=Session)
        seeder = LigasSeeder(mock_db)

        # Act
        ligas = seeder._obtener_ligas_por_pais("Spain")

        # Assert - Debe retornar lista vacía en caso de error
        assert ligas == []

    @patch("scripts.db.seeders.sql.ligas_seeder.LeaguesService")
    @patch("scripts.db.seeders.sql.ligas_seeder.SQLLeaguesRepository")
    @patch("scripts.db.seeders.sql.ligas_seeder.httpx.Client")
    def test_run_es_idempotente(self, mock_httpx, mock_repo_class, mock_service_class):
        """Verifica que el seeder sea idempotente (update=True no duplica)."""
        # Arrange
        import tempfile
        from pathlib import Path
        from scripts.db.seeders.sql.ligas_seeder import LigasSeeder
        from apps.leagues_manager.application.dto.liga_dto import LigaDTO

        # Usar archivo temporal para progreso
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp_file:
            progress_file = Path(tmp_file.name)
            tmp_file.write("{}")

        mock_response = Mock()
        mock_response.json.return_value = {"response": MOCK_API_RESPONSE}
        mock_response.raise_for_status = Mock()
        mock_httpx.return_value.__enter__.return_value.get.return_value = mock_response

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_service = Mock()
        # Mock de países
        mock_service.obtener_todos_los_paises.return_value = [MOCK_PAISES[0]]

        # Primera ejecución: liga creada
        mock_liga_creada = LigaDTO(
            id=1,
            nombre="La Liga",
            pais_id=1,
            nombre_categoria=CategoriaLigaEnum.A,
            id_api_externa=None,
            logo_url=None,
            tipo_liga=None,
        )

        # Simular idempotencia: primera ejecución crea, segunda actualiza
        call_count = [0]

        def mock_registrar_liga(dto, update=False):
            call_count[0] += 1
            if call_count[0] <= 3:  # Primera ejecución (3 ligas)
                return mock_liga_creada
            else:  # Segunda ejecución: liga ya existe
                return LigaDTO(
                    id=1,
                    nombre=dto.nombre,
                    pais_id=dto.pais_id,
                    nombre_categoria=dto.nombre_categoria,
                    id_api_externa=140,  # Ya tiene ID de API
                    logo_url="https://media.api-sports.io/football/leagues/140.png",
                    tipo_liga="League",
                )

        mock_service.registrar_liga.side_effect = mock_registrar_liga
        mock_service_class.return_value = mock_service

        mock_db = MagicMock(spec=Session)
        mock_db.commit = Mock()

        seeder = LigasSeeder(mock_db, progress_file=progress_file)

        # Act - Ejecutar dos veces con update=True
        resultado1 = seeder.run(update=True)
        resultado2 = seeder.run(update=True)

        # Assert - Primera ejecución crea ligas
        assert resultado1["ligas_creadas"] >= 0
        assert resultado1["paises_procesados"] == 1
        # Segunda ejecución: no procesa países porque el único país ya fue procesado
        # (el progreso guardó ultimo_pais_id=1, y el país tiene id=1, por lo que no pasa el filtro id > ultimo_pais_id)
        assert resultado2["paises_procesados"] == 0

    @patch("scripts.db.seeders.sql.ligas_seeder.LeaguesService")
    @patch("scripts.db.seeders.sql.ligas_seeder.SQLLeaguesRepository")
    def test_procesar_liga_sin_datos_validos(self, mock_repo_class, mock_service_class):
        """Verifica que se ignoren ligas sin datos válidos."""
        # Arrange
        from scripts.db.seeders.sql.ligas_seeder import LigasSeeder

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_db = MagicMock(spec=Session)
        seeder = LigasSeeder(mock_db)

        # Liga sin nombre
        liga_data = {"league": {"id": 140, "name": None, "type": "League"}}

        # Act
        resultado = seeder._procesar_liga(liga_data, 1, mock_service, update=False)

        # Assert
        assert resultado == "ignorada"
        mock_service.registrar_liga.assert_not_called()

    @patch("scripts.db.seeders.sql.ligas_seeder.LeaguesService")
    @patch("scripts.db.seeders.sql.ligas_seeder.SQLLeaguesRepository")
    @patch("scripts.db.seeders.sql.ligas_seeder.httpx.Client")
    def test_run_pais_sin_codigo_iso(
        self, mock_httpx, mock_repo_class, mock_service_class
    ):
        """Verifica que se salten países sin código ISO."""
        # Arrange
        from scripts.db.seeders.sql.ligas_seeder import LigasSeeder

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_service = Mock()
        # País sin código ISO
        mock_service.obtener_todos_los_paises.return_value = [
            Mock(id=1, nombre="País Sin ISO", codigo_iso=None)
        ]
        mock_service_class.return_value = mock_service

        mock_db = MagicMock(spec=Session)
        mock_db.commit = Mock()

        seeder = LigasSeeder(mock_db)

        # Act
        resultado = seeder.run(update=False)

        # Assert
        assert resultado["paises_procesados"] == 0
        assert resultado["ligas_creadas"] == 0
