"""
Repositorio para operaciones de usuarios en PostgreSQL.
"""

from typing import Optional
from uuid import UUID
from loguru import logger

from apps.auth.infrastructure.models.sql.user import User
from core.db.sql.database_sql import get_db_session, get_db_context


class UserRepository:
    """
    Repositorio para gestionar operaciones CRUD de usuarios en PostgreSQL.

    Principios aplicados:
    - SRP: Solo operaciones de persistencia de usuarios
    - Repository Pattern: Abstrae la capa de acceso a datos
    """

    async def create(self, user: User) -> User:
        """
        Crea un nuevo usuario en la base de datos.

        Args:
            user: Instancia de User a crear

        Returns:
            User creado con ID asignado

        Raises:
            Exception: Error al crear usuario en BD
        """
        try:
            with get_db_context() as db:
                db.add(user)
                db.flush()  # Para obtener el ID generado
                db.refresh(user)
                logger.info(
                    f"✅ Usuario creado exitosamente: {user.username} (ID: {user.id})"
                )
                return user
        except Exception as e:
            logger.error(f"❌ Error al crear usuario: {e}")
            raise

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Obtiene un usuario por su email.

        Args:
            email: Email del usuario

        Returns:
            User si existe, None en caso contrario
        """
        try:
            with get_db_context() as db:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    logger.debug(f"✅ Usuario encontrado por email: {email}")
                else:
                    logger.debug(f"ℹ️ No se encontró usuario con email: {email}")
                return user
        except Exception as e:
            logger.error(f"❌ Error al buscar usuario por email: {e}")
            raise

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Obtiene un usuario por su username.

        Args:
            username: Nombre de usuario

        Returns:
            User si existe, None en caso contrario
        """
        try:
            with get_db_context() as db:
                user = db.query(User).filter(User.username == username).first()
                if user:
                    logger.debug(f"✅ Usuario encontrado por username: {username}")
                else:
                    logger.debug(f"ℹ️ No se encontró usuario con username: {username}")
                return user
        except Exception as e:
            logger.error(f"❌ Error al buscar usuario por username: {e}")
            raise

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Obtiene un usuario por su ID.

        Args:
            user_id: ID del usuario

        Returns:
            User si existe, None en caso contrario
        """
        try:
            with get_db_context() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    logger.debug(f"✅ Usuario encontrado por ID: {user_id}")
                else:
                    logger.debug(f"ℹ️ No se encontró usuario con ID: {user_id}")
                return user
        except Exception as e:
            logger.error(f"❌ Error al buscar usuario por ID: {e}")
            raise

    async def update(self, user: User) -> User:
        """
        Actualiza un usuario existente.

        Args:
            user: Instancia de User con datos actualizados

        Returns:
            User actualizado
        """
        try:
            with get_db_context() as db:
                db.merge(user)
                db.refresh(user)
                logger.info(
                    f"✅ Usuario actualizado exitosamente: {user.username} (ID: {user.id})"
                )
                return user
        except Exception as e:
            logger.error(f"❌ Error al actualizar usuario: {e}")
            raise

    async def delete(self, user_id: int) -> bool:
        """
        Elimina un usuario por su ID.

        Args:
            user_id: ID del usuario a eliminar

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            with get_db_context() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    db.delete(user)
                    logger.info(f"✅ Usuario eliminado exitosamente: ID {user_id}")
                    return True
                else:
                    logger.warning(
                        f"⚠️ No se encontró usuario con ID {user_id} para eliminar"
                    )
                    return False
        except Exception as e:
            logger.error(f"❌ Error al eliminar usuario: {e}")
            raise

    async def get_all_active(self, limit: int = 100, offset: int = 0) -> list[User]:
        """
        Obtiene todos los usuarios activos con paginación.

        Args:
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Lista de usuarios activos
        """
        try:
            with get_db_context() as db:
                users = (
                    db.query(User)
                    .filter(User.is_active == True)
                    .offset(offset)
                    .limit(limit)
                    .all()
                )
                logger.debug(f"✅ Obtenidos {len(users)} usuarios activos")
                return users
        except Exception as e:
            logger.error(f"❌ Error al obtener usuarios activos: {e}")
            raise
