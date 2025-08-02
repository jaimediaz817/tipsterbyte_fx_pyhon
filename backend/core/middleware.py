import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger

class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id

        start_time = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            logger.exception(f"[TraceID: {trace_id}] Error en request: {request.url.path}")
            raise exc
        process_time = time.perf_counter() - start_time

        logger.info(f"📈 [TraceID: {trace_id}] {request.method} {request.url.path} completado en {process_time:.4f}s")
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"

        return response
