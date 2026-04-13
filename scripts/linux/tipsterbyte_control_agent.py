#!/usr/bin/env python3
# TipsterByte Control Agent - Standalone Linux Agent
# Compilable a binario standalone sin dependencias
from __future__ import annotations
import os
import sys
import json
import time
import socket
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class StatusColor(Enum):
    OK = "✅"
    WARNING = "🟡"
    ERROR = "🔴"
    INFO = "ℹ️"


@dataclass
class CheckResult:
    name: str
    status: StatusColor
    message: str
    duration: float = 0.0


class TipsterByteControlAgent:
    """Agente de Control Standalone para TipsterByte FX"""

    def __init__(self):
        self.start_time = time.time()
        self.results: List[CheckResult] = []
        self.env_config: Dict[str, str] = {}

        print("\n" + "=" * 70)
        print("🔷 TIPSTERBYTE FX - AGENTE DE CONTROL Y DIAGNOSTICO")
        print("🔷 Torre de Control - Health Check Standalone")
        print("🔷 Ejecutado:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 70 + "\n")

    def load_environment(self, env_path: Optional[str] = None) -> None:
        """Carga variables de entorno automaticamente"""
        possible_paths = [
            ".env",
            "../.env",
            "../../.env",
            "/opt/tipsterbyte/.env",
            env_path,
        ]

        found_env = None
        for path in possible_paths:
            if path and os.path.exists(path):
                found_env = path
                break

        if found_env:
            print(f"ℹ️  Archivo .env encontrado en: {found_env}")
            with open(found_env, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        self.env_config[key.strip()] = value.strip()
        else:
            print("⚠️  No se encontró archivo .env, usando valores por defecto")

    def check_postgresql_connection(self) -> CheckResult:
        """Verifica conexion a PostgreSQL"""
        start = time.time()
        db_url = self.env_config.get("DATABASE_URL", "")

        if not db_url:
            return CheckResult(
                name="PostgreSQL",
                status=StatusColor.WARNING,
                message="No hay DATABASE_URL configurada",
                duration=time.time() - start,
            )

        try:
            import psycopg2
            from urllib.parse import urlparse

            result = urlparse(db_url)
            conn = psycopg2.connect(
                host=result.hostname,
                port=result.port or 5432,
                user=result.username,
                password=result.password,
                database=result.path[1:],
                connect_timeout=5,
            )
            conn.close()

            return CheckResult(
                name="PostgreSQL",
                status=StatusColor.OK,
                message="Conexión exitosa",
                duration=time.time() - start,
            )

        except Exception as e:
            return CheckResult(
                name="PostgreSQL",
                status=StatusColor.ERROR,
                message=f"Error de conexión: {str(e)[:80]}",
                duration=time.time() - start,
            )

    def check_mongodb_connection(self) -> CheckResult:
        """Verifica conexion a MongoDB"""
        start = time.time()
        mongo_uri = self.env_config.get("MONGO_URI", "")

        if not mongo_uri:
            return CheckResult(
                name="MongoDB",
                status=StatusColor.WARNING,
                message="No hay MONGO_URI configurada",
                duration=time.time() - start,
            )

        try:
            from pymongo import MongoClient

            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")

            return CheckResult(
                name="MongoDB",
                status=StatusColor.OK,
                message="Conexión exitosa",
                duration=time.time() - start,
            )

        except Exception as e:
            return CheckResult(
                name="MongoDB",
                status=StatusColor.ERROR,
                message=f"Error de conexión: {str(e)[:80]}",
                duration=time.time() - start,
            )

    def check_network_connectivity(self) -> CheckResult:
        """Verifica conectividad a internet"""
        start = time.time()
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return CheckResult(
                name="Conectividad Internet",
                status=StatusColor.OK,
                message="Conexión a internet funcionando",
                duration=time.time() - start,
            )
        except Exception as e:
            return CheckResult(
                name="Conectividad Internet",
                status=StatusColor.ERROR,
                message=f"Sin conexión a internet: {str(e)}",
                duration=time.time() - start,
            )

    def check_system_resources(self) -> CheckResult:
        """Verifica recursos del sistema"""
        start = time.time()
        try:
            import psutil

            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            status = StatusColor.OK
            messages = []

            if cpu_usage > 80:
                status = StatusColor.WARNING
                messages.append(f"CPU Alto: {cpu_usage}%")
            if memory.percent > 85:
                status = StatusColor.WARNING
                messages.append(f"RAM Alta: {memory.percent}%")
            if disk.percent > 90:
                status = StatusColor.ERROR
                messages.append(f"Disco casi lleno: {disk.percent}%")

            if not messages:
                messages.append(
                    f"CPU: {cpu_usage}% | RAM: {memory.percent}% | Disco: {disk.percent}%"
                )

            return CheckResult(
                name="Recursos del Sistema",
                status=status,
                message=" | ".join(messages),
                duration=time.time() - start,
            )

        except Exception as e:
            return CheckResult(
                name="Recursos del Sistema",
                status=StatusColor.WARNING,
                message=f"No se pudo verificar: {str(e)}",
                duration=time.time() - start,
            )

    def run_all_checks(self) -> None:
        """Ejecuta todos los chequeos disponibles"""
        checks = [
            self.check_network_connectivity,
            self.check_postgresql_connection,
            self.check_mongodb_connection,
            self.check_system_resources,
        ]

        print("🔍 Ejecutando chequeos de salud...\n")

        for check_func in checks:
            result = check_func()
            self.results.append(result)

            status_icon = result.status.value
            duration = f"{result.duration:.2f}s"
            print(f"{status_icon} {result.name:<25} {result.message} [{duration}]")

        print("\n" + "=" * 70)

    def generate_final_report(self) -> None:
        """Genera informe final con resumen y recomendaciones"""
        total_checks = len(self.results)
        ok_count = sum(1 for r in self.results if r.status == StatusColor.OK)
        warning_count = sum(1 for r in self.results if r.status == StatusColor.WARNING)
        error_count = sum(1 for r in self.results if r.status == StatusColor.ERROR)

        print("\n📊 RESUMEN FINAL DE SALUD:")
        print(f"   ✅ Correctos: {ok_count}/{total_checks}")
        print(f"   🟡 Advertencias: {warning_count}/{total_checks}")
        print(f"   🔴 Errores: {error_count}/{total_checks}")
        print(f"   ⏱️  Tiempo total: {time.time() - self.start_time:.2f}s")
        print("\n" + "=" * 70)

        if error_count > 0:
            print("\n🚨 ACCIONES REQUERIDAS INMEDIATAMENTE:")
            for result in self.results:
                if result.status == StatusColor.ERROR:
                    print(f"   🔴 {result.name}: {result.message}")

        if warning_count > 0:
            print("\n⚠️  RECOMENDACIONES PENDIENTES:")
            for result in self.results:
                if result.status == StatusColor.WARNING:
                    print(f"   🟡 {result.name}: {result.message}")

        if error_count == 0 and warning_count == 0:
            print("\n✅ SISTEMA EN ESTADO ÓPTIMO - TODO FUNCIONANDO CORRECTAMENTE")

        print("\n" + "=" * 70)
        print("\n📋 COPIA TODO ESTE INFORME Y PEGALO EN CHAT PARA ANALISIS")
        print("\n")


def main():
    try:
        agent = TipsterByteControlAgent()
        agent.load_environment()
        agent.run_all_checks()
        agent.generate_final_report()

    except KeyboardInterrupt:
        print("\n\n⚠️  Ejecución cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error fatal en el agente: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
