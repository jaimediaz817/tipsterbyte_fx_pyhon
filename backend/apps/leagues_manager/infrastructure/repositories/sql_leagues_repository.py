from sqlalchemy.orm import Session

from apps.leagues_manager.domain.entities.continente import Continente
from apps.leagues_manager.domain.entities.liga import Liga
from apps.leagues_manager.domain.entities.pais import Pais
from apps.leagues_manager.domain.entities.torneo import Torneo
from apps.leagues_manager.domain.repositories.i_leagues_repository import ILeaguesRepository


from apps.leagues_manager.infrastructure.models.sql.continente import Continente as ContinenteModel
from apps.leagues_manager.infrastructure.models.sql.pais import Pais as PaisModel
from apps.leagues_manager.infrastructure.models.sql.liga import Liga as LigaModel
from apps.leagues_manager.infrastructure.models.sql.torneo import Torneo as TorneoModel
from shared.utils.db.sql.sqlalchemy_utils import update_from_dict

class SQLLeaguesRepository(ILeaguesRepository):
    def __init__(self, db: Session):
        self.db = db

    # --- mappers ---
    def _to_continente(self, m: ContinenteModel) -> Continente:
        return Continente(m.id, m.nombre, m.codigo)

    def _to_pais(self, m: PaisModel) -> Pais:
        return Pais(m.id, m.nombre, m.continente_id, m.codigo_iso)

    def _to_liga(self, m: LigaModel) -> Liga:
        return Liga(m.id, m.nombre, m.pais_id, m.nombre_categoria)

    def _to_torneo(self, m: TorneoModel) -> Torneo:
        return Torneo(m.id, m.nombre, m.liga_id, m.fecha_inicio, m.fecha_fin)

    # --- Continente ---
    def get_all_continentes(self):
        ms = self.db.query(ContinenteModel).all()
        return [self._to_continente(m) for m in ms]
    
    def get_continente_by_nombre(self, nombre: str):
        m = self.db.query(ContinenteModel).filter(ContinenteModel.nombre == nombre).first()
        return self._to_continente(m) if m else None

    def create_continente(self, nombre: str, codigo: str | None):
        m = ContinenteModel(nombre=nombre, codigo=codigo)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._to_continente(m)


    def update_continente(self, continente_id: int, data: dict) -> Continente:
        obj = self.db.query(ContinenteModel).filter(ContinenteModel.id == continente_id).first()
        if not obj:
            raise ValueError("Continente no encontrado")
        update_from_dict(obj, data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_continente(obj)      

    # --- País ---
    def get_pais_by_nombre_and_continente(self, nombre: str, continente_id: int):
        m = self.db.query(PaisModel).filter(
            PaisModel.nombre == nombre,
            PaisModel.continente_id == continente_id
        ).first()
        return self._to_pais(m) if m else None

    def get_pais_by_nombre(self, nombre: str):
        m = self.db.query(PaisModel).filter(PaisModel.nombre == nombre).first()
        return self._to_pais(m) if m else None

    def create_pais(self, nombre: str, codigo_iso: str | None, continente_id: int):
        m = PaisModel(nombre=nombre, codigo_iso=codigo_iso, continente_id=continente_id)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._to_pais(m)
    
    def update_pais(self, pais_id: int, data: dict) -> Pais:
        obj = self.db.query(PaisModel).filter(PaisModel.id == pais_id).first()
        if not obj:
            raise ValueError("País no encontrado")
        update_from_dict(obj, data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_pais(obj)    

    # --- Liga ---
    def get_liga_by_nombre_and_pais(self, nombre: str, pais_id: int):
        m = self.db.query(LigaModel).filter(
            LigaModel.nombre == nombre,
            LigaModel.pais_id == pais_id
        ).first()
        return self._to_liga(m) if m else None

    def get_liga_by_nombre(self, nombre: str):
        m = self.db.query(LigaModel).filter(LigaModel.nombre == nombre).first()
        return self._to_liga(m) if m else None

    def create_liga(self, nombre: str, nombre_categoria: str | None, pais_id: int):
        m = LigaModel(nombre=nombre, nombre_categoria=nombre_categoria, pais_id=pais_id)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._to_liga(m)
    
    def update_liga(self, liga_id: int, data: dict) -> Liga:
        obj = self.db.query(LigaModel).filter(LigaModel.id == liga_id).first()
        if not obj:
            raise ValueError("Liga no encontrada")
        update_from_dict(obj, data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_liga(obj)    

    # --- Torneo ---
    def get_torneo_by_nombre_and_liga(self, nombre: str, liga_id: int):
        m = self.db.query(TorneoModel).filter(
            TorneoModel.nombre == nombre,
            TorneoModel.liga_id == liga_id
        ).first()
        return self._to_torneo(m) if m else None

    def create_torneo(self, nombre: str, liga_id: int, fecha_inicio=None, fecha_fin=None):
        m = TorneoModel(nombre=nombre, liga_id=liga_id, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._to_torneo(m)
    
    def update_torneo(self, torneo_id: int, data: dict) -> Torneo:
        obj = self.db.query(TorneoModel).filter(TorneoModel.id == torneo_id).first()
        if not obj:
            raise ValueError("Torneo no encontrado")
        update_from_dict(obj, data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_torneo(obj)    