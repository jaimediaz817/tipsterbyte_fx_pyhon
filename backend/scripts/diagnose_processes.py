#!/usr/bin/env python
"""Script de diagnóstico para verificar procesos en la base de datos."""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.sql.database_sql import SessionLocal
from apps.platform_config.infrastructure.models.sql.process import Process


def main():
    """Función principal de diagnóstico."""
    print("=" * 60)
    print("DIAGNOSTICO DE PROCESOS EN LA BASE DE DATOS")
    print("=" * 60)

    try:
        with SessionLocal() as db:
            processes = db.query(Process).all()
            print(f"\nTotal de procesos en BD: {len(processes)}")

            if processes:
                print("\nDetalle de procesos:")
                for p in processes:
                    status = "ACTIVO" if bool(p.is_active) else "INACTIVO"
                    print(f"  - {p.code}: {p.name} [{status}]")
            else:
                print("\nNo hay procesos registrados en la base de datos.")

            # Verificar procesos activos
            active_processes = [p for p in processes if bool(p.is_active)]
            print(f"\nProcesos activos: {len(active_processes)}")

            # Verificar procesos inactivos
            inactive_processes = [p for p in processes if not bool(p.is_active)]
            print(f"Procesos inactivos: {len(inactive_processes)}")

    except Exception as e:
        print(f"\nError al conectar con la base de datos: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("DIAGNOSTICO COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
