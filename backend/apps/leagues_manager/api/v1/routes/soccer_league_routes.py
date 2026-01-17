from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from apps.leagues_manager.services.leagues_service import LeaguesService
from apps.leagues_manager.application.dto.continente_create_dto import ContinenteCreateDTO
from apps.leagues_manager.application.dto.continente_dto import ContinenteDTO
from apps.leagues_manager.application.dto.liga_create_dto import LigaCreateDTO
from apps.leagues_manager.application.dto.liga_dto import LigaDTO
from apps.leagues_manager.application.dto.pais_create_dto import PaisCreateDTO
from apps.leagues_manager.application.dto.pais_dto import PaisDTO
from apps.leagues_manager.application.dto.torneo_create_dto import TorneoCreateDTO
from apps.leagues_manager.application.dto.torneo_dto import TorneoDTO
from core.db.sql.database_sql import get_db_session
from typing import List
from apps.leagues_manager.infrastructure.repositories.sql_leagues_repository import SQLLeaguesRepository
# from apps.leagues_manager.application.services.leagues_service import LeaguesService
# from apps.leagues_manager.application.dtos.leagues_dtos import (
#     ContinenteCreateDTO, PaisCreateDTO, LigaCreateDTO, TorneoCreateDTO,
#     ContinenteDTO, PaisDTO, LigaDTO, TorneoDTO
# )

router = APIRouter(prefix="/api/v1/leagues", tags=["LeaguesManager"])

def get_service(db: Session = Depends(get_db_session)):
    repo = SQLLeaguesRepository(db)
    return LeaguesService(repo)

@router.post("/continentes", response_model=ContinenteDTO)
def crear_continente(dto: ContinenteCreateDTO, service: LeaguesService = Depends(get_service)):
    return service.registrar_continente(dto)

@router.post("/paises", response_model=PaisDTO)
def crear_pais(dto: PaisCreateDTO, service: LeaguesService = Depends(get_service)):
    return service.registrar_pais(dto)

@router.post("/ligas", response_model=LigaDTO)
def crear_liga(dto: LigaCreateDTO, service: LeaguesService = Depends(get_service)):
    return service.registrar_liga(dto)

@router.post("/torneos", response_model=TorneoDTO)
def crear_torneo(dto: TorneoCreateDTO, service: LeaguesService = Depends(get_service)):
    return service.registrar_torneo(dto)

# --- NUEVAS RUTAS GET ---

# --- Continentes ---
@router.get("/continentes", response_model=List[ContinenteDTO])
def obtener_continentes(service: LeaguesService = Depends(get_service)):
    return service.obtener_todos_los_continentes()

@router.get("/continentes/{continente_id}", response_model=ContinenteDTO)
def obtener_continente(continente_id: int, service: LeaguesService = Depends(get_service)):
    continente = service.obtener_continente_por_id(continente_id)
    if not continente:
        raise HTTPException(status_code=404, detail="Continente no encontrado")
    return continente

# # --- Paises ---
# @router.get("/paises", response_model=List[PaisDTO])
# def obtener_paises(service: LeaguesService = Depends(get_service)):
#     return service.obtener_paises()

# @router.get("/paises/{pais_id}", response_model=PaisDTO)
# def obtener_pais(pais_id: int, service: LeaguesService = Depends(get_service)):
#     pais = service.obtener_pais_por_id(pais_id)
#     if not pais:
#         raise HTTPException(status_code=404, detail="País no encontrado")
#     return pais

# # --- Ligas ---
# @router.get("/ligas", response_model=List[LigaDTO])
# def obtener_ligas(service: LeaguesService = Depends(get_service)):
#     return service.obtener_ligas()

# @router.get("/ligas/{liga_id}", response_model=LigaDTO)
# def obtener_liga(liga_id: int, service: LeaguesService = Depends(get_service)):
#     liga = service.obtener_liga_por_id(liga_id)
#     if not liga:
#         raise HTTPException(status_code=404, detail="Liga no encontrada")
#     return liga

# # --- Torneos ---
# @router.get("/torneos", response_model=List[TorneoDTO])
# def obtener_torneos(service: LeaguesService = Depends(get_service)):
#     return service.obtener_torneos()

# @router.get("/torneos/{torneo_id}", response_model=TorneoDTO)
# def obtener_torneo(torneo_id: int, service: LeaguesService = Depends(get_service)):
#     torneo = service.obtener_torneo_por_id(torneo_id)
#     if not torneo:
#         raise HTTPException(status_code=404, detail="Torneo no encontrado")
#     return torneo