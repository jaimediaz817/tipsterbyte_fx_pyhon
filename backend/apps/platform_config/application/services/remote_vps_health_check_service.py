"""
✅ SERVICIO DE EJECUCION REMOTA DEL VPS HEALTH CHECK
✅ NO NECESITAS NADA INSTALADO EN LA VPS OBJETIVO
✅ NO DEJAS NINGUN RASTRO NI ARCHIVO ESCRITO
✅ OBTIENES LA SALIDA COMPLETA DEL DIAGNOSTICO
"""

from pathlib import Path
from loguru import logger
from backend.core.config import settings
from backend.core.ssh.remote_script_executor import (
    RemoteScriptExecutor,
    SSHConnectionConfig,
    RemoteExecutionResult,
)


class RemoteVpsHealthCheckService:
    """
    Servicio para ejecutar el health check de VPS remotamente
    sin necesidad de copiar ningun archivo al servidor objetivo
    """

    # ✅ Cargamos el script una sola vez en memoria al iniciar el servicio
    # ✅ RUTA ABSOLUTA 100% FIABLE: Funciona desde CUALQUIER ubicacion
    _SCRIPT_PATH = (
        Path(__file__).resolve().parents[5]
        / "scripts"
        / "linux"
        / "vps_health_check.sh"
    )
    HEALTH_CHECK_SCRIPT = _SCRIPT_PATH.read_text(encoding="utf-8")

    @staticmethod
    async def execute_on_remote_vps(
        hostname: str | None = None,
        username: str | None = None,
        port: int | None = None,
        password: str | None = None,
        private_key_path: str | None = None,
    ) -> RemoteExecutionResult:
        """
        Ejecuta el health check COMPLETAMENTE en la VPS remota

        ✅ NO COPIA ARCHIVOS
        ✅ NO MODIFICA NADA
        ✅ TODO SE EJECUTA EN MEMORIA
        ✅ OBTIENES LA SALIDA EXACTA IGUAL QUE SI LO EJECUTARAS TU MANUALMENTE

        Args:
            hostname: IP o dominio de la VPS
            username: Usuario SSH (normalmente root)
            port: Puerto SSH (normalmente 22)
            password: Contraseña (si usas autenticacion por contraseña)
            private_key_path: Ruta a clave privada (si usas autenticacion por llave)

        Returns:
            Resultado completo con toda la salida del diagnostico
        """

        # ✅ Si no se pasan parametros usamos automaticamente la VPS principal del config
        target_host = hostname or settings.VPS_MAIN_HOST
        target_port = port or settings.VPS_MAIN_PORT
        target_user = username or settings.VPS_MAIN_USER
        target_pass = password or settings.VPS_MAIN_PASSWORD
        target_key = private_key_path or settings.VPS_MAIN_PRIVATE_KEY

        logger.info(f"🚀 Iniciando Health Check remoto en servidor: {target_host}")

        config = SSHConnectionConfig(
            hostname=target_host,
            port=target_port,
            username=target_user,
            password=target_pass,
            private_key_path=target_key,
        )

        # ✅ Aqui sucede la magia: enviamos TODO el script por SSH directamente a bash
        resultado = RemoteScriptExecutor.execute_bash_script(
            config=config,
            script_content=RemoteVpsHealthCheckService.HEALTH_CHECK_SCRIPT,
        )

        if resultado.success:
            logger.info(f"✅ Health Check ejecutado correctamente en {hostname}")
            logger.info(
                f"⏱️  Tiempo de ejecucion: {resultado.execution_time_seconds} segundos"
            )
        else:
            logger.error(
                f"❌ Fallo Health Check en {hostname} | Codigo: {resultado.exit_code}"
            )

        # ✅ Guardar SIEMPRE el resultado en MongoDB sin importar si fue exitoso o no
        try:
            from backend.apps.platform_config.infrastructure.repositories.mongo_vps_health_check_repository import (
                MongoVpsHealthCheckRepository,
            )
            from backend.apps.platform_config.domain.entities.vps_health_check import (
                VpsHealthCheck,
            )

            logger.info("💾 Intentando guardar registro en MongoDB...")

            # ✅ Convertimos resultado de ejecucion a entidad de dominio
            health_check_entity = VpsHealthCheck.create(
                hostname=target_host,
                success=resultado.success,
                exit_code=resultado.exit_code,
                stdout=resultado.stdout,
                stderr=resultado.stderr,
                execution_time_seconds=resultado.execution_time_seconds,
            )

            repository = MongoVpsHealthCheckRepository()
            await repository.save(health_check_entity)

            logger.success("✅ Registro guardado CORRECTAMENTE en MongoDB")

        except Exception as e:
            logger.error("❌ ❌ ❌ FALLO AL GUARDAR EN MONGODB ❌ ❌ ❌")
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Mensaje: {str(e)}")
            import traceback

            logger.error(f"Stacktrace completo: {traceback.format_exc()}")
            logger.warning(
                "⚠️  El Health Check se ejecutó pero NO SE GUARDÓ el historial"
            )

        return resultado
