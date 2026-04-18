"""
✅ TEST UNITARIO COMPLETO: Resumen y Rate Limit
✅ Simula el comportamiento completo del seeder
✅ Simula ejecucion parcial + rate limit
✅ Simula reanudacion al dia siguiente
✅ Verifica que continua EXACTAMENTE donde se quedo
"""

import sys
from pathlib import Path
import json
from unittest.mock import Mock, patch
from tempfile import TemporaryDirectory

# ✅ Configuracion PATH Universal
ROOT_PROYECTO = Path(__file__).resolve().parents[4]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

from dotenv import load_dotenv

load_dotenv(ROOT_PROYECTO / "backend" / ".env")

import pytest
from scripts.db.seeders.sql.ligas_seeder import LigasSeeder


class TestLigasSeederResumeRateLimit:

    def test_seeder_guarda_progreso_y_se_reanuda_correctamente(self):
        """
        ✅ Test flujo completo:
        1. Ejecucion inicial
        2. Alcanza Rate Limit en el pais 3
        3. Se detiene y guarda progreso
        4. Simula ejecucion al dia siguiente
        5. Verifica que empieza directamente desde el pais 4
        """

        with TemporaryDirectory() as tmpdir:
            progress_file = Path(tmpdir) / "test_progress.json"

            # Mock de base de datos
            mock_db = Mock()

            # Mock de paises simulados
            paises_mock = [
                Mock(id=1, nombre="Pais 1", codigo_iso="P1"),
                Mock(id=2, nombre="Pais 2", codigo_iso="P2"),
                Mock(
                    id=3, nombre="Pais 3", codigo_iso="P3"
                ),  # <--- AQUI LLEGA RATE LIMIT
                Mock(id=4, nombre="Pais 4", codigo_iso="P4"),
                Mock(id=5, nombre="Pais 5", codigo_iso="P5"),
            ]

            # 🔹 PRIMERA EJECUCION: Llega Rate Limit en pais 3
            seeder = LigasSeeder(mock_db, progress_file=progress_file)

            with patch.object(seeder, "_obtener_ligas_por_pais") as mock_api:
                # Primeros 2 paises responden bien
                mock_api.side_effect = [
                    [{"league": {"id": 1, "name": "Liga 1"}}],
                    [{"league": {"id": 2, "name": "Liga 2"}}],
                    # Tercer pais lanza Rate Limit
                    RuntimeError("RATE_LIMIT_REACHED"),
                ]

                with patch.object(seeder, "_procesar_liga", return_value="creada"):
                    with patch(
                        "apps.leagues_manager.services.leagues_service.LeaguesService.obtener_todos_los_paises",
                        return_value=paises_mock,
                    ):

                        # Ejecutar seeder primera vez
                        resultado = seeder.run()

            # ✅ Verificar que se guardo progreso correctamente en pais 3
            assert (
                resultado["ultimo_pais_id"] == 2
            ), "❌ No se guardo el ultimo pais exitoso"

            # Cargar progreso guardado
            with open(progress_file, "r") as f:
                progreso_guardado = json.load(f)

            assert (
                progreso_guardado["ultimo_pais_id"] == 2
            ), "❌ Progreso no guardado correctamente"

            # ✅ VERIFICACION MAS IMPORTANTE:
            # Cuando volvemos a ejecutar el seeder, empieza DIRECTAMENTE desde el pais 3
            # No vuelve a procesar 1 y 2!

            # 🔹 SEGUNDA EJECUCION: Simulamos que pasaron 24h
            seeder2 = LigasSeeder(mock_db, progress_file=progress_file)

            paises_procesados_segunda_vez = []

            def mock_obtener_ligas_segunda_vez(nombre_pais):
                paises_procesados_segunda_vez.append(nombre_pais)
                return [{"league": {"id": 100, "name": "Liga Test"}}]

            with patch.object(
                seeder2,
                "_obtener_ligas_por_pais",
                side_effect=mock_obtener_ligas_segunda_vez,
            ):
                with patch.object(seeder2, "_procesar_liga", return_value="creada"):
                    with patch(
                        "apps.leagues_manager.services.leagues_service.LeaguesService.obtener_todos_los_paises",
                        return_value=paises_mock,
                    ):

                        # Ejecutar seeder nuevamente (como si fuera al dia siguiente)
                        resultado2 = seeder2.run()

            # ✅ Verificacion FINAL: SOLO procesa paises desde el 3 en adelante
            assert (
                "Pais 1" not in paises_procesados_segunda_vez
            ), "❌ Vuelve a procesar pais 1!"
            assert (
                "Pais 2" not in paises_procesados_segunda_vez
            ), "❌ Vuelve a procesar pais 2!"
            assert (
                "Pais 3" in paises_procesados_segunda_vez
            ), "❌ No continua desde el pais 3!"
            assert "Pais 4" in paises_procesados_segunda_vez, "❌ No procesa pais 4!"
            assert "Pais 5" in paises_procesados_segunda_vez, "❌ No procesa pais 5!"

            # ✅ Todo funciona perfectamente
            assert True, "✅ El seeder se reanuda CORRECTAMENTE donde se quedo!"

    def test_seeder_se_detiene_inmediatamente_en_rate_limit(self):
        """✅ Verifica que cuando llega Rate Limit NO sigue haciendo peticiones"""

        with TemporaryDirectory() as tmpdir:
            progress_file = Path(tmpdir) / "test_progress_rate.json"
            mock_db = Mock()

            paises_mock = [
                Mock(id=1, nombre="Pais 1", codigo_iso="P1"),
                Mock(id=2, nombre="Pais 2", codigo_iso="P2"),
                Mock(id=3, nombre="Pais 3", codigo_iso="P3"),
                Mock(id=4, nombre="Pais 4", codigo_iso="P4"),
            ]

            seeder = LigasSeeder(mock_db, progress_file=progress_file)

            contador_peticiones = 0

            def mock_api_conteo(nombre_pais):
                nonlocal contador_peticiones
                contador_peticiones += 1

                if nombre_pais == "Pais 2":
                    raise RuntimeError("RATE_LIMIT_REACHED")

                return [{"league": {"id": 1, "name": "Liga Test"}}]

            with patch.object(
                seeder, "_obtener_ligas_por_pais", side_effect=mock_api_conteo
            ):
                with patch.object(seeder, "_procesar_liga", return_value="creada"):
                    with patch(
                        "apps.leagues_manager.services.leagues_service.LeaguesService.obtener_todos_los_paises",
                        return_value=paises_mock,
                    ):
                        seeder.run()

            # ✅ Solo hace 2 peticiones, no 4!
            # Se detiene INMEDIATAMENTE cuando llega rate limit
            assert (
                contador_peticiones == 2
            ), f"❌ Hizo {contador_peticiones} peticiones, deberian ser 2"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
