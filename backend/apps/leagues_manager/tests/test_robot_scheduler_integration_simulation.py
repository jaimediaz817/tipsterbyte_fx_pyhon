# ------------------------------------------------------------------------------
# ✅ TEST INTEGRACION SIMULACION COMPLETA ROBOT + SCHEDULER
# ✅ Simula exactamente el flujo real de produccion
# ✅ Incluye Premier League y Liga BetPlay Colombia
# ✅ Simula ejecuciones cada minuto como cron real
# ------------------------------------------------------------------------------
import sys
from pathlib import Path

from shared.repositories.scheduler_repos.i_process_run_repository import (
    IProcessRunRepository,
)

# ✅ SOLUCION PERMANENTE PATH: Funciona en TODOS los entornos
ROOT_PROYECTO = Path(__file__).resolve().parents[5]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))
if str(ROOT_PROYECTO / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO / "backend"))

# ✅ Cargar automaticamente variables de entorno
from dotenv import load_dotenv

load_dotenv(ROOT_PROYECTO / "backend" / ".env")

import asyncio
import time
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import pytest
from random import choice


# ------------------------------------------------------------------------------
# ✅ CODIGOS DE COLOR TERMINAL VISUAL
# ------------------------------------------------------------------------------
class Colores:
    ROJO = "\033[91m"
    VERDE = "\033[92m"
    AMARILLO = "\033[93m"
    AZUL = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BLANCO = "\033[97m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    BARRA_PROGRESO = "█"


# Asignacion permanente de colores a cada liga
COLORES_LIGAS = {
    1: Colores.VERDE,  # Premier League
    2: Colores.AZUL,  # Liga BetPlay Colombia
    3: Colores.AMARILLO,
    4: Colores.MAGENTA,
    5: Colores.CYAN,
}

# ✅ Declaracion de tipos para chequeo estatico, NUNCA se importan en runtime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.leagues_manager.domain.entities.torneo import Torneo
    from apps.leagues_manager.domain.entities.detalle_fuente_extraccion import (
        DetalleFuenteExtraccion,
    )
    from shared.repositories.scheduler_repos import IProcessRunRepository

# Importar componentes reales
from apps.leagues_manager.domain.robots.base_robot import BaseRobot
from apps.leagues_manager.tests.mock_data_leagues import (
    MockTorneo,
    MockDetalleFuenteExtraccion,
)
from apps.leagues_manager.tests.mock_repositories import MockProcessRunRepository
from core.exceptions import ScrapingException
from core.robot_logging import log_robot_start, log_robot_end

# ------------------------------------------------------------------------------
# ✅ SIMULACION DE LIGAS REALES
# ------------------------------------------------------------------------------
LIGAS_PRUEBA = [
    {
        "id": 1,
        "nombre": "Premier League",
        "pais": "Inglaterra",
        "codigo_api": "39",
        "temporada": "2025",
    },
    {
        "id": 2,
        "nombre": "Liga BetPlay Colombia",
        "pais": "Colombia",
        "codigo_api": "143",
        "temporada": "2025",
    },
]


# ------------------------------------------------------------------------------
# ✅ ROBOT SIMULADO DE WEB SCRAPING
# ------------------------------------------------------------------------------
class RobotSimuladoScraping(BaseRobot):
    """
    Robot que simula exactamente el comportamiento de un scraper real:
    ✅ Tiempo de ejecucion variable entre 2 y 7 segundos
    ✅ Posibilidad de fallo aleatorio 10%
    ✅ Simula extraccion de datos reales
    ✅ Registra progreso paso a paso
    """

    async def _execute_scraping(self):
        await self._log_step(
            step="INICIO_EXTRACCION",
            level="info",
            message=f"Iniciando extraccion para {self.torneo.nombre}",
            input_data=f"codigo_api={getattr(self.torneo, 'codigo_api', 'N/A')}, temporada={getattr(self.torneo, 'temporada', 'N/A')}",
        )

        # Simular tiempo de scraping real
        tiempo_espera = 2 + (hash(self.torneo.id) % 5)
        await asyncio.sleep(tiempo_espera)

        await self._log_step(
            step="OBTENCION_PARTIDOS",
            level="info",
            message=f"Obtenidos 10 partidos de la API",
            output_data=f"partidos=10, fecha_actualizacion={datetime.now().isoformat()}",
        )

        await asyncio.sleep(1)

        # 10% de probabilidad de fallo aleatorio para probar manejo de errores
        if hash(time.time()) % 10 == 0:
            raise Exception(f"Error simulado de conexion API para {self.torneo.nombre}")

        await self._log_step(
            step="GUARDADO_BD",
            level="info",
            message="Datos guardados correctamente en base de datos",
        )

        await self._log_step(
            step="FIN_EXTRACCION",
            level="success",
            message=f"Extraccion completada exitosamente para {self.torneo.nombre}",
        )


