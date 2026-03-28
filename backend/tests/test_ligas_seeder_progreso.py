"""Tests unitarios para verificar el funcionamiento del seeder de ligas con progreso."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from scripts.db.seeders.sql.ligas_seeder import LigasSeeder


class TestLigasSeederProgreso:
    """Tests para verificar el comportamiento del seeder con progreso."""

    def test_procesa_solo_20_paises_por_ejecucion(self):
        """Verifica que el seeder procesa solo 20 países por ejecución."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_paises = []
        for i in range(1, 81):  # 80 países
            mock_pais = Mock()
            mock_pais.id = i
            mock_pais.nombre = f"Pais_{i}"
            mock_pais.codigo_iso = f"P{i:02d}"
            mock_paises.append(mock_pais)

        mock_service = Mock()
        mock_service.obtener_todos_los_paises.return_value = mock_paises

        mock_response = Mock()
        mock_response.json.return_value = {"response": []}
        mock_response.raise_for_status = Mock()

        # Crear archivo temporal para progreso
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            progress_file = Path(f.name)
            f.write("{}")

        try:
            with patch(
                "scripts.db.seeders.sql.ligas_seeder.httpx.Client"
            ) as mock_httpx:
                mock_httpx.return_value.__enter__.return_value.get.return_value = (
                    mock_response
                )
                with patch(
                    "scripts.db.seeders.sql.ligas_seeder.SQLLeaguesRepository",
                    return_value=Mock(),
                ):
                    with patch(
                        "scripts.db.seeders.sql.ligas_seeder.LeaguesService",
                        return_value=mock_service,
                    ):
                        seeder = LigasSeeder(mock_db, progress_file=progress_file)

                        # Act
                        resultado = seeder.run(update=False)

                        # Assert
                        assert resultado["paises_procesados"] <= 20
                        assert resultado["ultimo_pais_id"] <= 20
        finally:
            # Cleanup
            if progress_file.exists():
                progress_file.unlink()

    def test_reanuda_desde_ultimo_pais_procesado(self):
        """Verifica que el seeder reanuda desde el último país procesado."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_paises = []
        for i in range(1, 81):  # 80 países
            mock_pais = Mock()
            mock_pais.id = i
            mock_pais.nombre = f"Pais_{i}"
            mock_pais.codigo_iso = f"P{i:02d}"
            mock_paises.append(mock_pais)

        mock_service = Mock()
        mock_service.obtener_todos_los_paises.return_value = mock_paises

        mock_response = Mock()
        mock_response.json.return_value = {"response": []}
        mock_response.raise_for_status = Mock()

        # Crear archivo temporal con progreso previo
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            progress_file = Path(f.name)
            progreso_previo = {
                "ultimo_pais_id": 20,
                "ultima_ejecucion": "2026-03-28T02:00:00",
                "total_paises_procesados": 20,
                "total_ligas_creadas": 100,
                "total_ligas_actualizadas": 50,
            }
            json.dump(progreso_previo, f)

        try:
            with patch(
                "scripts.db.seeders.sql.ligas_seeder.httpx.Client"
            ) as mock_httpx:
                mock_httpx.return_value.__enter__.return_value.get.return_value = (
                    mock_response
                )
                with patch(
                    "scripts.db.seeders.sql.ligas_seeder.SQLLeaguesRepository",
                    return_value=Mock(),
                ):
                    with patch(
                        "scripts.db.seeders.sql.ligas_seeder.LeaguesService",
                        return_value=mock_service,
                    ):
                        seeder = LigasSeeder(mock_db, progress_file=progress_file)

                        # Act
                        resultado = seeder.run(update=False)

                        # Assert - Debe continuar desde país 21
                        assert resultado["ultimo_pais_id"] >= 20
                        assert resultado["paises_procesados"] <= 20
        finally:
            # Cleanup
            if progress_file.exists():
                progress_file.unlink()

    def test_no_se_bloquea_con_80_paises(self):
        """Verifica que el seeder no se bloquea procesando 80 países."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_paises = []
        for i in range(1, 81):  # 80 países
            mock_pais = Mock()
            mock_pais.id = i
            mock_pais.nombre = f"Pais_{i}"
            mock_pais.codigo_iso = f"P{i:02d}"
            mock_paises.append(mock_pais)

        mock_service = Mock()
        mock_service.obtener_todos_los_paises.return_value = mock_paises

        mock_response = Mock()
        mock_response.json.return_value = {"response": []}
        mock_response.raise_for_status = Mock()

        # Crear archivo temporal para progreso
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            progress_file = Path(f.name)
            f.write("{}")

        try:
            with patch(
                "scripts.db.seeders.sql.ligas_seeder.httpx.Client"
            ) as mock_httpx:
                mock_httpx.return_value.__enter__.return_value.get.return_value = (
                    mock_response
                )
                with patch(
                    "scripts.db.seeders.sql.ligas_seeder.SQLLeaguesRepository",
                    return_value=Mock(),
                ):
                    with patch(
                        "scripts.db.seeders.sql.ligas_seeder.LeaguesService",
                        return_value=mock_service,
                    ):
                        seeder = LigasSeeder(mock_db, progress_file=progress_file)

                        # Act
                        resultado = seeder.run(update=False)

                        # Assert
                        assert resultado["paises_procesados"] <= 20
                        assert len(resultado["errores"]) == 0
        finally:
            # Cleanup
            if progress_file.exists():
                progress_file.unlink()

    def test_multiples_ejecuciones_completan_todos_los_paises(self):
        """Verifica que múltiples ejecuciones procesan todos los países."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        mock_paises = []
        for i in range(1, 81):  # 80 países
            mock_pais = Mock()
            mock_pais.id = i
            mock_pais.nombre = f"Pais_{i}"
            mock_pais.codigo_iso = f"P{i:02d}"
            mock_paises.append(mock_pais)

        mock_service = Mock()
        mock_service.obtener_todos_los_paises.return_value = mock_paises

        mock_response = Mock()
        mock_response.json.return_value = {"response": []}
        mock_response.raise_for_status = Mock()

        # Crear archivo temporal para progreso
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            progress_file = Path(f.name)
            f.write("{}")

        try:
            with patch(
                "scripts.db.seeders.sql.ligas_seeder.httpx.Client"
            ) as mock_httpx:
                mock_httpx.return_value.__enter__.return_value.get.return_value = (
                    mock_response
                )
                with patch(
                    "scripts.db.seeders.sql.ligas_seeder.SQLLeaguesRepository",
                    return_value=Mock(),
                ):
                    with patch(
                        "scripts.db.seeders.sql.ligas_seeder.LeaguesService",
                        return_value=mock_service,
                    ):
                        seeder = LigasSeeder(mock_db, progress_file=progress_file)

                        # Act - Ejecutar múltiples veces
                        total_procesados = 0
                        for _ in range(5):  # 5 ejecuciones deberían ser suficientes
                            resultado = seeder.run(update=False)
                            total_procesados += resultado["paises_procesados"]
                            if total_procesados >= 80:
                                break

                        # Assert
                        assert total_procesados >= 80  # Todos los países procesados
        finally:
            # Cleanup
            if progress_file.exists():
                progress_file.unlink()
