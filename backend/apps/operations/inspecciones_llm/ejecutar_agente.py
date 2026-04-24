"""
✅ Script para ejecutar el Agente Supervisor en modo standalone
Ejecuta este archivo para poner a trabajar al tercer miembro del equipo
"""

import sys
from pathlib import Path

# ✅ Correcion path permanente
ROOT_PROYECTO = Path(__file__).resolve().parents[1]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

import asyncio
from inspecciones_llm.agente_supervisor import agente_supervisor, EstadoTarea


async def demo_agente():
    print("🤖 Iniciando DEMO Agente Supervisor TipsterByte FX")
    print("=" * 80)

    # Registrar algunas tareas de ejemplo
    agente_supervisor.registrar_tarea(
        id="tarea_002",
        nombre="Limpieza automatica de logs",
        descripcion="Revisar y limpiar logs antiguos cada 24 horas",
        asignado_a="AGENTE_SUPERVISOR_001",
    )

    agente_supervisor.registrar_tarea(
        id="tarea_003",
        nombre="Monitoreo VPS Principal",
        descripcion="Verificar estado de salud del VPS cada 5 minutos",
        asignado_a="AGENTE_SUPERVISOR_001",
    )

    agente_supervisor.registrar_tarea(
        id="tarea_004",
        nombre="Verificacion consistencia BD",
        descripcion="Validar integridad de tablas principales",
        asignado_a="AGENTE_SUPERVISOR_001",
    )

    # Mostrar estado inicial
    print("\n📋 Estado inicial del tablero:")
    print("-" * 60)
    print(agente_supervisor.generar_reporte_md())

    print("\n🚀 Iniciando ciclo infinito del agente...")
    print("   Presiona CTRL+C para detener")
    print("=" * 80)

    # Iniciar el agente
    await agente_supervisor.iniciar()


if __name__ == "__main__":
    try:
        asyncio.run(demo_agente())
    except KeyboardInterrupt:
        print("\n✅ Demo finalizada correctamente")
        print("\n📋 Estado final del tablero:")
        print("-" * 60)
        print(agente_supervisor.generar_reporte_md())
