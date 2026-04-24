"""
✅ Servidor Web Minimo para Dashboard del Agente
Levanta automaticamente en puerto 9999
Solo accesible desde localhost
Sin dependencias externas, usa solo http.server estandar
"""

import json
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from pathlib import Path
from loguru import logger


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "":
            self._servir_dashboard()
        elif self.path == "/api/estado":
            self._servir_estado_json()
        elif self.path.startswith("/api/aprobar/"):
            tarea_id = self.path.replace("/api/aprobar/", "")
            self._aprobar_cambio(tarea_id)
        elif self.path.startswith("/api/rechazar/"):
            tarea_id = self.path.replace("/api/rechazar/", "")
            self._rechazar_cambio(tarea_id)
        else:
            self.send_error(404)

    def _servir_dashboard(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Agente Supervisor</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <meta http-equiv="refresh" content="10">
</head>
<body class="bg-gray-900 text-white min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
        <header class="mb-8">
            <h1 class="text-3xl font-bold mb-2">🤖 Agente Supervisor</h1>
            <p class="text-gray-400">Tercer miembro del equipo - Monitoreo en tiempo real</p>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div class="bg-gray-800 rounded-lg p-4 border-l-4 border-green-500">
                <div class="text-gray-400 text-sm">Estado Agente</div>
                <div class="text-2xl font-bold text-green-500">✅ ACTIVO</div>
            </div>
            <div class="bg-gray-800 rounded-lg p-4 border-l-4 border-blue-500">
                <div class="text-gray-400 text-sm">Ciclos ejecutados</div>
                <div class="text-2xl font-bold">{{CICLOS}}</div>
            </div>
            <div class="bg-gray-800 rounded-lg p-4 border-l-4 border-yellow-500">
                <div class="text-gray-400 text-sm">Tareas pendientes</div>
                <div class="text-2xl font-bold">{{PENDIENTES}}</div>
            </div>
            <div class="bg-gray-800 rounded-lg p-4 border-l-4 border-emerald-500">
                <div class="text-gray-400 text-sm">Tareas completadas</div>
                <div class="text-2xl font-bold">{{COMPLETADAS}}</div>
            </div>
        </div>

        <div class="bg-gray-800 rounded-lg p-6 mb-8 border-2 border-orange-500">
            <h2 class="text-xl font-bold mb-4 text-orange-400">⏳ CAMBIOS PENDIENTES DE APROBACION</h2>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="border-b border-gray-700">
                            <th class="text-left py-3 px-2 text-gray-400">Documento</th>
                            <th class="text-left py-3 px-2 text-gray-400">Descripcion Cambio</th>
                            <th class="text-left py-3 px-2 text-gray-400">Estado</th>
                            <th class="text-left py-3 px-2 text-gray-400">Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {{CAMBIOS_PENDIENTES}}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="bg-gray-800 rounded-lg p-6 mb-8">
            <h2 class="text-xl font-bold mb-4">📋 Tablero de Tareas</h2>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="border-b border-gray-700">
                            <th class="text-left py-3 px-2 text-gray-400">ID</th>
                            <th class="text-left py-3 px-2 text-gray-400">Nombre</th>
                            <th class="text-left py-3 px-2 text-gray-400">Asignado</th>
                            <th class="text-left py-3 px-2 text-gray-400">Estado</th>
                            <th class="text-left py-3 px-2 text-gray-400">Actualizado</th>
                        </tr>
                    </thead>
                    <tbody>
                        {{FILAS_TABLA}}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="text-center text-gray-500 text-sm">
            Actualizado automaticamente cada 10 segundos
        </div>
    </div>
</body>
</html>
        """

        # Obtener datos actuales del agente
        from inspecciones_llm.agente_supervisor import agente_supervisor

        estado = agente_supervisor.obtener_tablero_estado()

        html = html.replace("{{CICLOS}}", str(estado["ciclos_ejecutados"]))
        html = html.replace(
            "{{PENDIENTES}}", str(estado["resumen_tareas"]["pendientes"])
        )
        html = html.replace(
            "{{COMPLETADAS}}", str(estado["resumen_tareas"]["completadas"])
        )

        filas = []
        cambios_pendientes = []

        for tarea in estado["tareas"].values():
            if tarea.estado.value == "⏳ ESPERA APROBACION":
                cambios_pendientes.append(
                    f"""
                <tr class="border-b border-orange-700/50 bg-orange-950/20">
                    <td class="py-3 px-2 font-mono text-sm">{tarea.id}</td>
                    <td class="py-3 px-2">{tarea.nombre}</td>
                    <td class="py-3 px-2 text-orange-400 font-bold">{tarea.estado.value}</td>
                    <td class="py-3 px-2">
                        <div class="flex gap-2">
                            <button onclick="location.href='/api/aprobar/{tarea.id}'" class="bg-green-600 hover:bg-green-500 px-3 py-1 rounded font-bold transition">✅ ACEPTAR</button>
                            <button onclick="location.href='/api/rechazar/{tarea.id}'" class="bg-red-600 hover:bg-red-500 px-3 py-1 rounded font-bold transition">❌ RECHAZAR</button>
                        </div>
                    </td>
                </tr>
                """
                )
            else:
                filas.append(
                    f"""
                <tr class="border-b border-gray-700/50">
                    <td class="py-3 px-2 font-mono text-sm">{tarea.id}</td>
                    <td class="py-3 px-2">{tarea.nombre}</td>
                    <td class="py-3 px-2 text-gray-400">{tarea.asignado_a}</td>
                    <td class="py-3 px-2">{tarea.estado.value}</td>
                    <td class="py-3 px-2 text-gray-500">{tarea.fecha_actualizacion.strftime('%d/%m %H:%M') if tarea.fecha_actualizacion else '-'}</td>
                </tr>
                """
                )

        html = html.replace("{{FILAS_TABLA}}", "\n".join(filas))

        if len(cambios_pendientes) > 0:
            html = html.replace("{{CAMBIOS_PENDIENTES}}", "\n".join(cambios_pendientes))
        else:
            html = html.replace(
                "{{CAMBIOS_PENDIENTES}}",
                '<tr><td colspan="4" class="py-4 text-center text-gray-500">✅ No hay cambios pendientes de aprobacion</td></tr>',
            )

        self.wfile.write(html.encode("utf-8"))

    def _servir_estado_json(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        from inspecciones_llm.agente_supervisor import agente_supervisor

        estado = agente_supervisor.obtener_tablero_estado()

        # Convertir a serializable
        estado_serializable = {
            **estado,
            "ultimo_latido": (
                estado["ultimo_latido"].isoformat() if estado["ultimo_latido"] else None
            ),
            "tareas": {
                k: {
                    **v.__dict__,
                    "fecha_creacion": v.fecha_creacion.isoformat(),
                    "fecha_actualizacion": (
                        v.fecha_actualizacion.isoformat()
                        if v.fecha_actualizacion
                        else None
                    ),
                    "estado": v.estado.value,
                }
                for k, v in estado["tareas"].items()
            },
        }

        self.wfile.write(json.dumps(estado_serializable, default=str).encode("utf-8"))

    def _aprobar_cambio(self, tarea_id: str) -> None:
        from inspecciones_llm.agente_supervisor import agente_supervisor, EstadoTarea

        agente_supervisor.actualizar_estado_tarea(
            tarea_id, EstadoTarea.COMPLETADA, "✅ Aprobado manualmente por usuario"
        )

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def _rechazar_cambio(self, tarea_id: str) -> None:
        from inspecciones_llm.agente_supervisor import agente_supervisor, EstadoTarea

        agente_supervisor.actualizar_estado_tarea(
            tarea_id, EstadoTarea.FALLIDA, "❌ Rechazado manualmente por usuario"
        )

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, format, *args):
        # Desactivar logs por defecto del servidor
        return


class DashboardServidor:
    def __init__(self, puerto: int = 9999):
        self.puerto = puerto
        self.servidor = None
        self.hilo = None
        self.corriendo = False

    def iniciar(self) -> None:
        """Inicia el servidor dashboard en hilo separado"""
        if self.corriendo:
            return

        try:
            self.servidor = HTTPServer(("127.0.0.1", self.puerto), DashboardHandler)
            self.hilo = Thread(target=self.servidor.serve_forever, daemon=True)
            self.hilo.start()
            self.corriendo = True

            logger.success(
                f"✅ Dashboard Agente Supervisor disponible en: http://localhost:{self.puerto}"
            )

        except Exception as e:
            logger.warning(f"⚠️  No se pudo levantar dashboard: {str(e)}")
            logger.info("ℹ️  El agente seguira funcionando sin interfaz web")

    def detener(self) -> None:
        """Detiene el servidor dashboard"""
        if not self.corriendo:
            return

        if self.servidor is not None:
            self.servidor.shutdown()

        if self.hilo is not None:
            from typing import cast
            from threading import Thread

            cast(Thread, self.hilo).join()

        self.corriendo = False
        logger.info("🛑 Dashboard detenido")


# ✅ Instancia global
dashboard = DashboardServidor()
