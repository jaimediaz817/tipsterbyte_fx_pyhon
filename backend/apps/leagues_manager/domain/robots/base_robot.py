import asyncio
from abc import ABC, abstractmethod
from loguru import logger
from typing import TYPE_CHECKING, Dict, Type

from shared.repositories.scheduler_repos.process_run_repository import (
    ProcessRunRepository,
)

if TYPE_CHECKING:
    from apps.leagues_manager.tests.mock_data_leagues import (
        MockTorneo,
        MockDetalleFuenteExtraccion,
    )

# ===================================================================
#  1. DEFINICIÓN DE LA ARQUITECTURA DE ROBOTS (HERENCIA Y POLIMORFISMO)
# ===================================================================


class BaseRobot(ABC):
    """
    Clase Base Abstracta para todos los robots de extracción.
    Define el contrato que todos los robots deben seguir.
    Cada robot específico (ej: StandingsRobot, OddsWPlayRobot) hereda de esta clase
    y implementa el método _execute_scraping() con su lógica particular.
    """

    def __init__(
        self,
        torneo: "MockTorneo",
        detalle: "MockDetalleFuenteExtraccion",
        run_id: str,
        repo: "ProcessRunRepository",  # <-- NUEVO
    ):
        self.torneo = torneo
        self.detalle = detalle
        self.fuente = detalle.fuente
        self.run_id = run_id
        self.repo = repo  # <-- NUEVO
        fuente_type = (
            self.fuente.type.upper()
            if self.fuente and hasattr(self.fuente, "type") and self.fuente.type
            else "UNKNOWN"
        )
        self.robot_id = f"Robot-{fuente_type}"
        fuente_name = (
            self.fuente.name
            if self.fuente and hasattr(self.fuente, "name")
            else "UNKNOWN"
        )
        self.job_context = f"'{self.torneo.nombre}' | Fuente: '{fuente_name}'"

    def _log_step(
        self,
        step: str,
        level: str,
        message: str,
        input_data: str | None = None,
        output_data: str | None = None,
    ):
        """Escribe log en consola Y en BD simultáneamente."""
        full_message = f"[{self.robot_id}] [run_id={self.run_id}] [detalle_id={self.detalle.id}] [{step}] {message}"

        if level == "info":
            logger.info(full_message)
        elif level == "warning":
            logger.warning(full_message)
        elif level == "error":
            logger.error(full_message)
        else:
            logger.debug(full_message)

        # Escribe en process_run_logs
        self.repo.write_log(
            run_id=self.run_id,
            step=step,
            level=level,
            message=message,
            detalle_fuente_extraccion_id=self.detalle.id,
            input=input_data,
            output=output_data,
        )

    @abstractmethod
    async def _execute_scraping(self):
        pass

    async def run(self):
        self._log_step("START", "info", f"Iniciando para {self.job_context}")
        logger.debug(f"   [run_id={self.run_id}] URL: {self.detalle.url}")
        try:
            await self._execute_scraping()
            self._log_step(
                "END", "info", f"Completado exitosamente para {self.job_context}"
            )
        except Exception as e:
            self._log_step("ERROR", "error", f"Falló para {self.job_context}: {e}")
            raise
