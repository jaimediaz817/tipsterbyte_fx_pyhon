import asyncio
from abc import ABC, abstractmethod
from loguru import logger
from typing import TYPE_CHECKING, Dict, Type, cast

from shared.repositories.scheduler_repos import IProcessRunRepository

# --- EXCEPCIONES PERSONALIZADAS ---
from core.exceptions import ScrapingException

# --- LOGGING MEJORADO ---
from core.robot_logging import (
    log_robot_start,
    log_robot_end,
    get_robot_emoji,
)
from apps.leagues_manager.domain.robots.robot_logger import RobotLogger

if TYPE_CHECKING:
    # ✅ USAMOS ENTIDADES DE DOMINIO REALES, NO MOCKS DE TEST
    from apps.leagues_manager.domain.entities.torneo import Torneo
    from apps.leagues_manager.domain.entities.detalle_fuente_extraccion import (
        DetalleFuenteExtraccion,
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
        torneo: "Torneo",
        detalle: "DetalleFuenteExtraccion",
        run_id: str,
        repo: "IProcessRunRepository",
        robot_logger: "RobotLogger | None" = None,
    ):
        self.torneo = torneo
        self.detalle = detalle
        # ✅ Correccion: Atributo 'fuente' no existe en DetalleFuenteExtraccion
        # Se obtiene de forma segura con getattr (compatibilidad runtime)
        self.fuente = getattr(detalle, "fuente", None)
        self.run_id = run_id
        self.repo = repo  # <-- NUEVO

        # ✅ SISTEMA DE ADAPTADORES DE FUENTE DE EXTRACCION
        from apps.leagues_manager.infrastructure.adapters.fuente_extraccion_adapter_factory import (
            FuenteExtraccionAdapterFactory,
        )

        self.adapter = FuenteExtraccionAdapterFactory.crear(detalle)
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

        # ✅ SRP: Logging delegado completamente a RobotLogger
        # Inyeccion opcional para permitir mockear en tests
        self._logger = robot_logger or RobotLogger(
            robot_id=self.robot_id,
            run_id=self.run_id,
            detalle_id=cast(int, self.detalle.id),
            repo=self.repo,
        )

    async def _log_step(
        self,
        step: str,
        level: str,
        message: str,
        input_data: str | None = None,
        output_data: str | None = None,
    ):
        """✅ DELEGADO: Escribe log en consola Y en BD simultáneamente.
        ⚠️ MANTENIDO 100% RETROCOMPATIBLE: Ningun robot existente se rompe.
        Logica completamente delegada a RobotLogger (SRP)
        """
        await self._logger.log_step(
            step=step,
            level=level,
            message=message,
            input_data=input_data,
            output_data=output_data,
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
            detalle_id=cast(int, self.detalle.id),
            url=self.detalle.url,
        )

        # También escribir en BD
        await self.repo.write_log(
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
            await self.repo.write_log(
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
            await self.repo.write_log(
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
