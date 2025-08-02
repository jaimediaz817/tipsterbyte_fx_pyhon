from datetime import datetime, timezone
import psutil
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

# Registrar tiempo de inicio
START_TIME = datetime.now(timezone.utc)


@router.get("/health", tags=["System"])
def health_check():
    return JSONResponse(content={"status": "ok"})


@router.get("/status", tags=["System"])
def status_check():
    uptime = datetime.now(timezone.utc) - START_TIME
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.5)

    return JSONResponse(content={
        "uptime_seconds": int(uptime.total_seconds()),
        "memory_percent": mem.percent,
        "cpu_percent": cpu
    })
