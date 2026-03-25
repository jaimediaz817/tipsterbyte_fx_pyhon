"""
Interface abstracta para el repositorio de ProcessRun.
Permite implementaciones alternativas (ej: NoOp para tests).
"""

from abc import ABC, abstractmethod
from typing import Optional
from apps.platform_config.infrastructure.models.sql.process_run import ProcessRun


class IProcessRunRepository(ABC):
    """
    Interfaz que define el contrato para gestionar el ciclo de vida
    de una ejecución (ProcessRun) y sus logs detallados (ProcessRunLog).
    """

    @abstractmethod
    def create_run(self, run_id: str, process_code: str) -> Optional[ProcessRun]:
        """
        Crea un registro ProcessRun al inicio de una ejecución del scheduler.

        Args:
            run_id:       ID único generado por generate_run_id().
            process_code: Código del proceso.

        Returns:
            ProcessRun creado, o None si el proceso no existe en la BD.
        """
        pass

    @abstractmethod
    def complete_run(self, run_id: str) -> None:
        """
        Marca un ProcessRun como completado exitosamente.
        Registra la fecha/hora de finalización.
        """
        pass

    @abstractmethod
    def fail_run(self, run_id: str) -> None:
        """
        Marca un ProcessRun como fallido.
        Registra la fecha/hora de finalización.
        """
        pass

    @abstractmethod
    def write_log(
        self,
        run_id: str,
        step: str,
        level: str,
        message: str,
        input: Optional[str] = None,
        output: Optional[str] = None,
    ) -> None:
        """
        Escribe un registro de log detallado para un paso concreto.

        Args:
            run_id:   ID de la ejecución padre (FK → process_runs).
            step:     Paso del proceso.
            level:    Nivel del log: 'info', 'warning', 'error', 'debug'.
            message:  Descripción legible de lo ocurrido.
            input:    Datos de entrada (opcional).
            output:   Resultado del paso (opcional).
        """
        pass
