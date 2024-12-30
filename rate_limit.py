from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import os

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit: int, ban_duration: int):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.ban_duration = ban_duration
        self.requests = {}
        self.banned_ips = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        # Check if the IP is banned
        if client_ip in self.banned_ips:
            ban_end_time = self.banned_ips[client_ip]
            if current_time < ban_end_time:
                return Response("IP banned due to excessive requests", status_code=403)
            else:
                del self.banned_ips[client_ip]  # Remove ban if time has passed

        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Clean up old requests
        self.requests[client_ip] = [timestamp for timestamp in self.requests[client_ip] if current_time - timestamp < 60]

        if len(self.requests[client_ip]) >= self.rate_limit:
            # Ban the IP
            self.banned_ips[client_ip] = current_time + self.ban_duration
            return Response("Too many requests, IP banned", status_code=429)

        self.requests[client_ip].append(current_time)
        response = await call_next(request)
        return response
