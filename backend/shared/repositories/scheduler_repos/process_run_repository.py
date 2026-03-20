from datetime import datetime
from sqlalchemy.orm import Session
from apps.platform_config.infrastructure.models.sql.process import Process
from apps.platform_config.infrastructure.models.sql.process_run import ProcessRun
from apps.platform_config.infrastructure.models.sql.process_run_log import ProcessRunLog
from loguru import logger


class ProcessRunRepository:
    """
    Repositorio para gestionar el ciclo de vida de una ejecución (ProcessRun)
    y sus logs detallados por paso (ProcessRunLog).
    """

    def __init__(self, db: Session):
        self.db = db

    def create_run(self, run_id: str, process_code: str) -> ProcessRun | None:
        """
        Crea un registro ProcessRun al inicio de una ejecución del scheduler.
        Busca el proceso por su código y lo vincula al run.

        Args:
            run_id:       ID único generado por generate_run_id().
            process_code: Código del proceso (ej: SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS).

        Returns:
            ProcessRun creado, o None si el proceso no existe en la BD.
        """
        process = self.db.query(Process).filter(Process.code == process_code).first()
        if not process:
            logger.error(f"❌ No se encontró el proceso con código '{process_code}'. No se puede crear el ProcessRun.")
            return None

        run = ProcessRun(
            run_id=run_id,
            process_id=process.id,
            status="in_progress",
        )
        self.db.add(run)
        self.db.commit()
        logger.info(f"📋 ProcessRun creado: run_id={run_id} | proceso='{process_code}'")
        return run

    def complete_run(self, run_id: str) -> None:
        """
        Marca un ProcessRun como completado exitosamente.
        Registra la fecha/hora de finalización.
        """
        self.db.query(ProcessRun).filter(ProcessRun.run_id == run_id).update({
            "status": "success",
            "ended_at": datetime.now(),
        })
        self.db.commit()
        logger.success(f"✅ ProcessRun completado: run_id={run_id}")

    def fail_run(self, run_id: str) -> None:
        """
        Marca un ProcessRun como fallido.
        Registra la fecha/hora de finalización.
        """
        self.db.query(ProcessRun).filter(ProcessRun.run_id == run_id).update({
            "status": "failed",
            "ended_at": datetime.now(),
        })
        self.db.commit()
        logger.error(f"❌ ProcessRun marcado como fallido: run_id={run_id}")

    def write_log(
        self,
        run_id: str,
        step: str,
        level: str,
        message: str,
        detalle_fuente_extraccion_id: int | None = None,
        input: str | None = None,
        output: str | None = None,
    ) -> None:
        """
        Escribe un registro de log detallado para un paso concreto dentro de un hilo.

        Args:
            run_id:                       ID de la ejecución padre (FK → process_runs).
            step:                         Paso del hilo (usar constantes de process_run_steps.py).
            level:                        Nivel del log: 'info', 'warning', 'error', 'debug'.
            message:                      Descripción legible de lo ocurrido en el paso.
            detalle_fuente_extraccion_id: ID del detalle de fuente que procesó este hilo (nullable).
            input:                        Datos de entrada del paso en formato texto/JSON (opcional).
            output:                       Resultado del paso en formato texto/JSON (opcional).
        """
        log = ProcessRunLog(
            run_id=run_id,
            detalle_fuente_extraccion_id=detalle_fuente_extraccion_id,
            step=step,
            level=level,
            message=message,
            input=input,
            output=output,
        )
        self.db.add(log)
        self.db.commit()
