#!/usr/bin/env python
"""
Script de prueba para verificar que los logs de los robots se están registrando correctamente.
Ejecuta cada robot individualmente y muestra los logs en tiempo real.
"""

import asyncio
from datetime import datetime
from loguru import logger
import sys  # <-- ¡IMPORTADO!
import os  # <-- ¡IMPORTADO!

# --- INICIO: Configuración para asegurar que Python encuentre los módulos ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# Subimos tres niveles desde 'tests' para llegar a 'backend'
# tests -> leagues_manager -> apps -> backend
backend_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)
# --- FIN: Configuración para asegurar que Python encuentre los módulos ---

# Ahora estas importaciones deberían funcionar
from apps.leagues_manager.tests.mock_data_leagues import (
    MockTorneo,
    MockDetalleFuenteExtraccion,
    MockFuenteExtraccion,
)
from apps.leagues_manager.robots.calendar_robot import CalendarRobot
from apps.leagues_manager.robots.odds_wplay_robot import OddsWPlayRobot
from apps.leagues_manager.robots.standings_robot import StandingsRobot


class MockProcessRunRepository:
    """Mock del repositorio de logs que almacena los logs en memoria."""

    def __init__(self):
        self.logs = []
        self.runs = {}

    def create_run(self, run_id: str, process_code: str):
        """Simula la creación de un ProcessRun."""
        self.runs[run_id] = {
            "run_id": run_id,
            "process_code": process_code,
            "status": "in_progress",
            "started_at": datetime.now(),
        }
        logger.info(f"📋 [MOCK] ProcessRun creado: run_id={run_id}")
        return self.runs[run_id]

    def complete_run(self, run_id: str) -> None:
        """Simula la finalización de un ProcessRun."""
        if run_id in self.runs:
            self.runs[run_id]["status"] = "success"
            self.runs[run_id]["ended_at"] = datetime.now()
            logger.success(f"✅ [MOCK] ProcessRun completado: run_id={run_id}")

    def fail_run(self, run_id: str) -> None:
        """Simula el fallo de un ProcessRun."""
        if run_id in self.runs:
            self.runs[run_id]["status"] = "failed"
            self.runs[run_id]["ended_at"] = datetime.now()
            logger.error(f"❌ [MOCK] ProcessRun fallido: run_id={run_id}")

    def write_log(
        self,
        run_id: str,
        step: str,
        level: str,  # El nivel del log es ahora un argumento obligatorio
        message: str,
        detalle_fuente_extraccion_id: int | None = None,
        input: str | None = None,
        output: str | None = None,
    ) -> None:
        """Registra un log en memoria."""
        log_entry = {
            "run_id": run_id,
            "step": step,
            "level": level,
            "message": message,
            "detalle_fuente_extraccion_id": detalle_fuente_extraccion_id,
            "input": input,
            "output": output,
            "timestamp": datetime.now(),
        }
        self.logs.append(log_entry)
        # Simular el guardado en BD (sin hacer commit real)
        logger.debug(
            f"💾 [MOCK] Log guardado en BD: step={step} | level={level} | message={message[:50]}..."
        )

    def get_logs_summary(self):
        """Devuelve un resumen de los logs registrados."""
        summary = {
            "total_logs": len(self.logs),
            "by_level": {},
            "by_step": {},
        }
        for log in self.logs:
            level = log["level"]
            step = log["step"]
            summary["by_level"][level] = summary["by_level"].get(level, 0) + 1
            summary["by_step"][step] = summary["by_step"].get(step, 0) + 1
        return summary


# RENOMBRADA: Antes era 'test_robot'
async def run_robot_test(robot_class, robot_name, torneo, detalle, run_id, repo):
    """Ejecuta un robot individual y muestra los logs."""
    logger.info(f"\n{'='*80}")
    logger.info(f"🤖 PROBANDO ROBOT: {robot_name}")
    logger.info(f"{'='*80}")

    try:
        # Crear instancia del robot
        robot = robot_class(torneo, detalle, run_id, repo)

        # Ejecutar el robot
        await robot.run()

        logger.info(f"✅ Robot {robot_name} ejecutado exitosamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error ejecutando robot {robot_name}: {e}")
        return False


