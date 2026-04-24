#!/usr/bin/env python3
"""
✅ EJECUTOR FINAL LISTO PARA USAR
✅ NO NECESITAS MODIFICAR NADA
✅ SOLO EJECUTA ESTE ARCHIVO
✅ SE CONECTA AUTOMATICAMENTE A LA VPS PRINCIPAL
✅ USA LAS CREDENCIALES DEL CONFIG.PY
"""
import sys
from pathlib import Path

ROOT_PROYECTO = Path(__file__).resolve().parent
BACKEND_FOLDER = ROOT_PROYECTO / "backend"

# ✅ FIX PERMANENTE PATH: Agregamos AMBAS carpetas al sys.path
for ruta in [ROOT_PROYECTO, BACKEND_FOLDER]:
    if str(ruta) not in sys.path:
        sys.path.insert(0, str(ruta))

from dotenv import load_dotenv

load_dotenv(ROOT_PROYECTO / "backend" / ".env")

import asyncio

from backend.apps.platform_config.application.services.remote_vps_health_check_service import (
    RemoteVpsHealthCheckService,
)
from backend.apps.platform_config.application.dto.vps_health_check_response_dto import (
    VpsHealthCheckResponseDto,
)


async def ejecutar_completo():
    # ✅ INICIALIZAR CONEXION MONGODB PARA STANDALONE
    from backend.core.db.no_sql.schema_initializer import initialize_mongo_schema

    await initialize_mongo_schema()

    print("\n🚀 CONECTANDO AUTOMATICAMENTE A LA VPS PRINCIPAL...")
    print("✅ Usando credenciales del config.py")
    print("✅ Conexion MongoDB inicializada")
    print("=" * 80)

    # ✅ MAGIA: NO NECESITAS PASAR NINGUN PARAMETRO
    return await RemoteVpsHealthCheckService().execute_on_remote_vps()


# ✅ SOLUCION PERMANENTE Event Loop Closed en Windows
# ✅ USAMOS UN SOLO asyncio.run() PARA TODO EL FLUJO
resultado_entidad = asyncio.run(ejecutar_completo())

# ✅ Convertimos a DTO de respuesta para presentacion
# ✅ Funciona tanto con RemoteExecutionResult como con VpsHealthCheck
resultado = VpsHealthCheckResponseDto.from_any(resultado_entidad)
# ✅ Usamos el metodo integrado de impresion
resultado.print_console_summary()
