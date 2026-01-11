from fastapi import APIRouter, status

router = APIRouter()

@router.get(
    "/ping",
    status_code=status.HTTP_200_OK,
    summary="Ruta de prueba del subsistema de autenticación",
)
async def auth_ping():
    return {"ok": True, "service": "auth", "message": "pong"}