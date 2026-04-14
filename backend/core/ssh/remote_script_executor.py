"""
✅ EJECUTOR REMOTO DE SCRIPTS SIN DEPENDENCIAS EN EL SERVIDOR
✅ NO NECESITA NADA INSTALADO EN EL OBJETIVO
✅ NO ESCRIBE NINGUN ARCHIVO EN EL SERVIDOR REMOTO
✅ TODO SE EJECUTA 100% EN MEMORIA

Funcionamiento:
1. Se conecta via SSH al servidor remoto
2. Inyecta TODO el codigo del script directamente en la sesion
3. Ejecuta el script completamente en memoria
4. Captura TODA la salida, stdout y stderr
5. Se desconecta sin dejar ningun rastro
"""

import paramiko
import io
from typing import Optional, Tuple
from dataclasses import dataclass
from loguru import logger


@dataclass(frozen=True)
class RemoteExecutionResult:
    """Resultado de ejecucion remota"""

    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time_seconds: float
    hostname: str


@dataclass(frozen=True)
class SSHConnectionConfig:
    """Configuracion de conexion SSH"""

    hostname: str
    port: int = 22
    username: str = "root"
    password: Optional[str] = None
    private_key_path: Optional[str] = None
    timeout: int = 30


class RemoteScriptExecutor:
    """
    Ejecutor universal de scripts bash en servidores remotos
    No requiere absolutamente nada instalado en el servidor objetivo
    """

    @staticmethod
    def execute_bash_script(
        config: SSHConnectionConfig, script_content: str
    ) -> RemoteExecutionResult:
        """
        Ejecuta un script bash REMOTAMENTE sin escribir ningun archivo

        Args:
            config: Configuracion de conexion SSH
            script_content: TODO el contenido del archivo .sh completo

        Returns:
            Resultado completo de la ejecucion
        """
        import time

        start_time = time.time()

        client = paramiko.SSHClient()

        try:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Conectar
            connect_kwargs = {
                "hostname": config.hostname,
                "port": config.port,
                "username": config.username,
                "timeout": config.timeout,
            }

            if config.password:
                connect_kwargs["password"] = config.password

            if config.private_key_path:
                connect_kwargs["key_filename"] = config.private_key_path

            client.connect(**connect_kwargs)
            logger.info(f"✅ Conectado exitosamente a {config.hostname}")

            # ✅ MAGIA AQUI: Inyectamos TODO el script directamente por stdin
            # No creamos archivos, no modificamos nada, todo se ejecuta en memoria
            transport = client.get_transport()

            if transport is None:
                raise ConnectionError(
                    "No se pudo obtener el transporte SSH, conexion invalida"
                )

            channel = transport.open_session()

            # Ejecutamos bash sin argumentos, le inyectamos el script completo
            channel.exec_command("bash -s")

            with channel.makefile("wb") as stdin:
                stdin.write(script_content.encode("utf-8"))

            # ✅ MUY IMPORTANTE: Cerramos el stdin para avisar a bash que ya terminamos de enviar el script
            # Sin esta linea se cuelga INFINITAMENTE esperando mas datos
            channel.shutdown_write()

            # Capturar salida
            stdout_buffer = io.BytesIO()
            stderr_buffer = io.BytesIO()

            with channel.makefile("rb") as stdout:
                stdout_buffer.write(stdout.read())

            with channel.makefile_stderr("rb") as stderr:
                stderr_buffer.write(stderr.read())

            exit_code = channel.recv_exit_status()
            success = exit_code == 0

            execution_time = round(time.time() - start_time, 2)

            logger.info(
                f"✅ Ejecucion completada en {config.hostname} | Codigo: {exit_code} | Tiempo: {execution_time}s"
            )

            return RemoteExecutionResult(
                success=success,
                exit_code=exit_code,
                stdout=stdout_buffer.getvalue().decode("utf-8", errors="replace"),
                stderr=stderr_buffer.getvalue().decode("utf-8", errors="replace"),
                execution_time_seconds=execution_time,
                hostname=config.hostname,
            )

        except Exception as e:
            execution_time = round(time.time() - start_time, 2)
            logger.error(f"❌ Error ejecutando en {config.hostname}: {str(e)}")

            return RemoteExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                execution_time_seconds=execution_time,
                hostname=config.hostname,
            )

        finally:
            client.close()
            logger.info(f"🔌 Conexion cerrada con {config.hostname}")
