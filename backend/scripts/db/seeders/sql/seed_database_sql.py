# filepath: c:\Users\JaimeIvanDiazGaona\Documents\proyectos_jdiaz\tipsterByte_fx\backend\scripts\db\seeders\seed_database.py
import sys
from pathlib import Path
from loguru import logger

# Añadir la raíz del proyecto al sys.path para que encuentre los módulos
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from core.db.database_sql import get_db_context
from core.logger import configure_logging
# --- CORRECCIÓN CLAVE ---
# Importamos cada modelo desde su propio archivo dedicado.
from apps.auth.infrastructure.models.sql.role import Role
from apps.auth.infrastructure.models.sql.user import User

# --- CONFIGURACIÓN DE DATOS INICIALES ---
DEFAULT_ROLES = [
    {"name": "admin", "description": "Administrador con todos los permisos."},
    {"name": "user", "description": "Usuario estándar de la plataforma."},
    {"name": "guest", "description": "Usuario con permisos de solo lectura."},
]

ADMIN_USER = {
    "username": "admin",
    "email": "admin@tipsterbyte.com",
    "hashed_password": "$2b$12$EixZA2aeD3t/iA23dJkS3uYwYJ.g1G.t/v.g.gYwYJ.g1G.t/v.g.",
    "is_active": True
}

def seed_sql_data_auth_module():
    """
    Puebla la base de datos con datos iniciales (roles y usuario admin).
    Es idempotente: no duplicará datos si se ejecuta varias veces.
    """
    configure_logging()
    logger.info("🌱 Iniciando el proceso de seeder para la base de datos...")

    with get_db_context() as db:
        try:
            # --- 1. Poblar Roles ---
            logger.info("Verificando y poblando roles...")
            for role_data in DEFAULT_ROLES:
                role = db.query(Role).filter(Role.name == role_data["name"]).first()
                if not role:
                    new_role = Role(**role_data)
                    db.add(new_role)
                    logger.info(f"Rol '{role_data['name']}' creado.")
                else:
                    logger.trace(f"Rol '{role_data['name']}' ya existe, omitiendo.")
            
            db.commit()

            # --- 2. Poblar Usuario Administrador ---
            logger.info("Verificando y poblando usuario administrador...")
            admin_user = db.query(User).filter(User.username == ADMIN_USER["username"]).first()
            
            if not admin_user:
                admin_role = db.query(Role).filter(Role.name == "admin").first()
                if not admin_role:
                    logger.error("❌ No se encontró el rol 'admin'. No se puede crear el usuario administrador.")
                    return

                new_admin = User(
                    username=ADMIN_USER["username"],
                    email=ADMIN_USER["email"],
                    hashed_password=ADMIN_USER["hashed_password"],
                    is_active=ADMIN_USER["is_active"]
                )
                new_admin.roles.append(admin_role)
                
                db.add(new_admin)
                logger.info(f"Usuario administrador '{ADMIN_USER['username']}' creado y asignado al rol 'admin'.")
            else:
                logger.trace(f"Usuario administrador '{ADMIN_USER['username']}' ya existe, omitiendo.")

            logger.success("✅ Seeder completado exitosamente.")

        except Exception as e:
            logger.error(f"❌ Error durante el proceso de seeder: {e}")

if __name__ == "__main__":
    seed_sql_data_auth_module()