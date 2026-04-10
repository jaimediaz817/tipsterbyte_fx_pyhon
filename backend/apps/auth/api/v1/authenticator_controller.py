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


"""
Controlador principal del módulo de autenticación (v1)
Re-exporta las rutas definidas en authenticator_routes.py
"""

from fastapi import APIRouter

# Re-exportar el router de authenticator_routes directamente
from .routes.authenticator_routes import router


# Agregar ruta de health check del controlador
@router.get("/test", summary="Auth controller health check")
async def controller_test():
    """Verifica que el controlador de autenticación está funcionando."""
    return {"status": "ok", "scope": "auth-controller", "version": "v1"}
