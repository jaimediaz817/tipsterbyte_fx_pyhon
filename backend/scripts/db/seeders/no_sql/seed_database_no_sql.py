import sys
import asyncio
from pathlib import Path

# Añadir la raíz del proyecto al sys.path
# project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
# if str(project_root) not in sys.path:
#     sys.path.append(str(project_root))

from core.enums.enums_process_status import ProcessStatus
from core.db.no_sql.database_no_sql import init_db_nosql
from apps.auth.infrastructure.models.mongo.access_log_model import AccessLog
from core.logger import configure_logging


async def seed_nosql_data_auth_module():
    configure_logging()
    await init_db_nosql()

    # Ejemplo de registros de acceso
    logs = [
        AccessLog(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            ip_address="192.168.1.10",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            process_name="user_login",
            process_status=ProcessStatus.COMPLETED
        ),
        AccessLog(
            user_id="123e4567-e89b-12d3-a456-426614174001",
            ip_address="10.0.0.5",
            user_agent="curl/7.68.0",
            process_name="data_fetch"
        ),
    ]

    for log in logs:
        await log.insert()
        print(f"Log insertado para user_id: {log.user_id}")

if __name__ == "__main__":
    asyncio.run(seed_nosql_data_auth_module())