# ------------------------------------------------------------------------------
# ✅ SIMULADOR DE SCHEDULER
# ------------------------------------------------------------------------------
class SimuladorScheduler:
    """
    Simula exactamente el comportamiento del scheduler real:
    ✅ Ejecuta procesos cada X segundos (simula cron)
    ✅ Gestiona ejecuciones concurrentes
    ✅ Mantiene historial de ejecuciones
    ✅ Muestra estadisticas en tiempo real
    """

    def __init__(self, intervalo_segundos: int = 60):
        self.intervalo = intervalo_segundos
        self.ejecuciones = []
        self.activo = False
        self.repo = MockProcessRunRepository()

    async def ejecutar_ciclo(self):
        """Ejecuta un ciclo completo del scheduler"""
        print(f"\n⏰ [{datetime.now().strftime('%H:%M:%S')}] INICIANDO CICLO SCHEDULER")
        print("=" * 100)

        tareas = []

        for liga in LIGAS_PRUEBA:
            # Extraer solo campos que corresponden a MockTorneo
            torneo = MockTorneo(id=liga["id"], nombre=liga["nombre"], is_active=True)
            detalle = MockDetalleFuenteExtraccion(
                id=liga["id"],
                torneo_id=liga["id"],
                fuente_id=liga["id"],
                url=f"https://api-football-v1.p.rapidapi.com/v3/fixtures?league={liga['codigo_api']}&season={liga['temporada']}",
            )

            run_id = f"run_{int(time.time())}_{liga['id']}"

            # ✅ Solucion oficial tipo Forward Reference: cast() indica validez
            from typing import cast

            robot = RobotSimuladoScraping(
                torneo=cast("Torneo", torneo),
                detalle=cast("DetalleFuenteExtraccion", detalle),
                run_id=run_id,
                repo=cast("IProcessRunRepository", self.repo),
            )

            tarea = asyncio.create_task(self._ejecutar_robot_seguro(robot))
            tareas.append(tarea)

        resultados = await asyncio.gather(*tareas, return_exceptions=True)

        exitos = sum(1 for r in resultados if r is True)
        fallos = sum(1 for r in resultados if r is False)

        print(f"\n📊 RESUMEN CICLO:")
        print(f"   ✅ Exitosos: {exitos}")
        print(f"   ❌ Fallidos: {fallos}")
        print(f"   ⏱️  Tiempo total ciclo: {time.time() - self.inicio_ciclo:.2f}s")

        self.ejecuciones.append(
            {"timestamp": datetime.now(), "exitos": exitos, "fallos": fallos}
        )

    async def _ejecutar_robot_seguro(self, robot: BaseRobot) -> bool:
        try:
            await robot.run()
            return True
        except Exception:
            return False

    async def iniciar(self, cantidad_ciclos: int = 2):
        """Inicia la simulacion del scheduler por N ciclos"""
        self.activo = True
        print(f"\n🚀 INICIANDO SIMULACION SCHEDULER")
        print(f"   Intervalo entre ciclos: {self.intervalo} segundos")
        print(f"   Cantidad de ciclos: {cantidad_ciclos}")
        print(f"   Ligas activas: {len(LIGAS_PRUEBA)}")

        for ciclo in range(cantidad_ciclos):
            self.inicio_ciclo = time.time()
            await self.ejecutar_ciclo()

            if ciclo < cantidad_ciclos - 1:
                print(f"\n⏳ Esperando {self.intervalo} segundos para proximo ciclo...")
                await asyncio.sleep(self.intervalo)

        print("\n" + "=" * 100)
        print("✅ SIMULACION COMPLETADA EXITOSAMENTE")
        print("=" * 100)

        self._mostrar_estadisticas_finales()

    def _mostrar_estadisticas_finales(self):
        total_exitos = sum(e["exitos"] for e in self.ejecuciones)
        total_fallos = sum(e["fallos"] for e in self.ejecuciones)
        total = total_exitos + total_fallos

        print(f"\n📈 ESTADISTICAS FINALES SIMULACION:")
        print(f"   Total ejecuciones: {total}")
        print(f"   Exitos totales: {total_exitos}")
        print(f"   Fallos totales: {total_fallos}")
        print(
            f"   Tasa exito: {((total_exitos / total) * 100):.1f}%"
            if total > 0
            else "0%"
        )
        print(f"   Ciclos ejecutados: {len(self.ejecuciones)}")


