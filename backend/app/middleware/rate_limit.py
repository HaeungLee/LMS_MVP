import time
import typing as t
from collections import deque, defaultdict
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import JSONResponse


class RateLimitMiddleware:
    """Simple in-memory sliding window rate limiter per IP+route.

    limits: dict[str, tuple[int,int]] maps route prefix to (max_requests, window_seconds)
    Example: {"/api/v1/auth/login": (10, 60)}
    """

    def __init__(self, app: ASGIApp, limits: dict[str, tuple[int, int]] | None = None):
        self.app = app
        self.limits = limits or {}
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def _match_limit(self, path: str) -> tuple[int, int] | None:
        # longest prefix match
        candidates = [p for p in self.limits.keys() if path.startswith(p)]
        if not candidates:
            return None
        prefix = max(candidates, key=len)
        return self.limits[prefix]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        limit = self._match_limit(path)
        if not limit:
            await self.app(scope, receive, send)
            return

        max_req, window = limit
        client = scope.get("client")
        ip = client[0] if client else "anonymous"
        key = f"{ip}:{path}"

        now = time.time()
        q = self._buckets[key]
        # purge old
        while q and (now - q[0]) > window:
            q.popleft()
        if len(q) >= max_req:
            # Too many requests
            resp = JSONResponse({"detail": "Too many requests"}, status_code=429)
            await resp(scope, receive, send)
            return
        q.append(now)
        await self.app(scope, receive, send)


