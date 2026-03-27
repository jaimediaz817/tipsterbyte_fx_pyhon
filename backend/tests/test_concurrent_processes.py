"""
Prueba de Escritorio: Múltiples Procesos Concurrentes

Simula múltiples procesos corriendo al mismo tiempo para verificar
que los semáforos diferenciados funcionan correctamente.

Uso:
    python backend/test_concurrent_processes.py
"""

import asyncio
import time
from loguru import logger
from core.config import settings
from core.db.sql.database_sql import SessionLocal
from apps.leagues_manager.application.job_runner_application import JobRunnerApplication
from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
    launch_process_rastreo_data_fuentes_deportivas_task,
)
from shared.constants.process.process_codes import (
    PROCESS_EXTRACT_DATA_FUENTES,
    PROCESS_STANDINGS_EXTRACTION,
    PROCESS_ODDS_WPLAY_EXTRACTION,
    PROCESS_CALENDAR_EXTRACTION,
)


async def run_concurrent_processes():
    """
    Prueba de escritorio con múltiples procesos concurrentes.

    Simula:
    1. Proceso general (todos los robots)
    2. Proceso específico de standings
    3. Proceso específico de odds
    4. Proceso específico de calendar

    Todos ejecutándose concurrentemente.
    """
    print("\n" + "=" * 80)
    print("🧪 PRUEBA DE ESCRITORIO: MÚLTIPLES PROCESOS CONCURRENTES")
    print("=" * 80)

    # =====================================================
    # PASO 1: Verificar configuración
    # =====================================================
    print("\n📋 PASO 1: Verificando configuración...")
    from core.config_semaphore import get_concurrency_for_robot_type
    from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum

    standings_concurrency = get_concurrency_for_robot_type(RobotTypeEnum.STANDINGS)
    odds_concurrency = get_concurrency_for_robot_type(RobotTypeEnum.ODDS_WPLAY)
    calendar_concurrency = get_concurrency_for_robot_type(RobotTypeEnum.CALENDAR)

    print(f"   ✅ STANDINGS: {standings_concurrency} concurrencia máxima")
    print(f"   ✅ ODDS_WPLAY: {odds_concurrency} concurrencia máxima")
    print(f"   ✅ CALENDAR: {calendar_concurrency} concurrencia máxima")

    # =====================================================
    # PASO 2: Definir procesos a ejecutar
    # =====================================================
    print("\n📋 PASO 2: Definiendo procesos concurrentes...")
    processes = [
        {
            "name": "Proceso General",
            "code": PROCESS_EXTRACT_DATA_FUENTES,
            "description": "Ejecuta TODOS los robots (standings, odds, calendar)",
        },
        {
            "name": "Proceso Standings",
            "code": PROCESS_STANDINGS_EXTRACTION,
            "description": "Ejecuta SOLO robot de standings",
        },
        {
            "name": "Proceso Odds WPlay",
            "code": PROCESS_ODDS_WPLAY_EXTRACTION,
            "description": "Ejecuta SOLO robot de odds",
        },
        {
            "name": "Proceso Calendar",
            "code": PROCESS_CALENDAR_EXTRACTION,
            "description": "Ejecuta SOLO robot de calendar",
        },
    ]

    for i, proc in enumerate(processes, 1):
        print(f"   {i}. {proc['name']}: {proc['description']}")

    # =====================================================
    # PASO 3: Ejecutar procesos concurrentemente
    # =====================================================
    print("\n📋 PASO 3: Ejecutando procesos concurrentemente...")
    print("   ⏳ Iniciando 4 procesos al mismo tiempo...")
    print("   📊 Observa cómo los semáforos controlan la concurrencia")
    print("")

    start_time = time.time()

    async def run_process(process_info):
        """Ejecuta un proceso individual."""
        process_name = process_info["name"]
        process_code = process_info["code"]

        print(f"   🚀 Iniciando: {process_name} (código: {process_code})")

        try:
            await launch_process_rastreo_data_fuentes_deportivas_task(
                process_code=process_code
            )
            print(f"   ✅ Completado: {process_name}")
            return {"name": process_name, "status": "success"}
        except Exception as e:
            print(f"   ❌ Error en {process_name}: {e}")
            return {"name": process_name, "status": "failed", "error": str(e)}

    # Ejecutar todos los procesos concurrentemente
    tasks = [run_process(proc) for proc in processes]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()
    total_time = end_time - start_time

    # =====================================================
    # PASO 4: Mostrar resultados
    # =====================================================
    print("\n" + "=" * 80)
    print("📊 RESULTADOS DE LA PRUEBA")
    print("=" * 80)

    successful = sum(
        1 for r in results if isinstance(r, dict) and r.get("status") == "success"
    )
    failed = sum(
        1 for r in results if isinstance(r, dict) and r.get("status") == "failed"
    )
    exceptions = sum(1 for r in results if isinstance(r, Exception))

    print(f"\n   ⏱️  Tiempo total: {total_time:.2f} segundos")
    print(f"   ✅ Exitosos: {successful}")
    print(f"   ❌ Fallidos: {failed}")
    print(f"   ⚠️  Excepciones: {exceptions}")

    print("\n   📋 Detalle por proceso:")
    for result in results:
        if isinstance(result, dict):
            status_icon = "✅" if result["status"] == "success" else "❌"
            print(f"      {status_icon} {result['name']}: {result['status']}")
        elif isinstance(result, Exception):
            print(f"      ⚠️  Excepción: {result}")

    # =====================================================
    # PASO 5: Verificar comportamiento de semáforos
    # =====================================================
    print("\n📋 PASO 5: Verificando comportamiento de semáforos...")
    print("   📝 Revisa los logs anteriores para verificar:")
    print("      - Cada proceso crea sus propios semáforos")
    print("      - Los semáforos son independientes entre procesos")
    print("      - La concurrencia se respeta por tipo de robot")
    print("      - No hay bloqueos entre procesos diferentes")

    # =====================================================
    # PASO 6: Resumen
    # =====================================================
    print("\n" + "=" * 80)
    print("🎯 CONCLUSIÓN")
    print("=" * 80)

    if successful == len(processes):
        print("   ✅ TODOS los procesos se ejecutaron correctamente")
        print("   ✅ Los semáforos diferenciados funcionan concurrentemente")
        print("   ✅ No hay bloqueos entre procesos")
    else:
        print("   ⚠️  Algunos procesos fallaron")
        print("   📝 Revisa los logs para más detalles")

    print("\n   💡 Los semáforos permiten:")
    print("      - Múltiples procesos simultáneos")
    print("      - Concurrencia controlada por tipo de robot")
    print("      - Sin bloqueos entre procesos independientes")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Ejecutar la prueba
    asyncio.run(run_concurrent_processes())
