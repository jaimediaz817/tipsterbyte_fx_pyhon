"""
Test de Integración: Verificación del Orquestador y Procesos Específicos

Este test crea datos de ejemplo y verifica que:
1. El orquestador ejecuta TODOS los procesos
2. Los procesos específicos ejecutan SOLO sus trabajos asignados
3. El filtrado por process_id funciona correctamente
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
    # Cleanup: rollback any uncommitted changes and close
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def test_data(db_session):
    """Crea datos de prueba con procesos específicos asignados."""
    suffix = uuid.uuid4().hex[:12]  # UUID más largo para evitar colisiones

    # Cleanup previo: eliminar TODOS los datos de tests anteriores
    # Orden inverso de dependencias para evitar FK violations
    # PRIMERO: Eliminar TODOS los detalles de fuentes (sin filtro) para evitar FK violations
    try:
        count = db_session.query(DetalleFuenteExtraccion).delete(
            synchronize_session=False
        )
        db_session.commit()
        if count > 0:
            logger.debug(f"Cleanup: eliminados {count} detalles de fuentes")
    except Exception as e:
        logger.warning(f"Cleanup error en detalle_fuente_extraccion: {e}")
        db_session.rollback()

    # SEGUNDO: Eliminar fuentes de tests anteriores
    try:
        count = (
            db_session.query(FuenteExtraccion)
            .filter(
                FuenteExtraccion.name.like("Standings_%")
                | FuenteExtraccion.name.like("Odds_%")
                | FuenteExtraccion.name.like("Calendar_%")
            )
            .delete(synchronize_session=False)
        )
        db_session.commit()
        if count > 0:
            logger.debug(f"Cleanup: eliminados {count} fuentes de extracción")
    except Exception as e:
        logger.warning(f"Cleanup error en fuente_extraccion: {e}")
        db_session.rollback()

    # TERCERO: Eliminar torneos de tests anteriores
    try:
        count = (
            db_session.query(Torneo)
            .filter(Torneo.nombre.like("Season_%"))
            .delete(synchronize_session=False)
        )
        db_session.commit()
        if count > 0:
            logger.debug(f"Cleanup: eliminados {count} torneos")
    except Exception as e:
        logger.warning(f"Cleanup error en torneo: {e}")
        db_session.rollback()

    # CUARTO: Eliminar ligas de tests anteriores
    try:
        count = (
            db_session.query(Liga)
            .filter(Liga.nombre.like("LaLiga_%"))
            .delete(synchronize_session=False)
        )
        db_session.commit()
        if count > 0:
            logger.debug(f"Cleanup: eliminadas {count} ligas")
    except Exception as e:
        logger.warning(f"Cleanup error en liga: {e}")
        db_session.rollback()

    # QUINTO: Eliminar países de tests anteriores
    try:
        count = (
            db_session.query(Pais)
            .filter(Pais.nombre.like("Spain_%"))
            .delete(synchronize_session=False)
        )
        db_session.commit()
        if count > 0:
            logger.debug(f"Cleanup: eliminados {count} países")
    except Exception as e:
        logger.warning(f"Cleanup error en pais: {e}")
        db_session.rollback()

    # SEXTO: Eliminar continentes de tests anteriores
    try:
        count = (
            db_session.query(Continente)
            .filter(Continente.nombre.like("EU_%"))
            .delete(synchronize_session=False)
        )
        db_session.commit()
        if count > 0:
            logger.debug(f"Cleanup: eliminados {count} continentes")
    except Exception as e:
        logger.warning(f"Cleanup error en continente: {e}")
        db_session.rollback()

    # Buscar procesos existentes o crearlos con códigos únicos
    orchestrator = (
        db_session.query(Process)
        .filter(Process.code == PROCESS_EXTRACT_DATA_FUENTES)
        .first()
    )
    if not orchestrator:
        orchestrator = Process(
            code=PROCESS_EXTRACT_DATA_FUENTES, name="Orchestrator", is_active=True
        )
        db_session.add(orchestrator)
        db_session.flush()

    standings = (
        db_session.query(Process)
        .filter(Process.code == PROCESS_STANDINGS_EXTRACTION)
        .first()
    )
    if not standings:
        standings = Process(
            code=PROCESS_STANDINGS_EXTRACTION, name="Standings", is_active=True
        )
        db_session.add(standings)
        db_session.flush()

    odds = (
        db_session.query(Process)
        .filter(Process.code == PROCESS_ODDS_WPLAY_EXTRACTION)
        .first()
    )
    if not odds:
        odds = Process(code=PROCESS_ODDS_WPLAY_EXTRACTION, name="Odds", is_active=True)
        db_session.add(odds)
        db_session.flush()

    calendar = (
        db_session.query(Process)
        .filter(Process.code == PROCESS_CALENDAR_EXTRACTION)
        .first()
    )
    if not calendar:
        calendar = Process(
            code=PROCESS_CALENDAR_EXTRACTION, name="Calendar", is_active=True
        )
        db_session.add(calendar)
        db_session.flush()

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

    # Crear detalles con process_id específico
    detalles = [
        DetalleFuenteExtraccion(
            torneo_id=torneo.id,
            fuente_id=fuentes[0].id,
            url="https://test.com/s",
            is_active=True,
            process_id=standings.id,
        ),
        DetalleFuenteExtraccion(
            torneo_id=torneo.id,
            fuente_id=fuentes[1].id,
            url="https://test.com/o",
            is_active=True,
            process_id=odds.id,
        ),
        DetalleFuenteExtraccion(
            torneo_id=torneo.id,
            fuente_id=fuentes[2].id,
            url="https://test.com/c",
            is_active=True,
            process_id=calendar.id,
        ),
    ]
    for d in detalles:
        db_session.add(d)
    db_session.flush()
    db_session.commit()

    yield {
        "orchestrator": orchestrator,
        "standings": standings,
        "odds": odds,
        "calendar": calendar,
        "detalles": detalles,
        "torneo": torneo,
        "liga": liga,
        "pais": pais,
        "continente": continente,
        "fuentes": fuentes,
        "suffix": suffix,
    }

    # Cleanup: eliminar datos de prueba creados
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


def test_orchestrator_executes_all(db_session, test_data):
    """El orquestador ejecuta TODOS los trabajos."""
    from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
        _build_jobs_from_leagues,
    )
    from apps.leagues_manager.infrastructure.repositories.sql_platform_repository import (
        SqlPlatformRepository,
    )

    leagues = SqlPlatformRepository(db_session).get_all_leagues_with_full_details()
    flat_jobs, _ = _build_jobs_from_leagues(
        leagues,
        target_process_id=test_data["orchestrator"].id,
        is_general_orchestrator=True,
    )

    assert (
        len(flat_jobs) == 3
    ), f"Orquestador debería ejecutar 3 trabajos, ejecutó {len(flat_jobs)}"
    logger.success("✅ Orquestador ejecuta TODOS los procesos")


def test_standings_executes_only_standings(db_session, test_data):
    """Proceso standings ejecuta SOLO standings."""
    from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
        _build_jobs_from_leagues,
    )
    from apps.leagues_manager.infrastructure.repositories.sql_platform_repository import (
        SqlPlatformRepository,
    )

    leagues = SqlPlatformRepository(db_session).get_all_leagues_with_full_details()
    flat_jobs, _ = _build_jobs_from_leagues(
        leagues,
        target_process_id=test_data["standings"].id,
        is_general_orchestrator=False,
    )

    assert len(flat_jobs) == 1
    assert flat_jobs[0][1].fuente.type == RobotTypeEnum.STANDINGS
    logger.success("✅ Proceso standings ejecuta SOLO sus trabajos")


def test_odds_executes_only_odds(db_session, test_data):
    """Proceso odds ejecuta SOLO odds."""
    from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
        _build_jobs_from_leagues,
    )
    from apps.leagues_manager.infrastructure.repositories.sql_platform_repository import (
        SqlPlatformRepository,
    )

    leagues = SqlPlatformRepository(db_session).get_all_leagues_with_full_details()
    flat_jobs, _ = _build_jobs_from_leagues(
        leagues, target_process_id=test_data["odds"].id, is_general_orchestrator=False
    )

    assert len(flat_jobs) == 1
    assert flat_jobs[0][1].fuente.type == RobotTypeEnum.ODDS_WPLAY
    logger.success("✅ Proceso odds ejecuta SOLO sus trabajos")


def test_calendar_executes_only_calendar(db_session, test_data):
    """Proceso calendar ejecuta SOLO calendar."""
    from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
        _build_jobs_from_leagues,
    )
    from apps.leagues_manager.infrastructure.repositories.sql_platform_repository import (
        SqlPlatformRepository,
    )

    leagues = SqlPlatformRepository(db_session).get_all_leagues_with_full_details()
    flat_jobs, _ = _build_jobs_from_leagues(
        leagues,
        target_process_id=test_data["calendar"].id,
        is_general_orchestrator=False,
    )

    assert len(flat_jobs) == 1
    assert flat_jobs[0][1].fuente.type == RobotTypeEnum.CALENDAR
    logger.success("✅ Proceso calendar ejecuta SOLO sus trabajos")
