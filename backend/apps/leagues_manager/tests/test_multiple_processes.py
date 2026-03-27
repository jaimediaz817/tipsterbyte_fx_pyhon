"""
Test de Integración: Verificación de Múltiples Procesos Simultáneos

Este test verifica que cuando hay múltiples procesos configurados,
cada uno ejecuta solo sus trabajos asignados correctamente.
"""

import pytest
import uuid
from loguru import logger

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
from core.db.sql.database_sql import SessionLocal
from shared.constants.process.process_codes import (
    PROCESS_EXTRACT_DATA_FUENTES,
    PROCESS_STANDINGS_EXTRACTION,
    PROCESS_ODDS_WPLAY_EXTRACTION,
    PROCESS_CALENDAR_EXTRACTION,
)


@pytest.fixture(scope="function")
def db_session():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def multiple_processes_data(db_session):
    """Crea datos de prueba con múltiples procesos configurados."""
    suffix = uuid.uuid4().hex[:12]

    # Cleanup previo
    try:
        db_session.query(DetalleFuenteExtraccion).delete(synchronize_session=False)
        db_session.commit()
    except Exception:
        db_session.rollback()

    try:
        db_session.query(FuenteExtraccion).filter(
            FuenteExtraccion.name.like("Standings_%")
            | FuenteExtraccion.name.like("Odds_%")
            | FuenteExtraccion.name.like("Calendar_%")
        ).delete(synchronize_session=False)
        db_session.commit()
    except Exception:
        db_session.rollback()

    try:
        db_session.query(Torneo).filter(Torneo.nombre.like("Season_%")).delete(
            synchronize_session=False
        )
        db_session.commit()
    except Exception:
        db_session.rollback()

    try:
        db_session.query(Liga).filter(Liga.nombre.like("LaLiga_%")).delete(
            synchronize_session=False
        )
        db_session.commit()
    except Exception:
        db_session.rollback()

    try:
        db_session.query(Pais).filter(Pais.nombre.like("Spain_%")).delete(
            synchronize_session=False
        )
        db_session.commit()
    except Exception:
        db_session.rollback()

    try:
        db_session.query(Continente).filter(Continente.nombre.like("EU_%")).delete(
            synchronize_session=False
        )
        db_session.commit()
    except Exception:
        db_session.rollback()

    # Crear procesos
    processes = {}
    for process_code, process_name in [
        (PROCESS_EXTRACT_DATA_FUENTES, "Orchestrator General"),
        (PROCESS_STANDINGS_EXTRACTION, "Standings Only"),
        (PROCESS_ODDS_WPLAY_EXTRACTION, "Odds Only"),
        (PROCESS_CALENDAR_EXTRACTION, "Calendar Only"),
    ]:
        process = db_session.query(Process).filter(Process.code == process_code).first()
        if not process:
            process = Process(code=process_code, name=process_name, is_active=True)
            db_session.add(process)
            db_session.flush()
        processes[process_code] = process

    # Crear estructura geográfica
    continente = Continente(nombre=f"EU_{suffix[:4]}", codigo=f"EU{suffix[:4]}")
    db_session.add(continente)
    db_session.flush()

    pais = Pais(
        nombre=f"Spain_{suffix[:4]}",
        codigo_iso=f"E{suffix[:2]}",
        continente_id=continente.id,
    )
    db_session.add(pais)
    db_session.flush()

    liga = Liga(nombre=f"LaLiga_{suffix}", pais_id=pais.id)
    db_session.add(liga)
    db_session.flush()

    torneo = Torneo(nombre=f"Season_{suffix}", is_active=True, liga_id=liga.id)
    db_session.add(torneo)
    db_session.flush()

    # Crear fuentes
    fuentes = [
        FuenteExtraccion(
            name=f"Standings_{suffix}", type=RobotTypeEnum.STANDINGS, is_active=True
        ),
        FuenteExtraccion(
            name=f"Odds_{suffix}", type=RobotTypeEnum.ODDS_WPLAY, is_active=True
        ),
        FuenteExtraccion(
            name=f"Calendar_{suffix}", type=RobotTypeEnum.CALENDAR, is_active=True
        ),
    ]
    for f in fuentes:
        db_session.add(f)
    db_session.flush()

    # Crear detalles con process_id específico para cada proceso
    detalles = [
        DetalleFuenteExtraccion(
            torneo_id=torneo.id,
            fuente_id=fuentes[0].id,
            url="https://test.com/s",
            is_active=True,
            process_id=processes[PROCESS_STANDINGS_EXTRACTION].id,
        ),
        DetalleFuenteExtraccion(
            torneo_id=torneo.id,
            fuente_id=fuentes[1].id,
            url="https://test.com/o",
            is_active=True,
            process_id=processes[PROCESS_ODDS_WPLAY_EXTRACTION].id,
        ),
        DetalleFuenteExtraccion(
            torneo_id=torneo.id,
            fuente_id=fuentes[2].id,
            url="https://test.com/c",
            is_active=True,
            process_id=processes[PROCESS_CALENDAR_EXTRACTION].id,
        ),
    ]
    for d in detalles:
        db_session.add(d)
    db_session.flush()
    db_session.commit()

    yield {
        "processes": processes,
        "detalles": detalles,
        "torneo": torneo,
        "liga": liga,
        "pais": pais,
        "continente": continente,
        "fuentes": fuentes,
        "suffix": suffix,
    }

    # Cleanup
    try:
        for detalle in detalles:
            db_session.delete(detalle)
        for fuente in fuentes:
            db_session.delete(fuente)
        db_session.delete(torneo)
        db_session.delete(liga)
        db_session.delete(pais)
        db_session.delete(continente)
        db_session.commit()
    except Exception:
        db_session.rollback()


