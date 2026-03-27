"""
Script de prueba manual para ejecutar limpieza de logs.
"""

import sys
from pathlib import Path

# Agregar directorio backend al path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from core.scheduler.log_cleanup_jobs import (
    LOG_CLEANUP_PROCESS_MAP,
    create_log_cleanup_job,
)
from services.log_cleanup_service import LogCleanupService


def main():
    print("=" * 80)
    print("PRUEBA MANUAL DE LIMPIEZA DE LOGS")
    print("=" * 80)

    # Verificar jobs registrados
    print("\n1. Jobs de limpieza de logs registrados:")
    for job_id, job_func in LOG_CLEANUP_PROCESS_MAP.items():
        print(f"   - {job_id}: {job_func}")

    # Ejecutar job de limpieza
    print("\n2. Ejecutando job de limpieza de logs...")
    job = LOG_CLEANUP_PROCESS_MAP.get("PROCESS_LOG_CLEANUP")
    if job:
        try:
            result = job()
            print(f"   Resultado: {result}")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("   ERROR: Job PROCESS_LOG_CLEANUP no encontrado")

    # Ejecutar servicio directamente
    print("\n3. Ejecutando LogCleanupService directamente...")
    service = LogCleanupService()
    try:
        result = service.run_cleanup()
        print(f"   Resultado del servicio: {result}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n" + "=" * 80)
    print("PRUEBA COMPLETADA")
    print("=" * 80)


if __name__ == "__main__":
    main()
