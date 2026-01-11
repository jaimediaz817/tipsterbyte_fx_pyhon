# from fastapi import APIRouter
# from fastapi import FastAPI
# from apps.auth.api.v1.authenticator_controller import router as auth_router

# # file: backend/apps/auth/api/v1/authenticator_controller.py

# # Controlador principal del módulo de autenticación (v1)
# # - Incluye las rutas definidas en authenticator_routes.py
# # - Expone además una ruta de test básica para health-check del controlador

# router = APIRouter()

# # Intento flexible de import para distintos layouts de proyecto
# _auth_routes_router = None
# try:
#     # Si authenticator_routes.py está en el mismo paquete
#     from .authenticator_routes import router as _auth_routes_router  # type: ignore
# except Exception:
#     try:
#         # Si está dentro de un sub-paquete "routes"
#         from .routes.authenticator_routes import router as _auth_routes_router  # type: ignore
#     except Exception:
#         _auth_routes_router = None

# # Incluir las rutas de autenticación si existen
# if _auth_routes_router is not None:
#     router.include_router(_auth_routes_router)

# # Ruta de test del controlador (útil para health-check del módulo completo)
# @router.get("/test", summary="Auth controller test")
# async def controller_test():
#     return {"status": "ok", "scope": "auth-controller", "version": "v1"}






from fastapi import APIRouter
from loguru import logger

# --- PASO 1: Importar las rutas existentes de forma directa ---
# Importamos el router que contiene la lógica de los endpoints (login, register, etc.)
# Asumimos que este archivo existe y contiene un objeto APIRouter llamado 'router'.
try:
    from .routes.authenticator_routes import router as endpoints_router
except ImportError:
    logger.error("No se pudo encontrar 'authenticator_routes.py' en la carpeta 'routes'. Asegúrate de que el archivo existe.")
    # Creamos un router vacío para evitar que la aplicación se rompa al iniciar.
    endpoints_router = APIRouter()


class AuthenticatorController:
    """
    Controlador basado en clases para el módulo de autenticación.
    
    Su responsabilidad es agrupar y exponer las rutas relacionadas con la autenticación.
    En esta versión, incluye las rutas definidas en un archivo separado.
    """
    def __init__(self):
        # El router principal de este controlador.
        self.router = APIRouter()
        
        # Registramos las rutas al instanciar la clase.
        self._register_routes()

    def _register_routes(self):
        """
        Registra los endpoints en el router de esta instancia.
        """
        # --- PASO 2: Incluir el router con la lógica de los endpoints ---
        # Aquí "absorbemos" todas las rutas (login, register) del otro archivo.
        self.router.include_router(endpoints_router)

        # También podemos añadir rutas específicas de este controlador si es necesario.
        self.router.get("/test", summary="Auth controller health check")(self.controller_test)

    async def controller_test(self):
        """
        Ruta de prueba para verificar que el controlador se ha cargado correctamente.
        """
        return {"status": "ok", "scope": "auth-controller-class", "version": "v1"}


# --- PASO 3: Crear una única instancia y exponer su router ---

# Creamos una instancia del controlador.
auth_controller = AuthenticatorController()

# Exponemos el router de la instancia para que pueda ser incluido en la app principal.
# Este es el único objeto que `main_init_web_server.py` necesita importar.
router = auth_controller.router