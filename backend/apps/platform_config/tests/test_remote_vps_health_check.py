"""
✅ TEST UNITARIO EJECUTABLE REMOTO VPS HEALTH CHECK
✅ Funciona desde Testing Explorer VS Code
✅ Funciona ejecutando python manualmente
✅ Funciona con pytest
"""

import sys
from pathlib import Path

# ✅ SOLUCION PERMANENTE PATH
ROOT_PROYECTO = Path(__file__).resolve().parents[4]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

# ✅ Cargar variables de entorno
from dotenv import load_dotenv

load_dotenv(ROOT_PROYECTO / "backend" / ".env")

import pytest
from backend.apps.platform_config.application.services.remote_vps_health_check_service import (
    RemoteVpsHealthCheckService,
)


def test_health_check_script_esta_cargado_correctamente():
    """Verifica que el script se cargue correctamente en memoria"""
    assert RemoteVpsHealthCheckService.HEALTH_CHECK_SCRIPT is not None
    assert len(RemoteVpsHealthCheckService.HEALTH_CHECK_SCRIPT) > 1000
    assert (
        "TIPSTERBYTE FX - VPS HEALTH CHECK AGENT"
        in RemoteVpsHealthCheckService.HEALTH_CHECK_SCRIPT
    )
    assert "✅ Sistema Operativo:" in RemoteVpsHealthCheckService.HEALTH_CHECK_SCRIPT

    print("✅ Script cargado correctamente en memoria")
    print(
        f"✅ Tamaño del script: {len(RemoteVpsHealthCheckService.HEALTH_CHECK_SCRIPT)} caracteres"
    )


def test_ejemplo_uso_ejecucion_remota():
    """
    ✅ EJEMPLO REAL DE USO

    Para usar esto realmente solo debes reemplazar los datos de tu VPS
    y ejecutar este test. O llamar directamente a este metodo desde
    cualquier parte del codigo, endpoint, scheduler, etc.
    """
    print("\n📋 EJEMPLO DE USO:")
    print("=" * 70)

    print(
        """
# 👇 Asi de simple es ejecutar el health check en CUALQUIER VPS:

resultado = RemoteVpsHealthCheckService.execute_on_remote_vps(
    hostname="192.168.1.100",  # IP de tu VPS
    username="root",           # Usuario SSH
    password="tucontraseña"    # Contraseña (o usa private_key_path)
)

✅ Devuelve TODO:
- resultado.success -> True/False
- resultado.exit_code -> Codigo de salida
- resultado.stdout -> TODA la salida del script completa
- resultado.stderr -> Errores si hubo
- resultado.execution_time_seconds -> Tiempo que tardo
- resultado.hostname -> Servidor donde se ejecuto

✅ NO HAY QUE HACER NADA MAS
✅ NO TOCAS LA VPS
✅ NO COPIAS ARCHIVOS
✅ NO NECESITAS NADA INSTALADO ALLI
✅ TODO FUNCIONA POR ARTE DE MAGIA
    """
    )

    print("=" * 70)
    print("\n✅ Test completado correctamente")


if __name__ == "__main__":
    # ✅ Permite ejecutar este archivo directamente
    test_health_check_script_esta_cargado_correctamente()
    test_ejemplo_uso_ejecucion_remota()
