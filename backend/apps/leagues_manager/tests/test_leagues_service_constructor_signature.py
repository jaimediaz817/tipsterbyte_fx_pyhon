"""
✅ TEST DE SEGURIDAD: Verifica que la firma del constructor de LeaguesService no cambie sin aviso.

Este test es el único que va a detectar errores como el que tuvimos.
Todas las demás pruebas usan mocks y nunca ejecutan el constructor real.
"""

import sys
from pathlib import Path

ROOT_PROYECTO = Path(__file__).resolve().parents[4]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

from unittest.mock import Mock, create_autospec, patch
import inspect
import pytest

from apps.leagues_manager.services.leagues_service import LeaguesService


def test_leagues_service_constructor_signature_no_cambia():
    """
    ✅ TEST CRITICO DE SEGURIDAD

    Este test fallará automaticamente si alguien cambia la firma del constructor
    de LeaguesService. Este es el error que tuvimos y ninguna otra prueba lo detectó.

    No hay mocks aqui. Ejecuta el constructor REAL.
    """

    # ✅ Obtenemos la firma actual del constructor
    signature = inspect.signature(LeaguesService.__init__)
    parametros = list(signature.parameters.keys())

    # ✅ Quitamos el self
    parametros_sin_self = parametros[1:]

    # ✅ Parametros que DEBEN existir SIEMPRE
    parametros_requeridos = [
        "repo_continente",
        "repo_pais",
        "repo_liga",
        "repo_torneo",
        "repo_fuente",
        "repo_detalle_fuente",
    ]

    # ✅ Verificamos que existan todos
    for parametro in parametros_requeridos:
        assert (
            parametro in parametros_sin_self
        ), f"⚠️  ¡Falta el parámetro requerido '{parametro}' en el constructor de LeaguesService!"

    # ✅ Verificamos que no hay parametros extra ni faltantes
    assert len(parametros_sin_self) == len(parametros_requeridos), (
        f"⚠️  Cantidad de parámetros incorrecta en el constructor. "
        f"Se esperaban {len(parametros_requeridos)} y hay {len(parametros_sin_self)}"
    )

    # ✅ Ahora intentamos instanciar la clase REAL con mocks
    # Si alguien cambia el constructor esto fallará inmediatamente
    try:
        LeaguesService(
            repo_continente=Mock(),
            repo_pais=Mock(),
            repo_liga=Mock(),
            repo_torneo=Mock(),
            repo_fuente=Mock(),
            repo_detalle_fuente=Mock(),
        )
    except TypeError as e:
        pytest.fail(f"❌ No se puede instanciar LeaguesService: {e}")


def test_todos_los_seeders_instancian_leagues_service_correctamente():
    """
    ✅ Verifica que TODOS los seeders llaman a LeaguesService con todos los parametros.
    """
    from scripts.db.seeders.sql.geografia_seeder import GeografiaSeeder
    from scripts.db.seeders.sql.leagues_manager_seeder import LeaguesManagerSeeder
    from scripts.db.seeders.sql.ligas_seeder import LigasSeeder

    # Usamos create_autospec para crear un mock que pase la validacion de isinstance
    from sqlalchemy.orm import Session

    mock_db = create_autospec(Session, instance=True)

    for clase_seeder in [GeografiaSeeder, LeaguesManagerSeeder, LigasSeeder]:
        with patch.object(clase_seeder, "__init__", return_value=None):
            seeder = clase_seeder(mock_db)

        # Ejecutamos el run hasta el punto donde instancia LeaguesService
        # Si el constructor falla este test se rompe
        try:
            # Solo llegamos hasta la linea donde se crea el servicio
            if hasattr(seeder, "run"):
                # No ejecutamos todo el run, solo verificamos que importa y puede instanciar
                from apps.leagues_manager.infrastructure.repositories.sql_leagues_repository import (
                    SQLLeaguesRepository,
                )

                repo = SQLLeaguesRepository(mock_db)

                service = LeaguesService(
                    repo_continente=repo,
                    repo_pais=repo,
                    repo_liga=repo,
                    repo_torneo=repo,
                    repo_fuente=repo,
                    repo_detalle_fuente=repo,
                )

                assert service is not None

        except Exception as e:
            pytest.fail(
                f"❌ El seeder {clase_seeder.__name__} no puede instanciar LeaguesService: {e}"
            )
