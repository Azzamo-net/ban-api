from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from collections import defaultdict
import os

RATE_LIMIT = int(os.getenv("RATE_LIMIT", 100))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 300))
RATE_LIMIT_BAN_DURATION = int(os.getenv("RATE_LIMIT_BAN_DURATION", 1260))

# Store request counts and ban info
request_counts = defaultdict(lambda: {"count": 0, "reset_time": datetime.utcnow()})
banned_ips = {}

def rate_limit(request: Request):
    client_ip = request.client.host
    current_time = datetime.utcnow()

    # Check if IP is banned
    if client_ip in banned_ips:
        ban_end_time = banned_ips[client_ip]
        if current_time < ban_end_time:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests, you are banned temporarily.",
            )
        else:
            del banned_ips[client_ip]  # Remove ban if time has passed

    # Check request count
    if current_time > request_counts[client_ip]["reset_time"]:
        # Reset count if window has passed
        request_counts[client_ip] = {"count": 1, "reset_time": current_time + timedelta(seconds=RATE_LIMIT_WINDOW)}
    else:
        request_counts[client_ip]["count"] += 1

    if request_counts[client_ip]["count"] > RATE_LIMIT:
        # Ban the IP
        banned_ips[client_ip] = current_time + timedelta(seconds=RATE_LIMIT_BAN_DURATION)
        del request_counts[client_ip]  # Reset request count
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests, you are banned temporarily.",
        )
