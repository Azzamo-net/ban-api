from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit: int):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        if client_ip not in self.requests:
            self.requests[client_ip] = []

        self.requests[client_ip] = [timestamp for timestamp in self.requests[client_ip] if current_time - timestamp < 60]

        if len(self.requests[client_ip]) >= self.rate_limit:
            return Response("Too many requests", status_code=429)

        self.requests[client_ip].append(current_time)
        response = await call_next(request)
        return response
