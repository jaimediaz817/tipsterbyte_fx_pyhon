# from apps.auth.infrastructure.models.sql.role import Role
# from apps.auth.infrastructure.models.sql.user import User
# from ..base_seeder import BaseSeeder
from apps.auth.infrastructure.models.sql.role import Role
from apps.auth.infrastructure.models.sql.user import User
# from scripts.db.seeders.seeder_utils import update_from_dict
from shared.utils.db.sql.sqlalchemy_utils import update_from_dict
from scripts.db.seeders.base_seeder import BaseSeeder
# from scripts.db.seeders.sql.base_seeder import BaseSeeder


# --- CONFIGURACIÓN DE DATOS INICIALES ---
DEFAULT_ROLES = [
    {"name": "admin", "description": "Administrador con todos los permisos. 817"},
    {"name": "user", "description": "Usuario estándar de la plataforma. 817"},
    {"name": "guest", "description": "Usuario con permisos de solo lectura. 817"},
    {"name": "invitado", "description": "Usuario con permisos de solo lectura/invitado. 817"},
]

ADMIN_USER = {
    "username": "admin",
    "email": "admin@tipsterbyte.com",
    "hashed_password": "$2b$12$EixZA2aeD3t/iA23dJkS3uYwYJ.g1G.t/v.g.gYwYJ.g1G.t/v.g.",
    "is_active": True
}

class AuthSeeder(BaseSeeder):
    """Puebla la base de datos con datos iniciales para el módulo de autenticación."""

    def run(self,  update: bool = False):
        self.logger.info("🌱 Ejecutando seeder del módulo de autenticación...")
        try:
            self._seed_roles(update=update)
            
            # Forzamos a la sesión a ejecutar los INSERTs de los roles en la BD.
            # Ahora los roles existen en la base de datos para la siguiente consulta.
            self.logger.info("Sincronizando roles con la base de datos...")
            self.db.flush()            
            
            self._seed_admin_user(update=update)
            self.db.commit()
            self.logger.success("✅ Seeder de autenticación completado exitosamente.")
        except Exception as e:
            self.logger.error(f"❌ Error durante el seeder de autenticación: {e}")
            self.db.rollback()
            raise

    def _seed_roles(self, update=False):
        self.logger.info("Verificando y poblando roles...")
        for role_data in DEFAULT_ROLES:
            print(">>>>>>>>>>>>>> Role.name : " + Role.name)
            role = self.db.query(Role).filter(Role.name == role_data["name"]).first()
            if not role:
                new_role = Role(**role_data)
                self.db.add(new_role)
                self.logger.info(f"Rol '{role_data['name']}' creado.")
            # --- ¡LÓGICA DE ACTUALIZACIÓN SIMPLIFICADA! ---
            elif update:
                self.logger.info(f"Actualizando rol '{role_data['name']}'...")
                update_from_dict(role, role_data)                
            else:
                self.logger.trace(f"Rol '{role_data['name']}' ya existe, omitiendo.")

    def _seed_admin_user(self, update=False):
        self.logger.info("Verificando y poblando usuario administrador...")
        admin_user = self.db.query(User).filter(User.username == ADMIN_USER["username"]).first()
        
        if not admin_user:
            admin_role = self.db.query(Role).filter(Role.name == "admin").first()
            if not admin_role:
                self.logger.error("No se encontró el rol 'admin'. No se puede crear el usuario administrador.")
                return

            new_admin = User(
                username=ADMIN_USER["username"],
                email=ADMIN_USER["email"],
                hashed_password=ADMIN_USER["hashed_password"],
                is_active=ADMIN_USER["is_active"]
            )
            new_admin.roles.append(admin_role)
            
            self.db.add(new_admin)
            self.logger.info(f"Usuario administrador '{ADMIN_USER['username']}' creado y asignado al rol 'admin'.")

        # --- ¡LÓGICA DE ACTUALIZACIÓN! ---
        elif update:
            self.logger.info(f"Actualizando usuario administrador '{ADMIN_USER['username']}'...")
            update_from_dict(admin_user, ADMIN_USER)
                        
        else:
            self.logger.trace(f"Usuario administrador '{ADMIN_USER['username']}' ya existe, omitiendo.")