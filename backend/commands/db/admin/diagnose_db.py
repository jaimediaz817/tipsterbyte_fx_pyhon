"""
Comando de diagnóstico de base de datos.

Verifica la conexión a PostgreSQL y MongoDB, y muestra información
útil para debugging y despliegue.

Uso:
    python -m commands.db.admin.diagnose_db
"""

import asyncio
from loguru import logger
from sqlalchemy import text
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from core.db.sql.database_sql import SessionLocal, engine


async def diagnose_database():
    """Diagnóstico completo de bases de datos."""
    print("\n" + "=" * 80)
    print("🔍 DIAGNÓSTICO DE BASES DE DATOS")
    print("=" * 80)

    # =====================================================
    # 1. INFORMACIÓN DE CONFIGURACIÓN
    # =====================================================
    print("\n📋 CONFIGURACIÓN ACTUAL:")
    print(f"   🌍 Entorno: {settings.ENV}")
    print(f"   🐛 Debug: {settings.DEBUG}")
    print(f"   📧 Support: {settings.SUPPORT_EMAIL}")

    # =====================================================
    # 2. DIAGNÓSTICO POSTGRESQL
    # =====================================================
    print("\n" + "=" * 80)
    print("🐘 POSTGRESQL")
    print("=" * 80)

    print(f"\n   📊 Configuración:")
    print(f"      Host: {settings.POSTGRES_HOST}")
    print(f"      Port: {settings.POSTGRES_PORT}")
    print(f"      Database: {settings.POSTGRES_DB}")
    print(f"      User: {settings.POSTGRES_USER}")
    print(f"      Pool Size: {settings.DATABASE_POOL_SIZE}")
    print(f"      Max Overflow: {settings.DATABASE_MAX_OVERFLOW}")

    print(f"\n   🔗 URL de Conexión:")
    print(f"      {settings.DATABASE_URL}")

    # Verificar conexión
    try:
        with SessionLocal() as session:
            # Ejecutar query simple
            result = session.execute(text("SELECT version()"))
            version = result.scalar()

            # Obtener nombre de BD actual
            result = session.execute(text("SELECT current_database()"))
            current_db = result.scalar()

            # Obtener usuario actual
            result = session.execute(text("SELECT current_user"))
            current_user = result.scalar()

            # Obtener host de conexión
            result = session.execute(text("SELECT inet_server_addr()"))
            server_addr = result.scalar()

            print(f"\n   ✅ CONEXIÓN EXITOSA:")
            print(f"      Versión PostgreSQL: {version}")
            print(f"      Base de Datos Actual: {current_db}")
            print(f"      Usuario Conectado: {current_user}")
            print(f"      Servidor: {server_addr}")

            # Verificar tablas
            result = session.execute(
                text(
                    """
                    SELECT COUNT(*) as table_count 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """
                )
            )
            table_count = result.scalar()
            print(f"      Tablas en BD: {table_count}")

    except Exception as e:
        print(f"\n   ❌ ERROR DE CONEXIÓN:")
        print(f"      {str(e)}")
        print(f"\n   💡 SOLUCIONES:")
        print(f"      1. Verifica que PostgreSQL esté corriendo")
        print(f"      2. Verifica credenciales en .env")
        print(f"      3. Verifica que el puerto {settings.POSTGRES_PORT} esté abierto")
        print(f"      4. Verifica que la BD '{settings.POSTGRES_DB}' exista")

    # =====================================================
    # 3. DIAGNÓSTICO MONGODB
    # =====================================================
    print("\n" + "=" * 80)
    print("🍃 MONGODB")
    print("=" * 80)

    print(f"\n   📊 Configuración:")
    print(f"      Host: {settings.MONGO_HOST}")
    print(f"      Port: {settings.MONGO_PORT}")
    print(f"      Database: {settings.MONGO_DB}")
    print(f"      User: {settings.MONGO_USER}")

    print(f"\n   🔗 URI de Conexión:")
    print(f"      {settings.MONGO_URI}")

    # Verificar conexión MongoDB
    try:
        # Crear cliente MongoDB directamente
        client = AsyncIOMotorClient(settings.MONGO_URI)
        mongo_db = client[settings.MONGO_DB]

        # Obtener información del servidor
        server_info = await mongo_db.command("serverStatus")

        print(f"\n   ✅ CONEXIÓN EXITOSA:")
        print(f"      Versión MongoDB: {server_info.get('version', 'N/A')}")
        print(f"      Base de Datos Actual: {mongo_db.name}")
        print(
            f"      Conexiones Activas: {server_info.get('connections', {}).get('current', 'N/A')}"
        )

        # Verificar colecciones
        collections = await mongo_db.list_collection_names()
        print(f"      Colecciones: {len(collections)}")

        if collections:
            print(f"         - {', '.join(collections[:5])}")
            if len(collections) > 5:
                print(f"         ... y {len(collections) - 5} más")

    except Exception as e:
        print(f"\n   ❌ ERROR DE CONEXIÓN:")
        print(f"      {str(e)}")
        print(f"\n   💡 SOLUCIONES:")
        print(f"      1. Verifica que MongoDB esté corriendo")
        print(f"      2. Verifica credenciales en .env")
        print(f"      3. Verifica que el puerto {settings.MONGO_PORT} esté abierto")
        print(f"      4. Verifica que la BD '{settings.MONGO_DB}' exista")

    # =====================================================
    # 4. RESUMEN Y RECOMENDACIONES
    # =====================================================
    print("\n" + "=" * 80)
    print("📊 RESUMEN")
    print("=" * 80)

    print(f"\n   🎯 Entorno: {settings.ENV}")
    print(
        f"   🐘 PostgreSQL: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    print(
        f"   🍃 MongoDB: {settings.MONGO_HOST}:{settings.MONGO_PORT}/{settings.MONGO_DB}"
    )

    print(f"\n   💡 RECOMENDACIONES PARA PRODUCCIÓN:")
    print(f"      1. Cambiar ENV=production en .env")
    print(f"      2. Cambiar DEBUG=False en .env")
    print(f"      3. Usar credenciales fuertes (no postgres/postgres)")
    print(f"      4. Configurar backups automáticos")
    print(f"      5. Monitorear conexiones y rendimiento")

    print(f"\n   🚀 COMANDOS ÚTILES:")
    print(f"      - Verificar BD: python -m commands.db.admin.diagnose_db")
    print(f"      - Ejecutar seeders: python -m scripts.db.seeders.run_all_seeders")
    print(f"      - Ejecutar migraciones: alembic upgrade head")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(diagnose_database())
