"""
Script de prueba para ejecutar manualmente el proceso de extracción.
"""

import asyncio
from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
    launch_process_rastreo_data_fuentes_deportivas_task,
)


async def main():
    print("=" * 70)
    print("🧪 EJECUCIÓN MANUAL DEL PROCESO DE EXTRACCIÓN")
    print("=" * 70)

    try:
        await launch_process_rastreo_data_fuentes_deportivas_task()
        print("\n✅ Proceso completado exitosamente")
    except Exception as e:
        print(f"\n❌ Error en la ejecución: {e}")


if __name__ == "__main__":
    asyncio.run(main())
