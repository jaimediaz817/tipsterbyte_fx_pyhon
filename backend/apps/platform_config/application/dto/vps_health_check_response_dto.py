"""
✅ DTO DE RESPUESTA PARA VPS HEALTH CHECK
✅ Usado para presentar resultados al usuario final
✅ Formato amigable para CLI y API
✅ Incluye metodos helpers para impresion
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class VpsHealthCheckResponseDto:
    """
    DTO de respuesta para resultados de Health Check de VPS.

    ✅ Esta clase es la interfaz publica para mostrar resultados
    ✅ No contiene logica de dominio, solo presentacion
    ✅ Incluye metodos convenientes para impresion en consola
    """

    id: UUID
    hostname: str
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time_seconds: float
    executed_at: datetime
    created_at: datetime

    # ✅ METRICAS PARSEADAS
    ram_total_mb: Optional[int] = None
    ram_used_mb: Optional[int] = None
    ram_usage_percent: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    disk_total_gb: Optional[float] = None
    disk_used_gb: Optional[float] = None
    disk_usage_percent: Optional[float] = None
    load_1min: Optional[float] = None
    load_5min: Optional[float] = None
    load_15min: Optional[float] = None
    process_count: Optional[int] = None
    uptime_seconds: Optional[int] = None

    # ✅ UNIDADES DE MEDIDA ORIGINALES DETECTADAS
    ram_total_unit: Optional[str] = None
    ram_used_unit: Optional[str] = None
    disk_total_unit: Optional[str] = None
    disk_used_unit: Optional[str] = None

    @classmethod
    def from_any(cls, result) -> "VpsHealthCheckResponseDto":
        """
        ✅ Metodo universal: acepta CUALQUIER objeto de resultado
        Funciona tanto con:
         - VpsHealthCheck (entidad de dominio)
         - RemoteExecutionResult (resultado directo del ejecutor)
        """
        from datetime import datetime
        from uuid import uuid4

        # Valores por defecto para objetos que no tienen estos campos
        default_id = uuid4()
        default_date = datetime.utcnow()

        return cls(
            id=getattr(result, "id", default_id),
            hostname=result.hostname,
            success=result.success,
            exit_code=result.exit_code,
            stdout=result.stdout,
            stderr=result.stderr,
            execution_time_seconds=result.execution_time_seconds,
            executed_at=getattr(result, "executed_at", default_date),
            created_at=getattr(result, "created_at", default_date),
            # ✅ METRICAS PARSEADAS
            ram_total_mb=getattr(result, "ram_total_mb", None),
            ram_used_mb=getattr(result, "ram_used_mb", None),
            ram_usage_percent=getattr(result, "ram_usage_percent", None),
            cpu_usage_percent=getattr(result, "cpu_usage_percent", None),
            disk_total_gb=getattr(result, "disk_total_gb", None),
            disk_used_gb=getattr(result, "disk_used_gb", None),
            disk_usage_percent=getattr(result, "disk_usage_percent", None),
            load_1min=getattr(result, "load_1min", None),
            load_5min=getattr(result, "load_5min", None),
            load_15min=getattr(result, "load_15min", None),
            process_count=getattr(result, "process_count", None),
            uptime_seconds=getattr(result, "uptime_seconds", None),
            # ✅ UNIDADES DE MEDIDA
            ram_total_unit=getattr(result, "ram_total_unit", None),
            ram_used_unit=getattr(result, "ram_used_unit", None),
            disk_total_unit=getattr(result, "disk_total_unit", None),
            disk_used_unit=getattr(result, "disk_used_unit", None),
        )

    @classmethod
    def from_domain_entity(cls, entity) -> "VpsHealthCheckResponseDto":
        """
        Crea un DTO desde la entidad de dominio VpsHealthCheck
        """
        return cls.from_any(entity)

    def print_console_summary(self) -> None:
        """
        Imprime un resumen formateado bonito para consola
        ✅ Compatible directamente con el script ejecutor
        """
        print("\n✅ EJECUCION COMPLETADA!")
        print("=" * 80)
        print(f"✅ Exito: {self.success}")
        print(f"✅ Codigo salida: {self.exit_code}")
        print(f"✅ Tiempo ejecucion: {self.execution_time_seconds} segundos")
        print(f"✅ Servidor: {self.hostname}")
        print("=" * 80)

        if self.success:
            print("\n📋 SALIDA COMPLETA DEL DIAGNOSTICO:\n")
            print(self.stdout)
        else:
            print("\n❌ FALLO LA EJECUCION:")
            print(self.stderr)

        # ✅ MEJORA EXPERIENCIA USUARIO: VERIFICAR COLECCIONES PENDIENTES
        print("\n" + "=" * 80)
        print("🔍 VERIFICANDO ESTADO DE COLECCIONES MONGODB...")
        print("=" * 80)

        try:
            import asyncio
            from motor.motor_asyncio import AsyncIOMotorClient
            from core.config import settings
            from core.db.no_sql.schema_initializer import _find_beanie_models, _get_collection_name

            # Buscar todos los modelos definidos
            modelos = _find_beanie_models()
            
            # Conectar a MongoDB para verificar existencia
            client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
            db = client.get_database(settings.MONGO_DB)
            
            async def verificar():
                colecciones_existentes = await db.list_collection_names()
                pendientes = []
                
                print(f"\n{'#':<3} {'MODELO':<30} {'COLECCION':<30} {'ESTADO':<10}")
                print(f"{'-'*3} {'-'*30} {'-'*30} {'-'*10}")

                for idx, modelo in enumerate(modelos, 1):
                    nombre_coleccion = _get_collection_name(modelo)
                    existe = nombre_coleccion in colecciones_existentes
                    
                    estado = "✅ OK" if existe else "❌ PENDIENTE"
                    print(f"{idx:<3} {modelo.__name__:<30} {nombre_coleccion:<30} {estado:<10}")
                    
                    if not existe:
                        pendientes.append(modelo.__name__)
                
                return pendientes

            pendientes = asyncio.run(verificar())
            client.close()

            if pendientes:
                print("\n" + "!" * 80)
                print(f"⚠️  TIO! TIENES {len(pendientes)} MODELOS PENDIENTES POR MIGRAR:")
                print("!" * 80)
                
                for modelo in pendientes:
                    print(f"   🔴 {modelo}")
                
                print("\n💡 SOLUCION EN 1 COMANDO:")
                print("\n   python manage.py nosql init-schema")
                print("\n✅ Este comando CREA AUTOMATICAMENTE todas las colecciones faltantes sin borrar nada")
                print("=" * 80)
            else:
                print("\n✅ TODAS LAS COLECCIONES ESTAN CORRECTAMENTE INICIALIZADAS")
                print(f"   Total modelos verificados: {len(modelos)}")

        except Exception as e:
            print(f"\n⚠️  No se pudo verificar estado de colecciones: {e}")
            print("\n🔧 Si tienes errores de colecciones faltantes ejecuta:")
            print("\n   python manage.py nosql init-schema")

        print("\n" + "=" * 80)
        print("✅ FINALIZADO")

    def get_status_icon(self) -> str:
        """Retorna icono representando el estado"""
        return "✅" if self.success else "❌"

    def get_status_text(self) -> str:
        """Retorna texto descriptivo del estado"""
        return "OK" if self.success else "FALLIDO"

    def __str__(self) -> str:
        return f"[{self.id}] {self.hostname} | {self.get_status_icon()} {self.get_status_text()} | {self.execution_time_seconds}s"
