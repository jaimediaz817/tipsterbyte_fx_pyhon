from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.platform_config.application.dto.process_create_dto import ProcessCreateDTO
from apps.platform_config.application.dto.process_dto import ProcessDTO
from apps.platform_config.application.dto.process_update_dto import ProcessUpdateDTO
from apps.platform_config.application.dto.scheduler_process_config_create_dto import ScheduledProcessConfigCreateDTO
from apps.platform_config.application.dto.scheduler_process_config_dto import ScheduledProcessConfigDTO
from apps.platform_config.application.dto.scheduler_process_config_update_dto import ScheduledProcessConfigUpdateDTO
from apps.platform_config.application.services.platform_config_service import PlatformConfigService
from apps.platform_config.infrastructure.repositories.sql_platform_config_repository import SQLPlatformConfigRepository
from core.db.sql.database_sql import get_db_session

from typing import List

router = APIRouter(prefix="/api/v1/platform-config", tags=["PlatformConfig"])

def get_service(db: Session = Depends(get_db_session)):
    repo = SQLPlatformConfigRepository(db)
    return PlatformConfigService(repo)

# --- ScheduledProcessConfig ---
@router.post("/scheduled-processes", response_model=ScheduledProcessConfigDTO)
def crear_scheduled_process(dto: ScheduledProcessConfigCreateDTO, service: PlatformConfigService = Depends(get_service)):
    return service.registrar_scheduled_process_config(dto)

@router.get("/scheduled-processes", response_model=List[ScheduledProcessConfigDTO])
def listar_scheduled_processes(enabled_only: bool = False, service: PlatformConfigService = Depends(get_service)):
    return service.obtener_scheduled_process_configs(enabled_only=enabled_only)

@router.get("/scheduled-processes/{process_name}", response_model=ScheduledProcessConfigDTO)
def obtener_scheduled_process(process_name: str, service: PlatformConfigService = Depends(get_service)):
    cfg = service.obtener_scheduled_process_config(process_name)
    if not cfg:
        raise HTTPException(status_code=404, detail="ScheduledProcessConfig no encontrado")
    return cfg

@router.patch("/scheduled-processes/{process_name}", response_model=ScheduledProcessConfigDTO)
def actualizar_scheduled_process(process_name: str, dto: ScheduledProcessConfigUpdateDTO, service: PlatformConfigService = Depends(get_service)):
    try:
        return service.actualizar_scheduled_process_config(process_name, dto)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Process ---
@router.post("/processes", response_model=ProcessDTO)
def crear_process(dto: ProcessCreateDTO, service: PlatformConfigService = Depends(get_service)):
    return service.registrar_process(dto)

@router.get("/processes", response_model=List[ProcessDTO])
def listar_processes(active_only: bool = False, service: PlatformConfigService = Depends(get_service)):
    return service.obtener_processes(active_only=active_only)

@router.get("/processes/{code}", response_model=ProcessDTO)
def obtener_process(code: str, service: PlatformConfigService = Depends(get_service)):
    p = service.obtener_process(code)
    if not p:
        raise HTTPException(status_code=404, detail="Process no encontrado")
    return p

@router.patch("/processes/{code}", response_model=ProcessDTO)
def actualizar_process(code: str, dto: ProcessUpdateDTO, service: PlatformConfigService = Depends(get_service)):
    try:
        return service.actualizar_process(code, dto)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))