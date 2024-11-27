import os
from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.orm import Session
import models, crud, schemas, database, utils
from database import engine, SessionLocal
from dotenv import load_dotenv
from dependencies import get_api_key
from rate_limit import rate_limit
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

load_dotenv()

app = FastAPI(title="Azzamo Banlist API")

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Ensure the lists directory and files are present
utils.ensure_lists_directory_and_files()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Public Endpoints
@app.get("/blocked/pubkeys", response_model=list[schemas.PublicKey], summary="Get Blocked Public Keys", description="Retrieve a list of all blocked public keys.")
async def get_blocked_pubkeys(db: Session = Depends(get_db)):
    try:
        return crud.get_blocked_pubkeys(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/blocked/words", response_model=list[schemas.Word], summary="Get Blocked Words", description="Retrieve a list of all blocked words.")
async def get_blocked_words(db: Session = Depends(get_db)):
    return crud.get_blocked_words(db)

@app.get("/blocked/ips", response_model=list[schemas.IPAddress], summary="Get Blocked IPs", description="Retrieve a list of all blocked IP addresses.")
async def get_blocked_ips(db: Session = Depends(get_db)):
    return crud.get_blocked_ips(db)

@app.get("/blocked/pubkeys/status", summary="Check Public Key Status", description="Check if a public key is blocked and if it is temporarily banned.")
async def check_pubkey_status(pubkey: str, db: Session = Depends(get_db)):
    return crud.check_pubkey_status(db, pubkey)

# Administrative Endpoints
@app.post("/blocked/pubkeys", response_model=dict, dependencies=[Depends(get_api_key)], summary="Add Blocked Public Key", description="Add a new public key to the blocked list.")
async def add_blocked_pubkey(pubkey: schemas.PublicKeyCreate, db: Session = Depends(get_db)):
    return crud.add_blocked_pubkey(db, pubkey)

@app.delete("/blocked/pubkeys", dependencies=[Depends(get_api_key)], summary="Remove Blocked Public Key", description="Remove a public key from the blocked list.")
async def remove_blocked_pubkey(pubkey: schemas.PublicKeyCreate, db: Session = Depends(get_db)):
    crud.remove_blocked_pubkey(db, pubkey)
    return {"message": "Public key removed"}

# Temporary Ban Management
@app.post("/temp-ban/pubkeys", dependencies=[Depends(get_api_key)], summary="Temporarily Ban Public Key", description="Temporarily ban a public key for a specified duration.")
async def temp_ban_pubkey(pubkey: schemas.TempBanCreate, db: Session = Depends(get_db)):
    return crud.temp_ban_pubkey(db, pubkey)

@app.delete("/temp-ban/pubkeys", dependencies=[Depends(get_api_key)], summary="Remove Temporary Ban", description="Remove a temporary ban on a public key.")
async def remove_temp_ban(pubkey: schemas.PublicKeyCreate, db: Session = Depends(get_db)):
    crud.remove_temp_ban(db, pubkey)
    return {"message": "Temporary ban removed"}

# Export and Import
@app.get("/export/all", dependencies=[Depends(get_api_key)], summary="Export All Data", description="Export all blocked data to text files.")
async def export_all():
    utils.export_all()
    return {"message": "Data exported"}

@app.post("/import/all", dependencies=[Depends(get_api_key)], summary="Import All Data", description="Import all blocked data from text files.")
async def import_all():
    utils.import_all()
    return {"message": "Data imported"}

# Apply rate limiting to all endpoints
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    rate_limit(request)
    response = await call_next(request)
    return response

# Custom exception handler for HTTPException
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Custom exception handler for RequestValidationError
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# Custom exception handler for generic exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )

@app.patch("/blocked/pubkeys/ban-reason", dependencies=[Depends(get_api_key)], summary="Update Ban Reason", description="Update the ban reason for a public key.")
async def update_ban_reason(pubkey: str, reason: str, db: Session = Depends(get_db)):
    return crud.update_ban_reason(db, pubkey, reason)

@app.delete("/blocked/pubkeys/ban-reason", dependencies=[Depends(get_api_key)], summary="Remove Ban Reason", description="Remove the ban reason for a public key.")
async def remove_ban_reason(pubkey: str, db: Session = Depends(get_db)):
    return crud.remove_ban_reason(db, pubkey)

@app.get("/public/blocked/pubkeys", summary="Get Public List of Blocked Public Keys", description="Retrieve a public list of all blocked public keys.")
async def get_public_blocked_pubkeys(db: Session = Depends(get_db)):
    blocked_pubkeys = crud.get_blocked_pubkeys(db)
    return [pubkey.pubkey for pubkey in blocked_pubkeys]

@app.post("/blacklist/words", dependencies=[Depends(get_api_key)], summary="Add Blacklisted Word", description="Add a new word or sentence to the blacklist.")
async def add_blacklisted_word(word: str, db: Session = Depends(get_db)):
    return crud.add_blacklisted_word(db, word)

@app.delete("/blacklist/words", dependencies=[Depends(get_api_key)], summary="Remove Blacklisted Word", description="Remove a word or sentence from the blacklist.")
async def remove_blacklisted_word(word: str, db: Session = Depends(get_db)):
    return crud.remove_blacklisted_word(db, word)

@app.post("/blocked/ips", dependencies=[Depends(get_api_key)], summary="Add Blocked IP", description="Add a new IP address to the blocked list.")
async def add_blocked_ip(ip: str, ban_reason: str = None, db: Session = Depends(get_db)):
    return crud.add_blocked_ip(db, ip, ban_reason)

@app.delete("/blocked/ips", dependencies=[Depends(get_api_key)], summary="Remove Blocked IP", description="Remove an IP address from the blocked list.")
async def remove_blocked_ip(ip: str, db: Session = Depends(get_db)):
    return crud.remove_blocked_ip(db, ip)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("APP_PORT", 8010))) 