async def main():
    """Función principal que ejecuta las pruebas de logs."""
    logger.info("🚀 INICIANDO PRUEBA DE LOGS DE ROBOTS")
    logger.info(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    # Crear mock del repositorio
    mock_repo = MockProcessRunRepository()

    # Crear datos de prueba
    run_id = f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    # La llamada a create_run en el mock debe coincidir con la de tu repositorio real
    mock_repo.create_run(run_id, "TEST_PROCESS")

    # Crear fuentes mock
    fuente_standings = MockFuenteExtraccion(
        id=1, name="Tabla (SofaScore)", type="standings"
    )
    fuente_odds = MockFuenteExtraccion(id=2, name="Wplay (WPlay)", type="odds_wplay")
    fuente_calendar = MockFuenteExtraccion(
        id=3, name="Calendar (Official)", type="calendar"
    )

    # Crear torneos mock
    torneo1 = MockTorneo(id=101, nombre="Premier League 2025-2026", is_active=True)
    torneo2 = MockTorneo(id=102, nombre="LaLiga 2025-2026", is_active=True)
    torneo3 = MockTorneo(id=103, nombre="Serie A 2025-2026", is_active=True)

    # Crear detalles mock
    detalle_standings = MockDetalleFuenteExtraccion(
        id=1,
        torneo_id=101,
        fuente_id=1,
        url="http://sofascore.com/premier-league/25-26/standings",
        fuente=fuente_standings,
    )

    detalle_odds = MockDetalleFuenteExtraccion(
        id=2,
        torneo_id=102,
        fuente_id=2,
        url="http://wplay.co/laliga/25-26/odds",
        fuente=fuente_odds,
    )

    detalle_calendar = MockDetalleFuenteExtraccion(
        id=3,
        torneo_id=103,
        fuente_id=3,
        url="http://official.com/serie-a/25-26/calendar",
        fuente=fuente_calendar,
    )

    # Ejecutar cada robot
    results = []

    # 1. StandingsRobot
    result_standings = await run_robot_test(
        StandingsRobot,
        "StandingsRobot",
        torneo1,
        detalle_standings,
        run_id,
        mock_repo,
    )
    results.append(("StandingsRobot", result_standings))

    # 2. OddsWPlayRobot
    result_odds = await run_robot_test(
        OddsWPlayRobot,
        "OddsWPlayRobot",
        torneo2,
        detalle_odds,
        run_id,
        mock_repo,
    )
    results.append(("OddsWPlayRobot", result_odds))

    # 3. CalendarRobot
    result_calendar = await run_robot_test(
        CalendarRobot,
        "CalendarRobot",
        torneo3,
        detalle_calendar,
        run_id,
        mock_repo,
    )
    results.append(("CalendarRobot", result_calendar))

    # Marcar el run como completado
    mock_repo.complete_run(run_id)

    # Mostrar resumen de logs
    logger.info("\n" + "=" * 80)
    logger.info("📊 RESUMEN DE LOGS REGISTRADOS")
    logger.info("=" * 80)

    summary = mock_repo.get_logs_summary()
    logger.info(f"Total de logs: {summary['total_logs']}")
    logger.info(f"\nPor nivel:")
    for level, count in summary["by_level"].items():
        logger.info(f"  - {level}: {count}")

    logger.info(f"\nPor paso:")
    for step, count in summary["by_step"].items():
        logger.info(f"  - {step}: {count}")

    # Mostrar logs detallados
    logger.info("\n" + "=" * 80)
    logger.info("📋 LOGS DETALLADOS")
    logger.info("=" * 80)

    for i, log in enumerate(mock_repo.logs, 1):
        timestamp = log["timestamp"].strftime("%H:%M:%S.%f")[:-3]
        level_icon = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "debug": "🔍",
        }.get(log["level"], "📝")

        logger.info(
            f"{i:2d}. [{timestamp}] {level_icon} [{log['step']:10s}] {log['message']}"
        )

    # Resultado final
    logger.info("\n" + "=" * 80)
    logger.info("🏁 RESULTADO FINAL")
    logger.info("=" * 80)

    all_passed = all(result for _, result in results)
    for robot_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"  {robot_name}: {status}")

    logger.info(
        f"\n{'✅ TODAS LAS PRUEBAS PASARON' if all_passed else '❌ ALGUNAS PRUEBAS FALLARON'}"
    )

    return all_passed


if __name__ == "__main__":
    # Configurar loguru para mostrar todos los niveles
    logger.remove()  # Remover handler por defecto
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {message}\n",
        level="TRACE",
    )

    # Ejecutar las pruebas
    success = asyncio.run(main())
    exit(0 if success else 1)
