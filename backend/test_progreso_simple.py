"""Test simple para verificar el progreso del LigasSeeder."""

import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent))

from apps.leagues_manager.tests.test_ligas_seeder_progreso import (
    TestLigasSeederProgreso,
)


def main():
    """Ejecuta los tests de progreso."""
    print("=" * 60)
    print("TEST SIMPLE: Verificando progreso del LigasSeeder")
    print("=" * 60)
    print()

    test = TestLigasSeederProgreso()

    # Test 1: Procesa solo 20 países
    print("TEST 1: Verificando que procesa solo 20 países...")
    try:
        test.test_procesa_solo_20_paises_por_ejecucion()
        print("✅ TEST 1 PASÓ: El seeder procesa máximo 20 países")
    except AssertionError as e:
        print(f"❌ TEST 1 FALLÓ (AssertionError): {e}")
    except Exception as e:
        print(f"❌ TEST 1 FALLÓ (Error): {e}")
        import traceback

        traceback.print_exc()

    print()

    # Test 2: No se bloquea con 80 países
    print("TEST 2: Verificando que no se bloquea con 80 países...")
    try:
        test.test_no_se_bloquea_con_80_paises()
        print("✅ TEST 2 PASÓ: El seeder no se bloquea")
    except AssertionError as e:
        print(f"❌ TEST 2 FALLÓ (AssertionError): {e}")
    except Exception as e:
        print(f"❌ TEST 2 FALLÓ (Error): {e}")
        import traceback

        traceback.print_exc()

    print()
    print("=" * 60)
    print("FIN DE TESTS")
    print("=" * 60)


if __name__ == "__main__":
    main()
