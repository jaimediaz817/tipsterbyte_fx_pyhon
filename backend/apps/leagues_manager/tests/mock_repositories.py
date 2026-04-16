from typing import Optional, Dict, Any

from .mock_data_leagues import (
    MockLiga,
    MockTorneo,
    MockDetalleFuenteExtraccion,
    MockFuenteExtraccion,
)


class MockPlatformRepository:
    """
    Repositorio simulado que construye la jerarquía de datos completa,
    simulando los JOINs que haría una consulta SQL real.
    """

    def __init__(self, session=None):
        # --- Simulación de Tablas de la Base de Datos ---

        # 1. Tabla Catálogo: FuenteExtraccion
        self._fuentes = {
            1: MockFuenteExtraccion(id=1, name="Tabla (SofaScore)", type="standings"),
            2: MockFuenteExtraccion(id=2, name="Wplay (WPlay)", type="odds_wplay"),
            3: MockFuenteExtraccion(id=3, name="Calendar (Official)", type="calendar"),
        }

        # 2. Tabla Pivote: DetalleFuenteExtraccion
        self._detalles = [
            # Fuentes para LaLiga 2025-2026
            MockDetalleFuenteExtraccion(
                id=1,
                torneo_id=101,
                fuente_id=1,
                url="http://sofascore.com/laliga/25-26/standings",
            ),
            MockDetalleFuenteExtraccion(
                id=2,
                torneo_id=101,
                fuente_id=2,
                url="http://wplay.co/laliga/25-26/otra-fuente",
            ),
        ]

        # 3. Tabla: Torneos
        self._torneos = {
            101: MockTorneo(id=101, nombre="Premier League 2025-2026", is_active=True),
            102: MockTorneo(id=102, nombre="Premier League 2026-2027", is_active=True),
        }

        # 4. Tabla: Ligas
        self._ligas = [
            MockLiga(
                id=1,
                name="PREMIER LEAGUE",
                is_active=True,
                torneos=[self._torneos[101], self._torneos[102]],
            ),
        ]

    def get_all_leagues_with_full_details(self):
        """
        Simula la consulta SQL compleja que une Ligas -> Torneos -> Detalles -> Fuentes.
        Devuelve la estructura de datos anidada y lista para ser procesada.
        """
        # Simulación del JOIN: Añadimos los detalles a cada torneo
        for detalle in self._detalles:
            if detalle.torneo_id in self._torneos:
                torneo = self._torneos[detalle.torneo_id]
                # Simulamos el JOIN con la tabla de fuentes para tener el objeto completo
                detalle.fuente = self._fuentes.get(detalle.fuente_id)
                if detalle.fuente:  # Solo añadir si la fuente existe
                    torneo.detalles_fuente.append(detalle)

        return self._ligas


class MockProcessRunRepository:
    """
    Repositorio mock para logs de ejecucion de robots y procesos
    Implementa la interfaz IProcessRunRepository
    """

    def __init__(self):
        self._logs = []

    async def create_run(
        self, run_id: str, process_name: str, details: Optional[Dict[str, Any]] = None
    ):
        pass

    async def update_status(
        self, run_id: str, status: str, details: Optional[Dict[str, Any]] = None
    ):
        pass

    async def add_log_entry(
        self, run_id: str, step: str, level: str, message: str, **kwargs
    ):
        """Agrega entrada de log al repositorio mock"""
        self._logs.append(
            {
                "run_id": run_id,
                "step": step,
                "level": level,
                "message": message,
                **kwargs,
            }
        )

    def get_logs(self, run_id: str):
        """Obtiene todos los logs registrados para un run_id"""
        return [log for log in self._logs if log["run_id"] == run_id]

    async def write_log(
        self,
        run_id: str,
        step: str,
        level: str,
        message: str,
        input: Optional[str] = None,
        **kwargs,
    ):
        """
        ✅ Metodo de compatibilidad con la interfaz real
        Alias para add_log_entry, usado por BaseRobot
        """
        return await self.add_log_entry(
            run_id, step, level, message, input=input, **kwargs
        )
