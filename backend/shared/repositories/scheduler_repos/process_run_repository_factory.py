"""
Factory para obtener la implementación correcta de IProcessRunRepository.
Permite cambiar entre implementación real y NoOp según configuración.
"""

from sqlalchemy.orm import Session
from loguru import logger
from core.config import settings
from shared.repositories.scheduler_repos.i_process_run_repository import (
    IProcessRunRepository,
)
from shared.repositories.scheduler_repos.process_run_repository import (
    ProcessRunRepository,
)
from shared.repositories.scheduler_repos.noop_process_run_repository import (
    NoOpProcessRunRepository,
)


class ProcessRunRepositoryFactory:
    """
    Factory que proporciona la implementación correcta de IProcessRunRepository
    según la configuración del entorno.
    """

    @staticmethod
    def get_repository(
        db: Session | None = None,
        use_real_db: bool | None = None,
    ) -> IProcessRunRepository:
        """
        Retorna la implementación apropiada del repositorio.

        Args:
            db: Sesión de SQLAlchemy (requerida si use_real_db=True).
            use_real_db: Si True, retorna ProcessRunRepository (escribe en BD).
                         Si False, retorna NoOpProcessRunRepository (no escribe).
                         Si None, lee de variable de entorno PROCESS_RUN_LOGGING_ENABLED.

        Returns:
            Implementación de IProcessRunRepository.
        """
        if use_real_db is None:
            # Leer de configuración centralizada (default: True para producción)
            use_real_db = settings.PROCESS_RUN_LOGGING_ENABLED

        if use_real_db:
            if db is None:
                raise ValueError(
                    "db session is required when use_real_db=True. "
                    "Pass a SQLAlchemy Session or set PROCESS_RUN_LOGGING_ENABLED=false"
                )
            logger.info("📊 Usando ProcessRunRepository (ESCRIBE en BD)")
            return ProcessRunRepository(db=db)

        logger.info("🔇 Usando NoOpProcessRunRepository (NO escribe en BD)")
        return NoOpProcessRunRepository()
