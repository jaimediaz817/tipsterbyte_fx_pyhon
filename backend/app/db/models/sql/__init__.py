# Este archivo asegura que todos los modelos se registren en Base.metadata
# Esto es esencial para que Alembic pueda autogenerar las migraciones correctamente

# from .client import Client
# from .process import Process
# from .client_process import ClientProcess

# from .external_system import ExternalSystem
# from .credential import Credential
# from .credential_config import CredentialConfig

# from .process_run import ProcessRun
# from .process_run_log import ProcessRunLog

# TODO: tener en cuenta el caso de uso de un ORM diferente o cambios en la estructura de la base de datos
# from ..models import (
#     User,
#     Role,
#     AccessLog
# )

from .user import User
from .role import Role
from .user_roles import user_roles