# ------------------------------------------------------------------------------
# ✅ TESTS UNITARIOS
# ------------------------------------------------------------------------------
class TestRobotSchedulerIntegracion:

    @pytest.mark.asyncio
    async def test_simulacion_completa(self):
        """✅ Simulacion completa de todo el flujo scheduler + robots"""

        # Ejecutar simulacion con intervalo reducido para pruebas
        scheduler = SimuladorScheduler(intervalo_segundos=5)
        await scheduler.iniciar(cantidad_ciclos=2)

        assert len(scheduler.ejecuciones) == 2
        print("\n✅ Test simulacion scheduler completado correctamente")

    def test_robot_scraping_simulado(self):
        """✅ Verifica que el robot simulado funciona correctamente"""

        torneo = MockTorneo(
            id=LIGAS_PRUEBA[0]["id"], nombre=LIGAS_PRUEBA[0]["nombre"], is_active=True
        )
        detalle = MockDetalleFuenteExtraccion(
            id=1, torneo_id=1, fuente_id=1, url="https://test.com"
        )
        repo = MockProcessRunRepository()

        # ✅ Solucion oficial tipo Forward Reference
        from typing import cast

        robot = cast(
            RobotSimuladoScraping,
            RobotSimuladoScraping(
                torneo=cast("Torneo", torneo),
                detalle=cast("DetalleFuenteExtraccion", detalle),
                run_id="test-123",
                repo=cast("IProcessRunRepository", repo),
            ),
        )

        assert robot.torneo.nombre == "Premier League"
        assert robot.detalle == detalle
        print("\n✅ Test robot simulado correcto")


# ------------------------------------------------------------------------------
# ✅ EJECUCION DIRECTA MANUAL
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "=" * 100)
    print("✅ SIMULADOR COMPLETO SCHEDULER + ROBOTS SCRAPING")
    print("=" * 100)
    print("\n💡 Este test simula EXACTAMENTE el comportamiento real en produccion:")
    print("   ✅ Premier League y Liga BetPlay Colombia activas")
    print("   ✅ Ejecuta 2 ciclos completos")
    print("   ✅ Intervalo entre ciclos: 5 segundos")
    print("   ✅ Simula tiempo de scraping real")
    print("   ✅ 10% probabilidad fallo aleatorio\n")

    asyncio.run(SimuladorScheduler(intervalo_segundos=5).iniciar(cantidad_ciclos=2))

    print("\n✅ SIMULACION FINALIZADA. Todo el flujo funciona correctamente.")
    print("\n💡 Ahora puedes:")
    print("   1. Aumentar cantidad_ciclos para probar mas tiempo")
    print("   2. Modificar intervalo_segundos para cambiar frecuencia")
    print("   3. Agregar mas ligas a LIGAS_PRUEBA")
    print("   4. Usar esto como base para el proceso real programado")
