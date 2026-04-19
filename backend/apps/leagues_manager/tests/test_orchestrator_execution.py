"""
✅ TEST UNITARIO 100% MOCKEADO - Orquestador y Procesos Específicos
✅ NO HAY NINGUNA CONEXION A BASE DE DATOS
✅ TODOS LOS DATOS SON EN MEMORIA
✅ NO ESCRIBE NADA EN NINGUN LUGAR
✅ ACTUALIZADO 2026 - VERSION REFACTOREADA DESPUES CAMBIOS ARQUITECTURA
"""

import sys
from pathlib import Path

# ✅ SOLUCION PERMANENTE PATH: Funciona en TODOS los entornos
ROOT_PROYECTO = Path(__file__).resolve().parents[3]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

# ✅ Cargar automaticamente variables de entorno
from dotenv import load_dotenv

load_dotenv(ROOT_PROYECTO / "backend" / ".env")

import pytest
import uuid
from loguru import logger
from types import SimpleNamespace

from apps.leagues_manager.domain.entities.continente import Continente
from apps.leagues_manager.domain.entities.pais import Pais
from apps.leagues_manager.domain.entities.liga import Liga
from apps.leagues_manager.domain.entities.torneo import Torneo
from apps.leagues_manager.domain.entities.fuente_extraccion import FuenteExtraccion
from apps.leagues_manager.domain.entities.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion,
)
from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum

from shared.constants.process.process_codes import (
    PROCESS_EXTRACT_DATA_FUENTES,
    PROCESS_STANDINGS_EXTRACTION,
    PROCESS_ODDS_WPLAY_EXTRACTION,
    PROCESS_CALENDAR_EXTRACTION,
)


