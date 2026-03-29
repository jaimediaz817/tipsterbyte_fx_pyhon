"""
Rutas para bitácora de sesión.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from apps.auth.application.services.session_log_service import SessionLogService
from apps.auth.infrastructure.repositories.session_log_repository import (
    SessionLogRepository,
)
from apps.auth.api.v1.dtos.session_log_dto import (
    SessionLogsListResponse,
    SessionLogsBySessionResponse,
)

router = APIRouter(prefix="/users", tags=["Session Logs"])


def get_session_log_service() -> SessionLogService:
    """Dependency para obtener el servicio de bitácora de sesión."""
    repository = SessionLogRepository()
    return SessionLogService(repository)


@router.get(
    "/{user_id}/logs",
    response_model=SessionLogsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener bitácora de accesos de un usuario",
)
async def get_user_logs(
    user_id: UUID,
    start_date: datetime = Query(..., description="Fecha de inicio (ISO 8601)"),
    end_date: datetime = Query(..., description="Fecha de fin (ISO 8601)"),
    action: Optional[str] = Query(None, description="Filtrar por tipo de acción"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    service: SessionLogService = Depends(get_session_log_service),
):
    """
    Obtiene la bitácora de accesos de un usuario con paginación y filtros.

    - **user_id**: ID del usuario (UUID)
    - **start_date**: Fecha de inicio en formato ISO 8601
    - **end_date**: Fecha de fin en formato ISO 8601
    - **action**: Filtrar por tipo de acción (opcional)
    - **limit**: Límite de resultados (1-1000, default: 100)
    - **offset**: Offset para paginación (default: 0)
    """
    return await service.get_user_logs(
        user_id, start_date, end_date, action, limit, offset
    )


@router.get(
    "/sessions/{session_id}",
    response_model=SessionLogsBySessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener logs por session_id",
)
async def get_session_logs(
    session_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    service: SessionLogService = Depends(get_session_log_service),
):
    """
    Obtiene los logs asociados a una sesión específica.

    - **session_id**: ID de la sesión
    - **limit**: Límite de resultados (1-1000, default: 100)
    - **offset**: Offset para paginación (default: 0)
    """
    return await service.get_session_logs(session_id, limit, offset)
