"""
Implementación No-Operation del repositorio de ProcessRun.
No escribe en base de datos - útil para tests unitarios.
"""

from typing import Optional
from loguru import logger
from apps.platform_config.infrastructure.models.sql.process_run import ProcessRun
from shared.repositories.scheduler_repos.i_process_run_repository import (
    IProcessRunRepository,
)


class NoOpProcessRunRepository(IProcessRunRepository):
    """
    Implementación que NO escribe en base de datos.
    Útil para tests unitarios donde no se necesita persistir logs.
    """

    def __init__(self):
        self._runs_created: list[str] = []
        self._runs_completed: list[str] = []
        self._runs_failed: list[str] = []
        self._logs_written: list[dict] = []

    def create_run(self, run_id: str, process_code: str) -> Optional[ProcessRun]:
        """
        Retorna un mock object sin escribir en BD.
        """
        self._runs_created.append(run_id)
        logger.debug(
            f"[NoOp] ProcessRun simulado: run_id={run_id} | proceso='{process_code}'"
        )
        # Retornamos un objeto simulado con los atributos mínimos necesarios
        mock_run = type(
            "MockProcessRun",
            (),
            {
                "run_id": run_id,
                "status": "in_progress",
            },
        )()
        return mock_run  # type: ignore

    def complete_run(self, run_id: str) -> None:
        """
        No-op: solo registra en memoria.
        """
        self._runs_completed.append(run_id)
        logger.debug(f"[NoOp] ProcessRun completado (simulado): run_id={run_id}")

    def fail_run(self, run_id: str) -> None:
        """
        No-op: solo registra en memoria.
        """
        self._runs_failed.append(run_id)
        logger.debug(f"[NoOp] ProcessRun fallido (simulado): run_id={run_id}")

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
        No-op: solo almacena en memoria para verificación en tests.
        """
        self._logs_written.append(
            {
                "run_id": run_id,
                "step": step,
                "level": level,
                "message": message,
                "input": input,
                "output": output,
            }
        )
        logger.debug(
            f"[NoOp] Log simulado: run_id={run_id} | step={step} | level={level}"
        )

    # --- Métodos auxiliares para verificación en tests ---
    def get_runs_created(self) -> list[str]:
        return self._runs_created.copy()

    def get_runs_completed(self) -> list[str]:
        return self._runs_completed.copy()

    def get_runs_failed(self) -> list[str]:
        return self._runs_failed.copy()

    def get_logs_written(self) -> list[dict]:
        return self._logs_written.copy()
