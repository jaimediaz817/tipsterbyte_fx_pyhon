import asyncio
from abc import ABC, abstractmethod
from loguru import logger
from typing import TYPE_CHECKING, Dict, Type

from shared.repositories.scheduler_repos import IProcessRunRepository

# --- EXCEPCIONES PERSONALIZADAS ---
from core.exceptions import ScrapingException

# --- LOGGING MEJORADO ---
from core.robot_logging import (
    log_robot_start,
    log_robot_end,
    log_step,
    get_robot_emoji,
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
        repo: "IProcessRunRepository",  # <-- NUEVO
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
            input=input_data,
            output=output_data,
        )

    @abstractmethod
    async def _execute_scraping(self):
        pass

    async def run(self):
        """Ejecuta el robot con logging mejorado y trazabilidad completa."""
        # Obtener tipo de robot para emoji
        robot_type = "UNKNOWN"
        if self.fuente and hasattr(self.fuente, "type") and self.fuente.type:
            # Usar getattr para acceder de forma segura al atributo value
            robot_type = getattr(self.fuente.type, "value", str(self.fuente.type))

        fuente_name = (
            self.fuente.name
            if self.fuente and hasattr(self.fuente, "name")
            else "UNKNOWN"
        )

        # Log de inicio mejorado
        log_robot_start(
            run_id=self.run_id,
            robot_type=robot_type,
            robot_class_name=self.__class__.__name__,
            torneo_nombre=self.torneo.nombre,
            fuente_name=fuente_name,
            detalle_id=self.detalle.id,
            url=self.detalle.url,
        )

        # También escribir en BD
        self.repo.write_log(
            run_id=self.run_id,
            step="START",
            level="info",
            message=f"Iniciando robot {self.__class__.__name__} para {self.job_context}",
            input=f"url={self.detalle.url}",
        )

        try:
            await self._execute_scraping()

            # Log de éxito mejorado
            log_robot_end(
                run_id=self.run_id,
                robot_type=robot_type,
                robot_class_name=self.__class__.__name__,
                torneo_nombre=self.torneo.nombre,
                success=True,
            )

            # También escribir en BD
            self.repo.write_log(
                run_id=self.run_id,
                step="END",
                level="info",
                message=f"Robot {self.__class__.__name__} completado exitosamente para {self.job_context}",
            )

        except ScrapingException:
            # Si ya es una ScrapingException, solo re-lanzar
            raise
        except Exception as e:
            # Log de error mejorado
            log_robot_end(
                run_id=self.run_id,
                robot_type=robot_type,
                robot_class_name=self.__class__.__name__,
                torneo_nombre=self.torneo.nombre,
                success=False,
                error=e,
            )

            # También escribir en BD
            self.repo.write_log(
                run_id=self.run_id,
                step="ERROR",
                level="error",
                message=f"Robot {self.__class__.__name__} falló para {self.job_context}: {e}",
            )

            # Envolver otras excepciones en ScrapingException
            raise ScrapingException(
                robot_id=self.robot_id,
                url=self.detalle.url,
                original_error=e,
            )
