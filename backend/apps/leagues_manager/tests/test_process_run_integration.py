# ...existing imports (asegúrate de que todos están bien y que el sys.path se configura correctamente)
import pytest
import uuid
from datetime import datetime
import sys
import os

# --- INICIO: Configuración para asegurar que pytest encuentre los módulos ---
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)
# --- FIN: Configuración para asegurar que pytest encuentre los módulos ---

from apps.leagues_manager.infrastructure.models.sql.continente import Continente
from apps.leagues_manager.infrastructure.models.sql.pais import Pais
from apps.leagues_manager.infrastructure.models.sql.liga import Liga
from apps.leagues_manager.infrastructure.models.sql.torneo import Torneo
from apps.leagues_manager.infrastructure.models.sql.fuente_extraccion import (
    FuenteExtraccion,
)
from apps.leagues_manager.infrastructure.models.sql.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion,
)
from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum
from apps.platform_config.infrastructure.models.sql.process import Process
from apps.platform_config.infrastructure.models.sql.process_run import ProcessRun
from apps.platform_config.infrastructure.models.sql.process_run_log import ProcessRunLog
from core.db.sql.database_sql import SessionLocal
from shared.repositories.scheduler_repos.process_run_repository import (
    ProcessRunRepository,
)
from shared.constants.process.process_codes import PROCESS_CUOTAS_WPLAY


@pytest.fixture(scope="function")
def db_session():
    """
    Crea una sesión de BD para un test.
    La limpieza de datos se realiza mediante el fixture cleanup_process_runs
    del conftest.py, que elimina los registros creados durante el test.

    NOTA: No iniciamos transacciones explícitas aquí porque el repositorio
    ProcessRunRepository hace commits internos. Usamos la sesión directamente
    y confiamos en el fixture cleanup_process_runs para la limpieza.
    """
    session = SessionLocal()
    yield session  # Pasa la sesión al test
    # No cerramos la sesión explícitamente para evitar errores de transacción
    # El pool de conexiones se encargará de cerrarla automáticamente


@pytest.fixture(scope="function")
def real_repo(db_session):
    return ProcessRunRepository(db=db_session)


@pytest.fixture(scope="function")
def run_id():
    return f"runid_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}"


