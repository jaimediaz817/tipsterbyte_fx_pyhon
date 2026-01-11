from .mock_data_leagues import MockLiga, MockTorneo, MockDetalleFuenteExtraccion, MockFuenteExtraccion

class MockPlatformRepository:
    """
    Repositorio simulado que construye la jerarquía de datos completa,
    simulando los JOINs que haría una consulta SQL real.
    """
    def __init__(self, session=None):
        # --- Simulación de Tablas de la Base de Datos ---

        # 1. Tabla Catálogo: FuenteExtraccion
        self._fuentes = {
            1: MockFuenteExtraccion(id=1, name="Standings (SofaScore)", type="standings"),
            2: MockFuenteExtraccion(id=2, name="Odds (WPlay)", type="odds_wplay"),
            3: MockFuenteExtraccion(id=3, name="Calendar (Official)", type="calendar"),
            4: MockFuenteExtraccion(id=4, name="Odds (Betfair)", type="odds_betfair"),
        }

        # 2. Tabla Pivote: DetalleFuenteExtraccion
        self._detalles = [
            # Fuentes para LaLiga 2025-2026
            MockDetalleFuenteExtraccion(torneo_id=101, fuente_id=1, url="http://sofascore.com/laliga/25-26/standings"),
            MockDetalleFuenteExtraccion(torneo_id=101, fuente_id=2, url="http://wplay.co/laliga/25-26/odds"),
            # Fuentes para Premier League 2025-2026
            MockDetalleFuenteExtraccion(torneo_id=201, fuente_id=1, url="http://sofascore.com/premier/25-26/standings"),
            MockDetalleFuenteExtraccion(torneo_id=201, fuente_id=3, url="http://premierleague.com/25-26/calendar"),
            MockDetalleFuenteExtraccion(torneo_id=201, fuente_id=4, url="http://betfair.com/premier/25-26/odds", is_active=False), # Inactiva
        ]

        # 3. Tabla: Torneos
        self._torneos = {
            101: MockTorneo(id=101, name="LaLiga 2025-2026", is_active=True),
            102: MockTorneo(id=102, name="LaLiga 2026-2027", is_active=False),
            201: MockTorneo(id=201, name="Premier League 2025-2026", is_active=True),
            401: MockTorneo(id=401, name="Serie A 2025-2026", is_active=True),
        }

        # 4. Tabla: Ligas
        self._ligas = [
            MockLiga(id=1, name="LaLiga EA Sports", is_active=True, torneos=[self._torneos[101], self._torneos[102]]),
            MockLiga(id=2, name="Premier League", is_active=True, torneos=[self._torneos[201]]),
            MockLiga(id=3, name="Ligue 1", is_active=False, torneos=[]),
            MockLiga(id=4, name="Serie A", is_active=True, torneos=[self._torneos[401]]),
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
                if detalle.fuente: # Solo añadir si la fuente existe
                    torneo.detalles_fuente.append(detalle)
        
        return self._ligas