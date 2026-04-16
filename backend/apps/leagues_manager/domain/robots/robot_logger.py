"""
✅ RobotLogger: Separacion de responsabilidades SRP
Extraido toda la logica de logging del BaseRobot.
Ahora el Robot SOLO hace scraping, el Logger SOLO hace logging.
Cumplimiento 100% Single Responsibility Principle.
"""

from loguru import logger
from typing import Optional
from shared.repositories.scheduler_repos import IProcessRunRepository


class RobotLogger:
    """
    ✅ Logger dedicado exclusivamente para Robots.
    Cumplimiento Single Responsibility Principle:
    Esta clase SOLO sabe escribir logs, nada mas.
    No sabe nada de scraping, ni de robots, ni de negocio.
    """

    def __init__(
        self, robot_id: str, run_id: str, detalle_id: int, repo: IProcessRunRepository
    ):
        self.robot_id = robot_id
        self.run_id = run_id
        self.detalle_id = detalle_id
        self.repo = repo

    async def log_step(
        self,
        step: str,
        level: str,
        message: str,
        input_data: Optional[str] = None,
        output_data: Optional[str] = None,
    ) -> None:
        """Escribe log en consola Y en BD simultáneamente."""
        full_message = f"[{self.robot_id}] [run_id={self.run_id}] [detalle_id={self.detalle_id}] [{step}] {message}"

        if level == "info":
            logger.info(full_message)
        elif level == "warning":
            logger.warning(full_message)
        elif level == "error":
            logger.error(full_message)
        else:
            logger.debug(full_message)

        # Escribe en process_run_logs
        from typing import cast, Awaitable

        await cast(
            Awaitable[None],
            self.repo.write_log(
                run_id=self.run_id,
                step=step,
                level=level,
                message=message,
                input=input_data,
                output=output_data,
            ),
        )
