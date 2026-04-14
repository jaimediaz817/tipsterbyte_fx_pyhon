"""
❌ ARCHIVO OBSOLETO - NO USAR
✅ Este test pertenece a la version ANTERIOR del semaforo antes del refactor.
✅ La clase SemaphoreSingleton fue ELIMINADA permanentemente.
✅ Reemplazado por:
   - test_semaphore_singleton_visual.py
   - test_semaphore_differentiation.py

NO EJECUTAR ESTE ARCHIVO.
TODO EL CODIGO AQUI ABAJO NO FUNCIONA CON LA NUEVA IMPLEMENTACION.
"""

import sys
from pathlib import Path

# ✅ SOLUCION PERMANENTE PATH: Funciona en TODOS los entornos
ROOT_PROYECTO = Path(__file__).resolve().parents[4]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

# ✅ Cargar automaticamente variables de entorno
from dotenv import load_dotenv

load_dotenv(ROOT_PROYECTO / "backend" / ".env")


import pytest


@pytest.mark.skip(reason="Test obsoleto - SemaphoreSingleton fue eliminado en refactor")
class TestSemaphoreDetalleFuenteExtraccion:
    """
    ❌ TEST OBSOLETO

    Este test correspondia a la antigua implementacion del semaforo.
    La clase SemaphoreSingleton ya no existe.

    ✅ Ver tests nuevos:
        - test_semaphore_singleton_visual.py
        - test_semaphore_differentiation.py
    """

    def test_obsoleto(self):
        pass


if __name__ == "__main__":
    print("\n❌ ESTE ARCHIVO ESTA OBSOLETO")
    print("✅ La clase SemaphoreSingleton fue eliminada permanentemente")
    print(
        "✅ Usar test_semaphore_singleton_visual.py y test_semaphore_differentiation.py\n"
    )
    pytest.main([__file__, "-v", "-s"])