@pytest.fixture(scope="function")
def test_data():
    """✅ Crea DATOS DE PRUEBA 100% EN MEMORIA - SIN BASE DE DATOS"""
    suffix = uuid.uuid4().hex[:12]

    # ✅ Procesos - Objetos simples sin dependencias externas
    orchestrator = SimpleNamespace(
        id=1, code=PROCESS_EXTRACT_DATA_FUENTES, name="Orchestrator", is_active=True
    )

    standings = SimpleNamespace(
        id=2, code=PROCESS_STANDINGS_EXTRACTION, name="Standings", is_active=True
    )

    odds = SimpleNamespace(
        id=3, code=PROCESS_ODDS_WPLAY_EXTRACTION, name="Odds", is_active=True
    )

    calendar = SimpleNamespace(
        id=4, code=PROCESS_CALENDAR_EXTRACTION, name="Calendar", is_active=True
    )

    # ✅ Estructura geografica completa en memoria
    continente = Continente(id=1, nombre=f"EU_{suffix[:4]}", codigo=f"EU{suffix[:4]}")

    pais = Pais(
        id=1,
        nombre=f"Spain_{suffix[:4]}",
        codigo_iso=f"E{suffix[:2]}",
        continente_id=continente.id,
    )

    liga = Liga(id=1, nombre=f"LaLiga_{suffix}", pais_id=pais.id)

    torneo = Torneo(id=1, nombre=f"Season_{suffix}", liga_id=liga.id)

    # Agregar atributo is_active que no esta en el constructor
    object.__setattr__(liga, "is_active", True)
    object.__setattr__(torneo, "is_active", True)

    from datetime import datetime

    # ✅ Fuentes de extraccion
    fuentes = [
        FuenteExtraccion(
            id=1,
            name=f"Standings_{suffix}",
            type=RobotTypeEnum.STANDINGS,
            is_active=True,
            descripcion="",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        FuenteExtraccion(
            id=2,
            name=f"Odds_{suffix}",
            type=RobotTypeEnum.ODDS_WPLAY,
            is_active=True,
            descripcion="",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        FuenteExtraccion(
            id=3,
            name=f"Calendar_{suffix}",
            type=RobotTypeEnum.CALENDAR,
            is_active=True,
            descripcion="",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]

    # ✅ Detalles con process_id especifico
    from typing import cast

    detalles = [
        DetalleFuenteExtraccion(
            id=1,
            torneo_id=torneo.id,
            fuente_id=cast(int, fuentes[0].id),
            url="https://test.com/s",
            is_active=True,
            process_id=standings.id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        DetalleFuenteExtraccion(
            id=2,
            torneo_id=torneo.id,
            fuente_id=cast(int, fuentes[1].id),
            url="https://test.com/o",
            is_active=True,
            process_id=odds.id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        DetalleFuenteExtraccion(
            id=3,
            torneo_id=torneo.id,
            fuente_id=cast(int, fuentes[2].id),
            url="https://test.com/c",
            is_active=True,
            process_id=calendar.id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]

    # ✅ SOLUCION PARA FROZEN DATACLASS: Usamos object.__setattr__
    # Las entidades son @dataclass(frozen=True) por lo que no se pueden modificar directamente
    for detalle, fuente in zip(detalles, fuentes):
        object.__setattr__(detalle, "fuente", fuente)

    # Asociar detalles al torneo
    object.__setattr__(torneo, "detalles_fuente", detalles)

    # Asociar torneos a la liga
    object.__setattr__(liga, "torneos", [torneo])

    return {
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
        "lista_ligas": [liga],
    }


def test_orchestrator_executes_all(test_data):
    """✅ El orquestador ejecuta TODOS los trabajos."""
    from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
        _build_jobs_from_leagues,
    )

    flat_jobs, _ = _build_jobs_from_leagues(
        test_data["lista_ligas"],
        target_process_id=test_data["orchestrator"].id,
        is_general_orchestrator=True,
    )

    assert (
        len(flat_jobs) == 3
    ), f"Orquestador debería ejecutar 3 trabajos, ejecutó {len(flat_jobs)}"
    logger.success("✅ Orquestador ejecuta TODOS los procesos")


def test_standings_executes_only_standings(test_data):
    """✅ Proceso standings ejecuta SOLO sus trabajos asignados."""
    from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
        _build_jobs_from_leagues,
    )

    flat_jobs, _ = _build_jobs_from_leagues(
        test_data["lista_ligas"],
        target_process_id=test_data["standings"].id,
        is_general_orchestrator=False,
    )

    assert len(flat_jobs) == 1
    assert flat_jobs[0][1].fuente.type == RobotTypeEnum.STANDINGS
    logger.success("✅ Proceso standings ejecuta SOLO sus trabajos")


def test_odds_executes_only_odds(test_data):
    """✅ Proceso odds ejecuta SOLO sus trabajos asignados."""
    from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
        _build_jobs_from_leagues,
    )

    flat_jobs, _ = _build_jobs_from_leagues(
        test_data["lista_ligas"],
        target_process_id=test_data["odds"].id,
        is_general_orchestrator=False,
    )

    assert len(flat_jobs) == 1
    assert flat_jobs[0][1].fuente.type == RobotTypeEnum.ODDS_WPLAY
    logger.success("✅ Proceso odds ejecuta SOLO sus trabajos")


def test_calendar_executes_only_calendar(test_data):
    """✅ Proceso calendar ejecuta SOLO sus trabajos asignados."""
    from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
        _build_jobs_from_leagues,
    )

    flat_jobs, _ = _build_jobs_from_leagues(
        test_data["lista_ligas"],
        target_process_id=test_data["calendar"].id,
        is_general_orchestrator=False,
    )

    assert len(flat_jobs) == 1
    assert flat_jobs[0][1].fuente.type == RobotTypeEnum.CALENDAR
    logger.success("✅ Proceso calendar ejecuta SOLO sus trabajos")


def test_unknown_process_returns_zero_jobs(test_data):
    """✅ Proceso desconocido no devuelve ningun trabajo. COBERTURA EXTRA"""
    from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
        _build_jobs_from_leagues,
    )

    flat_jobs, _ = _build_jobs_from_leagues(
        test_data["lista_ligas"],
        target_process_id=999,
        is_general_orchestrator=False,
    )

    assert len(flat_jobs) == 0
    logger.success("✅ Proceso desconocido retorna 0 trabajos correctamente")


def test_inactive_details_are_skipped(test_data):
    """✅ Detalles inactivos son ignorados. COBERTURA EXTRA"""
    from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
        _build_jobs_from_leagues,
    )

    # Desactivamos un detalle
    object.__setattr__(test_data["detalles"][0], "is_active", False)

    flat_jobs, _ = _build_jobs_from_leagues(
        test_data["lista_ligas"],
        target_process_id=test_data["orchestrator"].id,
        is_general_orchestrator=True,
    )

    assert len(flat_jobs) == 2
    logger.success("✅ Detalles inactivos son correctamente ignorados")


def test_inactive_fuente_is_skipped(test_data):
    """✅ Fuente inactiva es ignorada completamente. NUEVA COBERTURA"""
    from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
        _build_jobs_from_leagues,
    )

    # Desactivamos la fuente, NO el detalle
    object.__setattr__(test_data["fuentes"][0], "is_active", False)

    flat_jobs, _ = _build_jobs_from_leagues(
        test_data["lista_ligas"],
        target_process_id=test_data["orchestrator"].id,
        is_general_orchestrator=True,
    )

    assert len(flat_jobs) == 2
    logger.success("✅ Fuentes inactivas son correctamente ignoradas")


def test_torneo_inactive_skips_all(test_data):
    """✅ Torneo inactivo ignora TODOS sus detalles. NUEVA COBERTURA"""
    from apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task import (
        _build_jobs_from_leagues,
    )

    # Desactivamos el torneo completo
    object.__setattr__(test_data["torneo"], "is_active", False)

    flat_jobs, _ = _build_jobs_from_leagues(
        test_data["lista_ligas"],
        target_process_id=test_data["orchestrator"].id,
        is_general_orchestrator=True,
    )

    assert len(flat_jobs) == 0
    logger.success("✅ Torneo inactivo ignora correctamente todos sus detalles")


if __name__ == "__main__":
    """✅ Permite ejecutar el test directamente desde consola sin pytest"""
    pytest.main([__file__, "-v", "-s"])
