import asyncio
from dataclasses import dataclass
from loguru import logger

from bodega_src.tasks.runner_leagues_manager import run_process_client_leagues_manager
from core.config import settings
from core.db.sql.database_sql import SessionLocal
from shared.constants.process.process_codes import (
    PROCESS_EXTRACCION_DATA_FUENTES_DEPORTIVAS,
)


# NOTE: esto es temporal, luego se moverá hacia: tests
@dataclass
class MockClient:
    id: int
    name: str


class MockClientRepository:
    def __init__(self, session):
        pass

    def get_all_active_for_process(self, process_id):
        return [
            MockClient(id=1, name="Premier League 123"),
            MockClient(id=2, name="Cliente Beta"),
            MockClient(id=3, name="Cliente Gamma"),
        ]


@dataclass
class MockProcess:
    id: int
    code: str


class MockProcessRepository:
    def __init__(self, session):
        pass

    def get_active_by_code(self, code):
        """_summary_

        Args:
            code (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Devuelve un proceso simulado si el código coincide
        if code == PROCESS_EXTRACCION_DATA_FUENTES_DEPORTIVAS:
            return MockProcess(id=1, code=code)
        return None


async def launch_process_rastreo_data_fuentes_deportivas_task():
    """_summary_
    Lanza la tarea de rastreo de datos desde fuentes deportivas para todos los clientes activos.
    Utiliza concurrencia limitada para procesar múltiples clientes al mismo tiempo.
    Args:
        None
    Returns:
        None
    Raises:
        None
    """
    logger.info("🚀 Iniciando tarea de rastreo de datos desde fuentes deportivas.")
    # Aquí se implementaría la lógica para rastrear datos desde las fuentes deportivas.
    # Por ejemplo, podrías llamar a funciones que interactúan con APIs o bases de datos.
    # ...
    logger.info("✅ Tarea de rastreo de datos desde fuentes deportivas completada.")
    logger.info(
        "🚀 Iniciando tarea de cruce cartera Sura para todos los clientes activos."
    )

    # 🔒 Limitar a N procesos concurrentes reales
    semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_CLIENTS)

    with SessionLocal() as session:
        # TODO: Refactor
        # process_repo = ProcessRepository(session)
        process_repo = MockProcessRepository(session)
        process = process_repo.get_active_by_code(
            PROCESS_EXTRACCION_DATA_FUENTES_DEPORTIVAS
        )

        if not process:
            logger.warning(
                f"⚠️ Proceso '{PROCESS_EXTRACCION_DATA_FUENTES_DEPORTIVAS}' no está registrado en BD o no se encuentra activo."
            )
            return

        # TODO: Refactor
        # client_repo = ClientRepository(session)
        client_repo = MockClientRepository(session)

        clients = client_repo.get_all_active_for_process(process.id)

        if not clients:
            logger.warning("⚠️ No hay clientes activos para ejecutar.")
            return

    async def run_for_client(client):
        """Ejecuta el proceso de cruce de cartera para un cliente específico.

        Args:
            client (MockClient): El cliente para el cual se ejecutará el proceso.
        """
        client_info = f"{client.name} (ID: {client.id})"

        if semaphore.locked():
            logger.info(
                f"⏳ Cliente en espera: {client_info} (esperando cupo disponible...)"
            )

        async with semaphore:
            try:
                logger.info(f"▶️ Procesando cliente: {client_info}")
                # NOTE - Ejecuta el proceso de extracción de datos para el cliente en un hilo separado
                await asyncio.to_thread(run_process_client_leagues_manager, client)
                logger.success(f"✅ Cliente procesado exitosamente: {client_info}")
            except Exception as e:
                logger.exception(f"❌ Error en cliente {client_info}: {e}")

    await asyncio.gather(*(run_for_client(client) for client in clients))

    logger.info("🏁 Proceso de cruce cartera Sura completado para todos los clientes.")
