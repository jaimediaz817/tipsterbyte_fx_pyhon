"""Tests unitarios para GeografiaSeeder."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session


# Datos mock de la API REST Countries
MOCK_API_RESPONSE = [
    {
        "name": {"common": "Colombia"},
        "continents": ["South America"],
        "region": "Americas",
        "subregion": "South America",
        "cca2": "CO",
    },
    {
        "name": {"common": "España"},
        "continents": ["Europe"],
        "region": "Europe",
        "subregion": "Southern Europe",
        "cca2": "ES",
    },
    {
        "name": {"common": "Argentina"},
        "continents": ["South America"],
        "region": "Americas",
        "subregion": "South America",
        "cca2": "AR",
    },
]


class TestGeografiaSeeder:
    """Tests para el seeder de geografía."""

    @patch("scripts.db.seeders.sql.geografia_seeder.httpx.Client")
    def test_agrupar_por_continente(self, mock_httpx):
        """Verifica que los países se agrupen correctamente por continente."""
        # Arrange
        from scripts.db.seeders.sql.geografia_seeder import GeografiaSeeder

        mock_response = Mock()
        mock_response.json.return_value = MOCK_API_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_httpx.return_value.__enter__.return_value.get.return_value = mock_response

        mock_db = MagicMock(spec=Session)
        seeder = GeografiaSeeder(mock_db)

        # Act
        datos_api = seeder._obtener_datos_api()
        agrupados = seeder._agrupar_por_continente(datos_api)

        # Assert
        assert "South America" in agrupados
        assert "Europe" in agrupados
        assert len(agrupados["South America"]) == 2  # Colombia y Argentina
        assert len(agrupados["Europe"]) == 1  # España

    @patch("scripts.db.seeders.sql.geografia_seeder.LeaguesService")
    @patch("scripts.db.seeders.sql.geografia_seeder.SQLLeaguesRepository")
    @patch("scripts.db.seeders.sql.geografia_seeder.httpx.Client")
    def test_run_crea_continentes_y_paises(
        self, mock_httpx, mock_repo_class, mock_service_class
    ):
        """Verifica que el seeder cree continentes y países correctamente."""
        # Arrange
        from scripts.db.seeders.sql.geografia_seeder import GeografiaSeeder
        from apps.leagues_manager.application.dto.continente_dto import ContinenteDTO
        from apps.leagues_manager.application.dto.geografia.pais_dto import PaisDTO

        mock_response = Mock()
        mock_response.json.return_value = MOCK_API_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_httpx.return_value.__enter__.return_value.get.return_value = mock_response

        # Mock del repositorio
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        # Mock del servicio - devolver continentes únicos para cada llamada
        mock_service = Mock()

        # Crear continentes mock con IDs únicos
        mock_continente_sa = ContinenteDTO(id=1, nombre="South America", codigo="SA")
        mock_continente_eu = ContinenteDTO(id=2, nombre="Europe", codigo="EU")

        # Mock de registrar_continente para devolver diferentes continentes
        mock_service.registrar_continente.side_effect = [
            mock_continente_sa,
            mock_continente_eu,
        ]

        # Mock de registrar_pais
        mock_pais = PaisDTO(
            id=1,
            nombre="Colombia",
            codigo_iso="CO",
            continente_id=1,
            was_created=True,
        )
        mock_service.registrar_pais.return_value = mock_pais

        # Mock de obtener_todos_los_continentes para devolver lista vacía (simula que no existen)
        mock_service.obtener_todos_los_continentes.return_value = []

        mock_service_class.return_value = mock_service

        mock_db = MagicMock(spec=Session)
        mock_db.commit = Mock()
        mock_db.rollback = Mock()

        seeder = GeografiaSeeder(mock_db)

        # Act
        resultado = seeder.run(update=False)

        # Assert
        assert resultado["continentes_creados"] >= 2
        assert resultado["paises_creados"] >= 3
        assert len(resultado["errores"]) == 0
        mock_db.commit.assert_called_once()

    @patch("scripts.db.seeders.sql.geografia_seeder.httpx.Client")
    def test_run_con_error_hace_rollback(self, mock_httpx):
        """Verifica que en caso de error se haga rollback."""
        # Arrange
        from scripts.db.seeders.sql.geografia_seeder import GeografiaSeeder

        mock_httpx.return_value.__enter__.return_value.get.side_effect = Exception(
            "Error de conexión"
        )

        mock_db = MagicMock(spec=Session)
        mock_db.rollback = Mock()

        seeder = GeografiaSeeder(mock_db)

        # Act & Assert
        with pytest.raises(Exception):
            seeder.run(update=False)

        mock_db.rollback.assert_called_once()

    @patch("scripts.db.seeders.sql.geografia_seeder.LeaguesService")
    @patch("scripts.db.seeders.sql.geografia_seeder.SQLLeaguesRepository")
    @patch("scripts.db.seeders.sql.geografia_seeder.httpx.Client")
    def test_run_es_idempotente(self, mock_httpx, mock_repo_class, mock_service_class):
        """Verifica que el seeder sea idempotente (update=True no duplica)."""
        # Arrange
        from scripts.db.seeders.sql.geografia_seeder import GeografiaSeeder
        from apps.leagues_manager.application.dto.continente_dto import ContinenteDTO
        from apps.leagues_manager.application.dto.geografia.pais_dto import PaisDTO

        mock_response = Mock()
        mock_response.json.return_value = MOCK_API_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_httpx.return_value.__enter__.return_value.get.return_value = mock_response

        # Mock del repositorio
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        # Mock del servicio
        mock_service = Mock()

        # Crear continentes mock con IDs únicos
        mock_continente_sa = ContinenteDTO(id=1, nombre="South America", codigo="SA")
        mock_continente_eu = ContinenteDTO(id=2, nombre="Europe", codigo="EU")

        # Mock de registrar_continente usando callable para soportar múltiples llamadas
        def mock_registrar_continente(dto, update=False):
            if dto.nombre == "South America":
                return mock_continente_sa
            elif dto.nombre == "Europe":
                return mock_continente_eu
            return mock_continente_sa

        mock_service.registrar_continente.side_effect = mock_registrar_continente

        # Mock de registrar_pais usando side_effect para simular idempotencia
        # Primera ejecución: países son creados (was_created=True)
        # Segunda ejecución: países ya existen (was_created=False)
        def mock_registrar_pais(dto, update=False):
            if not hasattr(mock_registrar_pais, "call_count"):
                mock_registrar_pais.call_count = 0
            mock_registrar_pais.call_count += 1

            # Primera ejecución: países son creados
            if mock_registrar_pais.call_count <= 3:  # 3 países en MOCK_API_RESPONSE
                return PaisDTO(
                    id=mock_registrar_pais.call_count,
                    nombre=dto.nombre,
                    codigo_iso=dto.codigo_iso,
                    continente_id=dto.continente_id,
                    was_created=True,
                )
            # Segunda ejecución: países ya existen
            else:
                return PaisDTO(
                    id=mock_registrar_pais.call_count - 3,
                    nombre=dto.nombre,
                    codigo_iso=dto.codigo_iso,
                    continente_id=dto.continente_id,
                    was_created=False,
                )

        mock_service.registrar_pais.side_effect = mock_registrar_pais

        # Mock de obtener_todos_los_continentes usando side_effect para simular idempotencia
        # Primera llamada: lista vacía (no existen continentes)
        # Segunda llamada: continentes existentes (simula que ya fueron creados)
        def mock_obtener_continentes():
            if not hasattr(mock_obtener_continentes, "called"):
                mock_obtener_continentes.called = True
                return []  # Primera llamada: no existen
            return [
                mock_continente_sa,
                mock_continente_eu,
            ]  # Segunda llamada: ya existen

        mock_service.obtener_todos_los_continentes.side_effect = (
            mock_obtener_continentes
        )

        mock_service_class.return_value = mock_service

        mock_db = MagicMock(spec=Session)
        mock_db.commit = Mock()

        seeder = GeografiaSeeder(mock_db)

        # Act - Ejecutar dos veces con update=True
        resultado1 = seeder.run(update=True)
        resultado2 = seeder.run(update=True)

        # Assert - Segunda ejecución no debe crear duplicados de continentes
        assert resultado2["continentes_creados"] == 0
        assert resultado2["continentes_actualizados"] >= 0
        # Segunda ejecución: países ya existen, no se crean nuevos
        assert resultado2["paises_creados"] == 0
        assert resultado2["paises_actualizados"] >= 0
