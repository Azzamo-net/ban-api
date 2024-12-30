from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Moderator
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_api_key(x_api_key: str = Header(...), admin_only: bool = False, db: Session = Depends(get_db)):
    admin_key = os.getenv("ADMIN_API_KEY")
    logging.info(f"Received x-api-key: {x_api_key}")
    logging.info(f"Expected ADMIN_API_KEY: {admin_key}")

    # Allow admin key for all endpoints
    if x_api_key == admin_key:
        logging.info("Admin key matched successfully.")
        return True

    # If the endpoint is admin-only and the key is not the admin key, deny access
    if admin_only:
        logging.warning("Admin-only access attempted with invalid key.")
        raise HTTPException(status_code=403, detail="Invalid API key for admin access")

    # Check if the key is a valid moderator key
    moderator = db.query(Moderator).filter(Moderator.private_key == x_api_key).first()
    if moderator:
        logging.info("Moderator key matched successfully.")
        return True

    logging.warning("Invalid API key provided.")
    raise HTTPException(status_code=403, detail="Invalid API key")

