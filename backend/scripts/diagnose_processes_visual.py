#!/usr/bin/env python
"""Diagnóstico Visual de Procesos - Herramienta de Medición de Fiabilidad."""

import sys
import os
import logging

# Deshabilitar logs de SQLAlchemy y otros módulos para diagnóstico limpio
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("core.db.sql").setLevel(logging.WARNING)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.sql.database_sql import SessionLocal
from apps.platform_config.infrastructure.models.sql.process import Process
from apps.platform_config.infrastructure.models.sql.process_run import ProcessRun
from datetime import datetime
from sqlalchemy import func


def create_visual_bar(percentage: float, length: int = 30) -> str:
    """Crea barra de progreso visual."""
    filled = int(length * percentage / 100)
    empty = length - filled
    if percentage >= 80:
        symbol = "#"
        color = "[OK]"
    elif percentage >= 50:
        symbol = "="
        color = "[WARN]"
    else:
        symbol = "-"
        color = "[ERR]"
    return f"{color} [{'#' * filled}{'.' * empty}] {percentage:.1f}%"


def get_reliability_from_db(db, process_id) -> float:
    """Calcula la fiabilidad de un proceso basándose en ProcessRun de la DB."""
    total_runs = (
        db.query(ProcessRun).filter(ProcessRun.process_id == process_id).count()
    )
    if total_runs == 0:
        return 0.0

    successful_runs = (
        db.query(ProcessRun)
        .filter(ProcessRun.process_id == process_id, ProcessRun.status == "success")
        .count()
    )

    return (successful_runs / total_runs) * 100


def get_reliability_emoji(reliability: float) -> str:
    """Retorna indicador según nivel de fiabilidad."""
    if reliability >= 90:
        return "[OK]"
    elif reliability >= 70:
        return "[WARN]"
    elif reliability >= 50:
        return "[MED]"
    else:
        return "[ERR]"


def main():
    """Función principal de diagnóstico visual."""
    print("\n" + "=" * 70)
    print("DIAGNOSTICO VISUAL DE PROCESOS")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    try:
        with SessionLocal() as db:
            processes = db.query(Process).all()
            if not processes:
                print("\nNo hay procesos registrados.")
                return

            print(f"\nTotal de procesos: {len(processes)}")
            print("-" * 70)

            active = [p for p in processes if bool(p.is_active)]
            inactive = [p for p in processes if not bool(p.is_active)]

            if active:
                print(f"\nPROCESOS ACTIVOS ({len(active)})")
                print("-" * 70)
                for process in active:
                    reliability = get_reliability_from_db(db, process.id)
                    emoji = get_reliability_emoji(reliability)
                    bar = create_visual_bar(reliability)
                    print(f"\n  {emoji} {process.code}")
                    print(f"     Nombre: {process.name}")
                    print(f"     Fiabilidad: {bar}")

            if inactive:
                print(f"\nPROCESOS INACTIVOS ({len(inactive)})")
                print("-" * 70)
                for process in inactive:
                    print(f"\n  [X] {process.code}")
                    print(f"     Nombre: {process.name}")

            print("\n" + "=" * 70)
            print("RESUMEN GENERAL")
            print("=" * 70)
            total = len(processes)
            print(f"\n  Total: {total}")
            print(f"  Activos: {len(active)} ({len(active)/total*100:.1f}%)")
            print(f"  Inactivos: {len(inactive)} ({len(inactive)/total*100:.1f}%)")

            if active:
                avg = sum(get_reliability_from_db(db, p.id) for p in active) / len(
                    active
                )
                print(f"\n  Fiabilidad promedio: {create_visual_bar(avg)}")

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("DIAGNOSTICO COMPLETADO")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
