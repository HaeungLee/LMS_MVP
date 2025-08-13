import json
import time
from typing import Optional
from starlette.types import ASGIApp, Receive, Scope, Send


class StructuredLoggingMiddleware:
    """Logs basic request/response info in structured JSON with request_id support."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started = time.time()
        method = scope.get("method")
        path = scope.get("path")
        client = scope.get("client")
        ip = client[0] if client else None
        state = scope.setdefault("state", {})
        request_id: Optional[str] = state.get("request_id")
        status_code_holder = {"value": None}

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code_holder["value"] = message.get("status")
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = int((time.time() - started) * 1000)
            log = {
                "level": "info",
                "message": "http_request",
                "request_id": request_id,
                "method": method,
                "path": path,
                "status": status_code_holder["value"],
                "duration_ms": duration_ms,
                "ip": ip,
            }
            print(json.dumps(log, ensure_ascii=False))