def test_multiple_processes_filter_correctly(db_session, multiple_processes_data):
    """Verifica que múltiples procesos filcan correctamente sus trabajos."""
    from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
        _build_jobs_from_leagues,
    )
    from apps.leagues_manager.infrastructure.repositories.sql_platform_repository import (
        SqlPlatformRepository,
    )

    leagues = SqlPlatformRepository(db_session).get_all_leagues_with_full_details()

    # Verificar que cada proceso filtra solo sus trabajos
    for process_code, process in multiple_processes_data["processes"].items():
        # El orquestador general necesita is_general_orchestrator=True
        is_orchestrator = process_code == PROCESS_EXTRACT_DATA_FUENTES
        flat_jobs, _ = _build_jobs_from_leagues(
            leagues,
            target_process_id=process.id,
            is_general_orchestrator=is_orchestrator,
        )

        if is_orchestrator:
            # El orquestador general debería ejecutar todos los trabajos
            assert len(flat_jobs) == 3, (
                f"Orquestador general debería ejecutar 3 trabajos, "
                f"ejecutó {len(flat_jobs)}"
            )
        else:
            # Cada proceso específico debería ejecutar solo 1 trabajo
            assert len(flat_jobs) == 1, (
                f"Proceso {process_code} debería ejecutar 1 trabajo, "
                f"ejecutó {len(flat_jobs)}"
            )

            # Verificar que el tipo de fuente corresponde al proceso
            fuente_type = flat_jobs[0][1].fuente.type
            if process_code == PROCESS_STANDINGS_EXTRACTION:
                assert fuente_type == RobotTypeEnum.STANDINGS
            elif process_code == PROCESS_ODDS_WPLAY_EXTRACTION:
                assert fuente_type == RobotTypeEnum.ODDS_WPLAY
            elif process_code == PROCESS_CALENDAR_EXTRACTION:
                assert fuente_type == RobotTypeEnum.CALENDAR

    logger.success("✅ Múltiples procesos filtran correctamente sus trabajos")


def test_all_processes_count_matches(db_session, multiple_processes_data):
    """Verifica que la suma de trabajos de procesos específicos equals al orquestador."""
    from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
        _build_jobs_from_leagues,
    )
    from apps.leagues_manager.infrastructure.repositories.sql_platform_repository import (
        SqlPlatformRepository,
    )

    leagues = SqlPlatformRepository(db_session).get_all_leagues_with_full_details()

    # Obtener trabajos del orquestador general
    orchestrator = multiple_processes_data["processes"][PROCESS_EXTRACT_DATA_FUENTES]
    orchestrator_jobs, _ = _build_jobs_from_leagues(
        leagues,
        target_process_id=orchestrator.id,
        is_general_orchestrator=True,
    )

    # Obtener trabajos de cada proceso específico
    specific_jobs_count = 0
    for process_code, process in multiple_processes_data["processes"].items():
        if process_code != PROCESS_EXTRACT_DATA_FUENTES:
            flat_jobs, _ = _build_jobs_from_leagues(
                leagues,
                target_process_id=process.id,
                is_general_orchestrator=False,
            )
            specific_jobs_count += len(flat_jobs)

    # La suma de trabajos específicos debería ser igual al orquestador
    assert specific_jobs_count == len(orchestrator_jobs), (
        f"Suma de trabajos específicos ({specific_jobs_count}) "
        f"debería ser igual al orquestador ({len(orchestrator_jobs)})"
    )

    logger.success(
        "✅ Conteo de trabajos de procesos específicos coincide con orquestador"
    )
