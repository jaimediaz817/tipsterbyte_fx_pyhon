import unittest
from unittest.mock import MagicMock, patch
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from apps.leagues_manager.infrastructure.repositories.sql_leagues_repository import (
    SQLLeaguesRepository,
)
from apps.leagues_manager.domain.entities.continente import Continente
from apps.leagues_manager.domain.entities.pais import Pais
from apps.leagues_manager.domain.entities.liga import Liga
from apps.leagues_manager.domain.entities.torneo import Torneo
from apps.leagues_manager.domain.enums.categoria_liga_enum import CategoriaLigaEnum

from apps.leagues_manager.infrastructure.models.sql.continente import (
    Continente,
)
from apps.leagues_manager.infrastructure.models.sql.pais import Pais as PaisModel
from apps.leagues_manager.infrastructure.models.sql.liga import Liga as LigaModel
from apps.leagues_manager.infrastructure.models.sql.torneo import Torneo as TorneoModel
from apps.leagues_manager.infrastructure.models.sql.fuente_extraccion import (
    FuenteExtraccion,
)
from apps.leagues_manager.infrastructure.models.sql.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion,
)


class TestSQLLeaguesRepository(unittest.TestCase):
    def setUp(self):
        """Configura el mock de la sesión de la base de datos para cada prueba."""
        self.db_session_mock = MagicMock(spec=Session)
        self.repository = SQLLeaguesRepository(self.db_session_mock)

    def test_create_repository(self):
        """Prueba que la instancia del repositorio se crea sin errores."""
        self.assertIsInstance(self.repository, SQLLeaguesRepository)

    # --- Pruebas para Continente ---

    def test_get_all_continentes(self):
        """Prueba obtener todos los continentes."""
        # Configurar el mock
        continente_model = Continente(id=1, nombre="América", codigo="AM")
        self.db_session_mock.query.return_value.all.return_value = [continente_model]

        # Ejecutar
        result: list[Continente] = self.repository.get_all_continentes()

        # Verificar
        self.db_session_mock.query.assert_called_once_with(Continente)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Continente)
        self.assertIsNotNone(result[0].id)
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[0].nombre, "América")
        self.assertEqual(result[0].codigo, "AM")

    def test_get_continente_by_nombre_found(self):
        """Prueba obtener un continente por nombre cuando existe."""
        continente_model = Continente(id=1, nombre="América", codigo="AM")
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            continente_model
        )

        result: Continente = self.repository.get_continente_by_nombre("América")

        self.assertIsNotNone(result)
        self.assertEqual(result.nombre, "América")

    def test_get_continente_by_nombre_not_found(self):
        """Prueba obtener un continente por nombre cuando no existe."""
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            None
        )

        result = self.repository.get_continente_by_nombre("Europa")

        self.assertIsNone(result)

    def test_create_continente(self):
        """Prueba crear un nuevo continente."""
        continente_model = Continente(id=1, nombre="África", codigo="AF")
        self.db_session_mock.add.return_value = None
        self.db_session_mock.commit.return_value = None
        self.db_session_mock.refresh.return_value = None
        # Mock para que el objeto tenga los atributos después de refresh
        with patch.object(
            self.db_session_mock,
            "refresh",
            side_effect=lambda obj: setattr(obj, "id", 1),
        ):
            result = self.repository.create_continente("África", "AF")

        self.assertIsInstance(result, Continente)
        self.assertEqual(result.nombre, "África")
        self.assertEqual(result.codigo, "AF")

    def test_update_continente_success(self):
        """Prueba actualizar un continente existente."""
        continente_model = Continente(id=1, nombre="América", codigo="AM")
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            continente_model
        )
        self.db_session_mock.commit.return_value = None
        self.db_session_mock.refresh.return_value = None

        data = {"nombre": "América del Sur", "codigo": "SOUTH"}
        result = self.repository.update_continente(1, data)

        self.assertEqual(result.nombre, "América del Sur")
        self.assertEqual(result.codigo, "SOUTH")

    def test_update_continente_not_found(self):
        """Prueba actualizar un continente que no existe."""
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            None
        )

        with self.assertRaises(ValueError) as context:
            self.repository.update_continente(999, {"nombre": "Inexistente"})

        self.assertIn("Continente no encontrado", str(context.exception))

    # --- Pruebas para País ---

    def test_get_pais_by_nombre_and_continente_found(self):
        """Prueba obtener un país por nombre y continente cuando existe."""
        pais_model = PaisModel(
            id=1, nombre="Colombia", codigo_iso="COL", continente_id=1
        )
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            pais_model
        )

        result: Pais | None = self.repository.get_pais_by_nombre_and_continente(
            "Colombia", 1
        )

        self.assertIsNotNone(result)
        nombre_obtenido = getattr(result, "nombre", None)
        self.assertEqual(nombre_obtenido, "Colombia")

        codigo_iso_obtenido = getattr(result, "codigo_iso", None)
        self.assertEqual(codigo_iso_obtenido, "COL")

    def test_get_pais_by_nombre_found(self):
        """Prueba obtener un país por nombre cuando existe."""
        pais_model = PaisModel(id=1, nombre="Brasil", codigo_iso="BRA", continente_id=1)
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            pais_model
        )

        result = self.repository.get_pais_by_nombre("Brasil")

        self.assertIsNotNone(result)
        nombre_obtenido = getattr(result, "nombre", None)
        self.assertEqual(nombre_obtenido, "Brasil")

    def test_create_pais(self):
        """Prueba crear un nuevo país."""
        pais_model = PaisModel(
            id=1, nombre="Argentina", codigo_iso="ARG", continente_id=1
        )
        self.db_session_mock.add.return_value = None
        self.db_session_mock.commit.return_value = None
        self.db_session_mock.refresh.return_value = None

        with patch.object(
            self.db_session_mock,
            "refresh",
            side_effect=lambda obj: setattr(obj, "id", 1),
        ):
            result = self.repository.create_pais("Argentina", "ARG", 1)

        self.assertIsInstance(result, Pais)
        self.assertEqual(result.nombre, "Argentina")
        self.assertEqual(result.codigo_iso, "ARG")

    def test_update_pais_success(self):
        """Prueba actualizar un país existente."""
        pais_model = PaisModel(id=1, nombre="Chile", codigo_iso="CHL", continente_id=1)
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            pais_model
        )
        self.db_session_mock.commit.return_value = None
        self.db_session_mock.refresh.return_value = None

        data = {"nombre": "Chile Nuevo", "codigo_iso": "CLN"}
        result = self.repository.update_pais(1, data)

        self.assertEqual(result.nombre, "Chile Nuevo")
        self.assertEqual(result.codigo_iso, "CLN")

    def test_update_pais_not_found(self):
        """Prueba actualizar un país que no existe."""
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            None
        )

        with self.assertRaises(ValueError) as context:
            self.repository.update_pais(999, {"nombre": "Inexistente"})

        self.assertIn("País no encontrado", str(context.exception))

    # --- Pruebas para Liga ---

    def test_get_liga_by_nombre_and_pais_found(self):
        """Prueba obtener una liga por nombre y país cuando existe."""
        liga_model = LigaModel(
            id=1,
            nombre="Liga BetPlay",
            nombre_categoria=CategoriaLigaEnum.A,
            pais_id=1,
        )
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            liga_model
        )

        result: Liga | None = self.repository.get_liga_by_nombre_and_pais(
            "Liga BetPlay", 1
        )

        self.assertIsNotNone(result)
        nombre_obtenido = getattr(result, "nombre", None)
        self.assertEqual(nombre_obtenido, "Liga BetPlay")
        categoria_obtenida = getattr(result, "nombre_categoria", None)
        self.assertEqual(categoria_obtenida, CategoriaLigaEnum.A)

    def test_get_liga_by_nombre_found(self):
        """Prueba obtener una liga por nombre cuando existe."""
        liga_model = LigaModel(
            id=1,
            nombre="Premier League",
            nombre_categoria=CategoriaLigaEnum.A,
            pais_id=1,
        )
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            liga_model
        )

        result = self.repository.get_liga_by_nombre("Premier League")

        self.assertIsNotNone(result)
        nombre_obtenido = getattr(result, "nombre", None)
        self.assertEqual(nombre_obtenido, "Premier League")

    def test_create_liga(self):
        """Prueba crear una nueva liga."""
        liga_model = LigaModel(
            id=1,
            nombre="Liga Pro",
            nombre_categoria=CategoriaLigaEnum.A,
            pais_id=1,
        )
        self.db_session_mock.add.return_value = None
        self.db_session_mock.commit.return_value = None
        self.db_session_mock.refresh.return_value = None

        with patch.object(
            self.db_session_mock,
            "refresh",
            side_effect=lambda obj: setattr(obj, "id", 1),
        ):
            result = self.repository.create_liga(
                "Liga Pro", CategoriaLigaEnum.A.value, 1
            )

        self.assertIsInstance(result, Liga)
        self.assertEqual(result.nombre, "Liga Pro")
        self.assertEqual(result.nombre_categoria, CategoriaLigaEnum.A)

    def test_update_liga_success(self):
        """Prueba actualizar una liga existente."""
        liga_model = LigaModel(
            id=1,
            nombre="Liga Antigua",
            nombre_categoria=CategoriaLigaEnum.A,
            pais_id=1,
        )
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            liga_model
        )
        self.db_session_mock.commit.return_value = None
        self.db_session_mock.refresh.return_value = None

        data = {
            "nombre": "Liga Nueva",
            "nombre_categoria": CategoriaLigaEnum.B.value,
        }
        result = self.repository.update_liga(1, data)

        self.assertEqual(result.nombre, "Liga Nueva")
        self.assertEqual(result.nombre_categoria, CategoriaLigaEnum.B)

    def test_update_liga_not_found(self):
        """Prueba actualizar una liga que no existe."""
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            None
        )

        with self.assertRaises(ValueError) as context:
            self.repository.update_liga(999, {"nombre": "Liga Inexistente"})

        self.assertIn("Liga no encontrada", str(context.exception))

    # --- Pruebas para Torneo ---

    def test_get_torneo_by_nombre_and_liga_found(self):
        """Prueba obtener un torneo por nombre y liga cuando existe."""
        torneo_model = TorneoModel(
            id=1, nombre="Apertura 2026", liga_id=1, fecha_inicio=date(2026, 1, 1)
        )
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            torneo_model
        )

        result = self.repository.get_torneo_by_nombre_and_liga("Apertura 2026", 1)

        self.assertIsNotNone(result)
        nombre_obtenido = getattr(result, "nombre", None)
        self.assertEqual(nombre_obtenido, "Apertura 2026")
        liga_id_obtenido = getattr(result, "liga_id", None)
        self.assertEqual(liga_id_obtenido, 1)

    def test_create_torneo(self):
        """Prueba crear un nuevo torneo."""
        torneo_model = TorneoModel(
            id=1, nombre="Clausura 2026", liga_id=1, fecha_inicio=date(2026, 7, 1)
        )
        self.db_session_mock.add.return_value = None
        self.db_session_mock.commit.return_value = None
        self.db_session_mock.refresh.return_value = None

        with patch.object(
            self.db_session_mock,
            "refresh",
            side_effect=lambda obj: setattr(obj, "id", 1),
        ):
            result = self.repository.create_torneo(
                "Clausura 2026", 1, fecha_inicio=date(2026, 7, 1)
            )

        self.assertIsInstance(result, Torneo)
        self.assertEqual(result.nombre, "Clausura 2026")
        self.assertEqual(result.liga_id, 1)

    def test_update_torneo_success(self):
        """Prueba actualizar un torneo existente."""
        torneo_model = TorneoModel(
            id=1, nombre="Torneo Antiguo", liga_id=1, fecha_inicio=date(2026, 1, 1)
        )
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            torneo_model
        )
        self.db_session_mock.commit.return_value = None
        self.db_session_mock.refresh.return_value = None

        data = {"nombre": "Torneo Nuevo", "fecha_inicio": date(2026, 2, 1)}
        result = self.repository.update_torneo(1, data)

        self.assertEqual(result.nombre, "Torneo Nuevo")
        self.assertEqual(result.fecha_inicio, date(2026, 2, 1))

    def test_update_torneo_not_found(self):
        """Prueba actualizar un torneo que no existe."""
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            None
        )

        with self.assertRaises(ValueError) as context:
            self.repository.update_torneo(999, {"nombre": "Torneo Inexistente"})

        self.assertIn("Torneo no encontrado", str(context.exception))

    # --- Pruebas para FuenteExtraccion (¡NUEVAS!) ---

    def test_get_fuente_extraccion_by_name_found(self):
        """Prueba obtener una FuenteExtraccion por nombre cuando existe."""
        fuente_model = FuenteExtraccion(
            id=1, name="Wplay", type="API", descripcion="Apuestas Wplay", is_active=True
        )
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            fuente_model
        )

        result = self.repository.get_fuente_extraccion_by_name("Wplay")

        self.assertIsNotNone(result)
        nombre_obtenido = getattr(result, "name", None)
        self.assertEqual(nombre_obtenido, "Wplay")
        type_obtenido = getattr(result, "type", None)
        self.assertEqual(type_obtenido, "API")

    def test_get_fuente_extraccion_by_name_not_found(self):
        """Prueba obtener una FuenteExtraccion por nombre cuando no existe."""
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            None
        )

        result = self.repository.get_fuente_extraccion_by_name("Inexistente")

        self.assertIsNone(result)

    def test_create_fuente_extraccion(self):
        """Prueba crear una nueva FuenteExtraccion."""
        fuente_model = FuenteExtraccion(
            id=1,
            name="Bet365",
            type="API",
            descripcion="Apuestas Bet365",
            is_active=True,
        )
        self.db_session_mock.add.return_value = None
        self.db_session_mock.commit.return_value = None
        self.db_session_mock.refresh.return_value = None

        with patch.object(
            self.db_session_mock,
            "refresh",
            side_effect=lambda obj: setattr(obj, "id", 1),
        ):
            result = self.repository.create_fuente_extraccion(
                "Bet365", "API", "Apuestas Bet365", True
            )

        self.assertIsInstance(result, FuenteExtraccion)
        self.assertEqual(result.name, "Bet365")
        self.assertEqual(result.type, "API")

    def test_update_fuente_extraccion_success(self):
        """Prueba actualizar una FuenteExtraccion existente."""
        fuente_model = FuenteExtraccion(
            id=1, name="Wplay", type="API", descripcion="Apuestas Wplay", is_active=True
        )
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            fuente_model
        )
        self.db_session_mock.commit.return_value = None
        self.db_session_mock.refresh.return_value = None

        data = {"name": "Wplay Nuevo", "descripcion": "Apuestas Wplay Actualizadas"}
        result = self.repository.update_fuente_extraccion(1, data)

        self.assertEqual(result.name, "Wplay Nuevo")
        self.assertEqual(result.descripcion, "Apuestas Wplay Actualizadas")

    def test_update_fuente_extraccion_not_found(self):
        """Prueba actualizar una FuenteExtraccion que no existe."""
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            None
        )

        with self.assertRaises(ValueError) as context:
            self.repository.update_fuente_extraccion(999, {"name": "Inexistente"})

        self.assertIn(
            "FuenteExtraccion con ID 999 no encontrada", str(context.exception)
        )

    # --- Pruebas para DetalleFuenteExtraccion (¡NUEVAS!) ---

    def test_get_detalle_fuente_extraccion_by_torneo_and_fuente_found(self):
        """Prueba obtener un DetalleFuenteExtraccion por torneo y fuente cuando existe."""
        detalle_model = DetalleFuenteExtraccion(
            id=1,
            torneo_id=1,
            fuente_id=1,
            url="https://api.wplay.co",
            is_active=True,
            process_id=101,  # Añadir process_id
        )
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            detalle_model
        )

        result = self.repository.get_detalle_fuente_extraccion_by_torneo_and_fuente(
            1, 1
        )

        self.assertIsNotNone(result)
        torneo_id_obtenido = getattr(result, "torneo_id", None)
        fuente_id_obtenido = getattr(result, "fuente_id", None)
        url_obtenida = getattr(result, "url", None)
        self.assertEqual(torneo_id_obtenido, 1)
        self.assertEqual(fuente_id_obtenido, 1)
        self.assertEqual(url_obtenida, "https://api.wplay.co")
        # self.assertEqual(result.process_id, 101)  # ¡NUEVA ASERCIÓN!

    def test_get_detalle_fuente_extraccion_by_torneo_and_fuente_not_found(self):
        """Prueba obtener un DetalleFuenteExtraccion por torneo y fuente cuando no existe."""
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            None
        )

        result = self.repository.get_detalle_fuente_extraccion_by_torneo_and_fuente(
            1, 1
        )

        self.assertIsNone(result)

    def test_create_detalle_fuente_extraccion(self):
        """Prueba crear un nuevo DetalleFuenteExtraccion."""
        detalle_model = DetalleFuenteExtraccion(
            id=1,
            torneo_id=1,
            fuente_id=1,
            url="https://api.bet365.com",
            is_active=True,
            process_id=101,  # Añadir process_id
        )
        self.db_session_mock.add.return_value = None
        self.db_session_mock.commit.return_value = None
        self.db_session_mock.refresh.return_value = None

        with patch.object(
            self.db_session_mock,
            "refresh",
            side_effect=lambda obj: setattr(obj, "id", 1),
        ):
            # El método mockeado debe recibir el nuevo argumento
            result = self.repository.create_detalle_fuente_extraccion(
                1, 1, "https://api.bet365.com", True, 101  # ¡NUEVO! Pasar process_id
            )

        self.assertIsInstance(result, DetalleFuenteExtraccion)
        self.assertEqual(result.torneo_id, 1)
        self.assertEqual(result.fuente_id, 1)
        self.assertEqual(result.url, "https://api.bet365.com")
        self.assertEqual(result.process_id, 101)  # ¡NUEVA ASERCIÓN!

    def test_update_detalle_fuente_extraccion_success(self):
        """Prueba actualizar un DetalleFuenteExtraccion existente."""
        detalle_model = DetalleFuenteExtraccion(
            id=1,
            torneo_id=1,
            fuente_id=1,
            url="https://api.wplay.co",
            is_active=True,
            process_id=101,  # Añadir process_id
        )
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            detalle_model
        )
        self.db_session_mock.commit.return_value = None
        self.db_session_mock.refresh.return_value = None

        data = {
            "url": "https://api.wplay.co/nueva",
            "is_active": False,
            "process_id": 102,
        }  # ¡NUEVO! Actualizar process_id
        result = self.repository.update_detalle_fuente_extraccion(1, data)

        self.assertEqual(result.url, "https://api.wplay.co/nueva")
        self.assertEqual(result.is_active, False)
        self.assertEqual(result.process_id, 102)  # ¡NUEVA ASERCIÓN!

    def test_update_detalle_fuente_extraccion_not_found(self):
        """Prueba actualizar un DetalleFuenteExtraccion que no existe."""
        self.db_session_mock.query.return_value.filter.return_value.first.return_value = (
            None
        )

        with self.assertRaises(ValueError) as context:
            self.repository.update_detalle_fuente_extraccion(
                999, {"url": "https://nueva.url"}
            )

        self.assertIn(
            "DetalleFuenteExtraccion con ID 999 no encontrado", str(context.exception)
        )

    # --- Pruebas de Mapeo (¡NUEVAS!) ---

    def test_to_continente(self):
        """Prueba el mapeo de Continente a Continente."""
        continente_model = Continente(id=1, nombre="Europa", codigo="EU")
        result = self.repository._to_continente(continente_model)

        self.assertIsInstance(result, Continente)
        continente_id_obtenido = getattr(result, "id", None)
        continente_nombre_obtenido = getattr(result, "nombre", None)
        continente_codigo_obtenido = getattr(result, "codigo", None)
        self.assertIsNotNone(continente_id_obtenido)
        self.assertEqual(continente_id_obtenido, 1)
        self.assertEqual(continente_nombre_obtenido, "Europa")
        self.assertEqual(continente_codigo_obtenido, "EU")

    def test_to_continente_none(self):
        """Prueba el mapeo cuando el modelo es None."""
        result: Continente | None = self.repository._to_continente(None)
        self.assertIsNone(result)

    def test_to_pais(self):
        """Prueba el mapeo de PaisModel a Pais."""
        pais_model = PaisModel(
            id=1, nombre="Francia", codigo_iso="FRA", continente_id=1
        )
        result = self.repository._to_pais(pais_model)

        self.assertIsInstance(result, Pais)
        self.assertIsNotNone(result.id)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.nombre, "Francia")
        self.assertEqual(result.codigo_iso, "FRA")

    def test_to_liga(self):
        """Prueba el mapeo de LigaModel a Liga."""
        liga_model = LigaModel(
            id=1,
            nombre="Ligue 1",
            nombre_categoria=CategoriaLigaEnum.A,
            pais_id=1,
        )
        result = self.repository._to_liga(liga_model)

        self.assertIsInstance(result, Liga)
        self.assertIsNotNone(result.id)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.nombre, "Ligue 1")
        self.assertEqual(result.nombre_categoria, CategoriaLigaEnum.A)

    def test_to_torneo(self):
        """Prueba el mapeo de TorneoModel a Torneo."""
        torneo_model = TorneoModel(
            id=1, nombre="Ligue 1 2026", liga_id=1, fecha_inicio=date(2026, 1, 1)
        )
        result = self.repository._to_torneo(torneo_model)

        self.assertIsInstance(result, Torneo)
        self.assertIsNotNone(result.id)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.nombre, "Ligue 1 2026")
        self.assertEqual(result.liga_id, 1)
        self.assertEqual(result.fecha_inicio, date(2026, 1, 1))

    def test_to_fuente_extraccion(self):
        """Prueba el mapeo de FuenteExtraccion a FuenteExtraccion (¡NUEVO!)."""
        fuente_model = FuenteExtraccion(
            id=1, name="Wplay", type="API", descripcion="Apuestas Wplay", is_active=True
        )
        result = self.repository._to_fuente_extraccion(fuente_model)

        self.assertIsInstance(result, FuenteExtraccion)

        id_obtenido = getattr(result, "id", None)
        self.assertIsNotNone(id_obtenido)
        self.assertEqual(id_obtenido, 1)
        name_obtenido = getattr(result, "name", None)
        self.assertEqual(name_obtenido, "Wplay")
        type_obtenido = getattr(result, "type", None)
        self.assertEqual(type_obtenido, "API")
        descripcion_obtenida = getattr(result, "descripcion", None)
        self.assertEqual(descripcion_obtenida, "Apuestas Wplay")
        is_active_obtenido = getattr(result, "is_active", None)
        self.assertEqual(is_active_obtenido, True)

    def test_to_fuente_extraccion_none(self):
        """Prueba el mapeo cuando el modelo es None (¡NUEVO!)."""
        result = self.repository._to_fuente_extraccion(None)
        self.assertIsNone(result)

    def test_to_detalle_fuente_extraccion(self):
        """Prueba el mapeo de DetalleFuenteExtraccion a DetalleFuenteExtraccion."""
        detalle_model = DetalleFuenteExtraccion(
            id=1,
            torneo_id=1,
            fuente_id=1,
            url="https://api.wplay.co",
            is_active=True,
            process_id=101,  # Añadir process_id
        )
        result = self.repository._to_detalle_fuente_extraccion(detalle_model)

        self.assertIsInstance(result, DetalleFuenteExtraccion)
        id_obtenido = getattr(result, "id", None)
        self.assertIsNotNone(id_obtenido)
        self.assertEqual(id_obtenido, 1)
        torneo_id_obtenido = getattr(result, "torneo_id", None)
        self.assertEqual(torneo_id_obtenido, 1)
        fuente_id_obtenido = getattr(result, "fuente_id", None)
        self.assertEqual(fuente_id_obtenido, 1)
        url_obtenida = getattr(result, "url", None)
        self.assertEqual(url_obtenida, "https://api.wplay.co")
        process_id_obtenido = getattr(result, "process_id", None)  # ¡NUEVA ASERCIÓN!
        self.assertEqual(process_id_obtenido, 101)

    def test_to_detalle_fuente_extraccion_none(self):
        """Prueba el mapeo cuando el modelo es None."""
        result: DetalleFuenteExtraccion | None = (
            self.repository._to_detalle_fuente_extraccion(None)
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
