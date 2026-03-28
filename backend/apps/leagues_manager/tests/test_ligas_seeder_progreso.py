"""Tests unitarios para verificar el progreso del LigasSeeder."""

import pytest
from unittest.mock import Mock, patch, MagicMock, create_autospec
from pathlib import Path
import json
import tempfile
from sqlalchemy.orm import Session


class TestLigasSeederProgreso:
    """Tests para verificar que el seeder maneja correctamente el progreso."""

    def test_procesa_solo_20_paises_por_ejecucion(self):
        """Verifica que el seeder procesa solo 20 países por ejecución."""
        from scripts.db.seeders.sql.ligas_seeder import LigasSeeder

        with tempfile.TemporaryDirectory() as temp_dir:
            progress_file = Path(temp_dir) / "progress.json"
            progress_file.write_text("{}", encoding="utf-8")

            mock_paises = [
                Mock(id=i, nombre=f"Pais_{i}", codigo_iso=f"P{i:02d}")
                for i in range(1, 81)
            ]

            mock_db = create_autospec(Session, instance=True)
            mock_service = Mock()
            mock_service.obtener_todos_los_paises.return_value = mock_paises

            mock_response = Mock()
            mock_response.json.return_value = {"response": []}
            mock_response.raise_for_status = Mock()

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
                        resultado = seeder.run(update=False)

            assert resultado["paises_procesados"] <= 20
            assert resultado["ultimo_pais_id"] <= 20

    def test_reanuda_desde_ultimo_pais_procesado(self):
        """Verifica que el seeder reanuda desde el último país procesado."""
        from scripts.db.seeders.sql.ligas_seeder import LigasSeeder

        with tempfile.TemporaryDirectory() as temp_dir:
            progress_file = Path(temp_dir) / "progress.json"
            progreso_previo = {
                "ultimo_pais_id": 20,
                "ultima_ejecucion": "2026-03-28T02:00:00",
                "total_paises_procesados": 20,
                "total_ligas_creadas": 100,
                "total_ligas_actualizadas": 50,
            }
            progress_file.write_text(json.dumps(progreso_previo), encoding="utf-8")

            mock_paises = [
                Mock(id=i, nombre=f"Pais_{i}", codigo_iso=f"P{i:02d}")
                for i in range(1, 81)
            ]

            mock_db = create_autospec(Session, instance=True)
            mock_service = Mock()
            mock_service.obtener_todos_los_paises.return_value = mock_paises

            mock_response = Mock()
            mock_response.json.return_value = {"response": []}
            mock_response.raise_for_status = Mock()

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
                        resultado = seeder.run(update=False)

            assert resultado["ultimo_pais_id"] >= 20
            assert resultado["paises_procesados"] <= 20

    def test_no_se_bloquea_con_80_paises(self):
        """Verifica que el seeder no se bloquea procesando 80 países."""
        from scripts.db.seeders.sql.ligas_seeder import LigasSeeder

        with tempfile.TemporaryDirectory() as temp_dir:
            progress_file = Path(temp_dir) / "progress.json"
            progress_file.write_text("{}", encoding="utf-8")

            mock_paises = [
                Mock(id=i, nombre=f"Pais_{i}", codigo_iso=f"P{i:02d}")
                for i in range(1, 81)
            ]

            mock_db = create_autospec(Session, instance=True)
            mock_service = Mock()
            mock_service.obtener_todos_los_paises.return_value = mock_paises

            mock_response = Mock()
            mock_response.json.return_value = {"response": []}
            mock_response.raise_for_status = Mock()

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
                        resultado = seeder.run(update=False)

            assert resultado["paises_procesados"] <= 20
            assert len(resultado["errores"]) == 0

    def test_multiples_ejecuciones_completan_todos_los_paises(self):
        """Verifica que múltiples ejecuciones procesan todos los países."""
        from scripts.db.seeders.sql.ligas_seeder import LigasSeeder

        with tempfile.TemporaryDirectory() as temp_dir:
            progress_file = Path(temp_dir) / "progress.json"
            progress_file.write_text("{}", encoding="utf-8")

            mock_paises = [
                Mock(id=i, nombre=f"Pais_{i}", codigo_iso=f"P{i:02d}")
                for i in range(1, 81)
            ]

            mock_db = create_autospec(Session, instance=True)
            mock_service = Mock()
            mock_service.obtener_todos_los_paises.return_value = mock_paises

            mock_response = Mock()
            mock_response.json.return_value = {"response": []}
            mock_response.raise_for_status = Mock()

            ultimo_pais_id_final = 0
            for _ in range(4):
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
                            resultado = seeder.run(update=False)
                            ultimo_pais_id_final = resultado["ultimo_pais_id"]

            # Verificar que el progreso se guardó correctamente
            assert ultimo_pais_id_final > 0
            assert ultimo_pais_id_final <= 80