@pytest.mark.asyncio
async def test_integration_create_run_y_write_logs(db_session, real_repo, run_id):
    """
    🔗 Test de integración REAL con datos controlados.
    Los datos se crean y se eliminan con rollback al finalizar el test.
    """
    test_suffix = str(uuid.uuid4())[:8]

    unique_continente_name = f"Europa_{test_suffix}"
    unique_continente_code = f"EU_{str(uuid.uuid4())[:7].upper()}"
    continente = Continente(
        nombre=unique_continente_name, codigo=unique_continente_code
    )
    db_session.add(continente)
    db_session.flush()

    unique_pais_codigo_iso = str(uuid.uuid4())[:3].upper()
    unique_pais_name = f"Spain_{test_suffix}"
    pais = Pais(
        nombre=unique_pais_name,
        codigo_iso=unique_pais_codigo_iso,
        continente_id=continente.id,
    )
    db_session.add(pais)
    db_session.flush()

    unique_liga_name = f"LaLiga_{test_suffix}"
    liga = Liga(nombre=unique_liga_name, pais_id=pais.id)
    db_session.add(liga)
    db_session.flush()

    unique_torneo_name = f"LaLiga 2025-2026_{test_suffix}"
    torneo = Torneo(nombre=unique_torneo_name, is_active=True, liga_id=liga.id)
    db_session.add(torneo)
    db_session.flush()

    unique_fuente_name = f"Standings (SofaScore)_{test_suffix}"
    fuente = FuenteExtraccion(
        name=unique_fuente_name,
        type=RobotTypeEnum.STANDINGS,
        is_active=True,
    )
    db_session.add(fuente)
    db_session.flush()

    unique_url = f"https://sofascore.com/laliga/{test_suffix}"
    detalle = DetalleFuenteExtraccion(
        torneo_id=torneo.id,
        fuente_id=fuente.id,
        url=unique_url,
        is_active=True,
    )
    db_session.add(detalle)
    db_session.flush()

    unique_process_code = f"{PROCESS_CUOTAS_WPLAY}_{test_suffix}"
    process_entity = Process(
        code=unique_process_code,
        name="Extracción Cuotas WPlay Test",
        is_active=True,
        description="Test process description",
    )
    db_session.add(process_entity)
    db_session.flush()

    # --- SIMULACIÓN DE LA LÓGICA DEL REPOSITORIO DE ProcessRun ---
    # Paso 1: Crear el ProcessRun con los argumentos mínimos esperados por real_repo.create_run
    real_repo.create_run(
        run_id=run_id,
        process_code=process_entity.code,
    )

    # Paso 2: Obtener la instancia de ProcessRun recién creada para actualizarla
    db_run_instance = (
        db_session.query(ProcessRun).filter(ProcessRun.run_id == run_id).first()
    )
    assert (
        db_run_instance is not None
    ), "ProcessRun no fue creado por real_repo.create_run"

    # Paso 3: Actualizar los detalles iniciales directamente en la instancia
    started_at = datetime.now()
    task_id = f"celery_task_{uuid.uuid4()}"

    db_run_instance.task_id = task_id
    db_run_instance.started_at = started_at
    db_run_instance.status = "running"
    db_run_instance.message = "Proceso de test iniciado"
    db_session.flush()  # Persistir los cambios iniciales

    real_repo.write_log(
        run_id=run_id,
        step="START",
        message="Inicio del test de integración.",
        level="INFO",  # <-- ¡CORREGIDO! Añadir el nivel del log
    )
    real_repo.write_log(
        run_id=run_id,
        step="STEP_1",
        message="Ejecutando paso 1.",
        level="INFO",  # <-- ¡CORREGIDO! Añadir el nivel del log
    )
    real_repo.write_log(
        run_id=run_id,
        step="STEP_2",
        message="Ejecutando paso 2.",
        level="INFO",  # <-- ¡CORREGIDO! Añadir el nivel del log
    )
    real_repo.write_log(
        run_id=run_id,
        step="END",
        message="Fin del test de integración.",
        level="INFO",  # <-- ¡CORREGIDO! Añadir el nivel del log
    )

    # Paso 4: Actualizar los detalles finales directamente en la instancia
    ended_at = datetime.now()
    db_run_instance.ended_at = ended_at
    db_run_instance.status = "success"
    db_run_instance.message = "Proceso de test finalizado con éxito"
    db_session.flush()  # Persistir los cambios finales

    # --- Aserciones en BD ---
    # Volvemos a consultar para asegurarnos de que los cambios se reflejaron correctamente
    final_db_run = (
        real_repo.db.query(ProcessRun).filter(ProcessRun.run_id == run_id).first()
    )
    assert final_db_run is not None
    assert final_db_run.process_id is not None
    assert (
        real_repo.db.query(Process)
        .filter(Process.code == process_entity.code)
        .first()
        .id
        == final_db_run.process_id
    )
    assert final_db_run.status == "success"
    assert final_db_run.ended_at is not None
    assert final_db_run.task_id == task_id
    assert final_db_run.started_at.isoformat(
        timespec="seconds"
    ) == started_at.isoformat(timespec="seconds")

    db_logs = (
        real_repo.db.query(ProcessRunLog)
        .filter(ProcessRunLog.run_id == run_id)
        .order_by(ProcessRunLog.timestamp)
        .all()
    )
    assert len(db_logs) == 4
    assert db_logs[0].step == "START"
    assert db_logs[1].step == "STEP_1"
    assert db_logs[2].step == "STEP_2"
    assert db_logs[3].step == "END"
    assert "Inicio del test de integración." in db_logs[0].message
    assert "Fin del test de integración." in db_logs[3].message
