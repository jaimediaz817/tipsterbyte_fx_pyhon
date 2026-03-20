# filepath: c:\Users\jdiaz\Documents\JDiaz-PC-DESKTOP-2\proyectos_jdiaz_pc_local\TIPSTERBYTE\tipsterByte_fx\backend\apps\leagues_manager\domain\enums\robot_type_enum.py
import enum


class RobotTypeEnum(str, enum.Enum):
    """
    Define los tipos válidos de robots de extracción de datos.
    Estos valores deben coincidir con las claves en JobRunnerApplication.robot_factory.
    """

    STANDINGS = "standings"
    ODDS_WPLAY = "odds_wplay"
    CALENDAR = "calendar"
    # Añade aquí cualquier otro tipo de robot que vayas a implementar
    # Por ejemplo:
    # ODDS_BETFAIR = "odds_betfair"
