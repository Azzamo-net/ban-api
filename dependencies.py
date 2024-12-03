from fastapi import Header, HTTPException, status
import os

def get_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("ADMIN_API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
