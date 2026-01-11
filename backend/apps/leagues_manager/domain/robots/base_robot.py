import asyncio
from abc import ABC, abstractmethod
from loguru import logger
from typing import TYPE_CHECKING, Dict, Type

if TYPE_CHECKING:
    from apps.leagues_manager.tests.mock_data_leagues import MockTorneo, MockDetalleFuenteExtraccion

# ===================================================================
#  1. DEFINICIÓN DE LA ARQUITECTURA DE ROBOTS (HERENCIA Y POLIMORFISMO)
# ===================================================================

class BaseRobot(ABC):
    """
    Clase Base Abstracta para todos los robots de extracción.
    Define el contrato que todos los robots deben seguir.
    """
    def __init__(self, torneo: 'MockTorneo', detalle: 'MockDetalleFuenteExtraccion'):
        self.torneo = torneo
        self.detalle = detalle
        self.fuente = detalle.fuente
        self.robot_id = f"Robot-{self.fuente.type.upper()}"
        self.job_context = f"'{self.torneo.name}' | Fuente: '{self.fuente.name}'"

    @abstractmethod
    async def _execute_scraping(self):
        """
        Método abstracto. Cada robot hijo DEBE implementar su propia lógica de scraping aquí.
        """
        pass

    async def run(self):
        """
        Método principal (Template Method). Maneja el ciclo de vida y logging común.
        """
        logger.info(f"▶️  [{self.robot_id}] Iniciando para {self.job_context}")
        logger.debug(f"   URL: {self.detalle.url}")
        try:
            await self._execute_scraping()
            logger.success(f"✅ [{self.robot_id}] Completado para {self.job_context}")
        except Exception as e:
            logger.exception(f"❌ [{self.robot_id}] Falló para {self.job_context}: {e}")