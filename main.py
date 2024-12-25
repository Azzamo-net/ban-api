import os
from fastapi import FastAPI, HTTPException, Depends, Request, Body, Header
from sqlalchemy.orm import Session
import models, crud, schemas, database, utils
from database import engine, SessionLocal
from dotenv import load_dotenv
from dependencies import get_api_key
from rate_limit import RateLimitMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

load_dotenv()

app = FastAPI(title="Azzamo Banlist API")

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware, rate_limit=int(os.getenv("RATE_LIMIT", 100)))

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
    words = crud.get_blocked_words(db)
    return [{"id": word.id, "word": word.word, "timestamp": word.timestamp.isoformat()} for word in words]

@app.get("/blocked/ips", response_model=list[schemas.IPAddress], dependencies=[Depends(get_api_key)], summary="Get Blocked IPs", description="Retrieve a list of all blocked IP addresses.")
async def get_blocked_ips(db: Session = Depends(get_db)):
    return crud.get_blocked_ips(db)

@app.get("/blocked/pubkeys/status", summary="Check Public Key Status", description="Check if a public key is blocked and if it is temporarily banned.")
async def check_pubkey_status(pubkey: str, db: Session = Depends(get_db), api_key: str = Header(None)):
    status_info = crud.check_pubkey_status(db, pubkey)
    
    # If an API key is provided, include the moderator information
    if api_key:
        blocked_pubkey = db.query(models.PublicKey).filter(models.PublicKey.pubkey == pubkey).first()
        if blocked_pubkey and blocked_pubkey.moderator_name:
            status_info["moderator"] = blocked_pubkey.moderator_name
    
    return status_info

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
async def add_blacklisted_word(word_data: schemas.WordCreate, db: Session = Depends(get_db)):
    word = word_data.word
    return crud.add_blacklisted_word(db, word)

@app.delete("/blacklist/words", dependencies=[Depends(get_api_key)], summary="Remove Blacklisted Word", description="Remove a word or sentence from the blacklist.")
async def remove_blacklisted_word(word_data: dict = Body(...), db: Session = Depends(get_db)):
    word = word_data.get("word")
    if not word:
        raise HTTPException(status_code=400, detail="Word is required")
    return crud.remove_blacklisted_word(db, word)

@app.post("/blocked/ips", dependencies=[Depends(get_api_key)], summary="Add Blocked IP", description="Add a new IP address to the blocked list.")
async def add_blocked_ip(ip_data: dict = Body(...), db: Session = Depends(get_db)):
    ip = ip_data.get("ip")
    ban_reason = ip_data.get("ban_reason")
    if not ip:
        raise HTTPException(status_code=400, detail="IP address is required")
    return crud.add_blocked_ip(db, ip, ban_reason)

@app.delete("/blocked/ips", dependencies=[Depends(get_api_key)], summary="Remove Blocked IP", description="Remove an IP address from the blocked list.")
async def remove_blocked_ip(ip: str, db: Session = Depends(get_db)):
    return crud.remove_blocked_ip(db, ip)

@app.get("/public/blocked/words", summary="Get Public List of Blocked Words", description="Retrieve a public list of all blocked words.")
async def get_public_blocked_words(db: Session = Depends(get_db)):
    blocked_words = crud.get_blocked_words(db)
    return [word.word for word in blocked_words]

@app.post("/moderators", dependencies=[Depends(lambda: get_api_key(admin_only=True))], summary="Add Moderator")
async def add_moderator(moderator: schemas.ModeratorCreate, db: Session = Depends(get_db)):
    return crud.add_moderator(db, moderator.name, moderator.private_key)

@app.delete("/moderators", dependencies=[Depends(lambda: get_api_key(admin_only=True))], summary="Remove Moderator")
async def remove_moderator(moderator: schemas.ModeratorDelete, db: Session = Depends(get_db)):
    return crud.remove_moderator(db, moderator.name)

@app.get("/moderators", dependencies=[Depends(lambda: get_api_key(admin_only=True))], summary="List Moderators")
async def list_moderators(db: Session = Depends(get_db)):
    return crud.list_moderators(db)

@app.get("/search/blocked", dependencies=[Depends(get_api_key)], summary="Search Blocked Entities", description="Search for blocked public keys, IPs, or words.")
async def search_blocked_entities(entity_type: str, query: str, db: Session = Depends(get_db)):
    if entity_type not in ["pubkey", "ip", "word"]:
        raise HTTPException(status_code=400, detail="Invalid entity type")
    return crud.search_blocked_entities(db, entity_type, query)

@app.post("/bulk/blocked", dependencies=[Depends(get_api_key)], summary="Bulk Add Blocked Entities", description="Bulk add public keys, IPs, or words to the blocked list.")
async def bulk_add_blocked_entities(entity_type: str, entities: list[str], db: Session = Depends(get_db)):
    if entity_type not in ["pubkey", "ip", "word"]:
        raise HTTPException(status_code=400, detail="Invalid entity type")
    return crud.bulk_add_blocked_entities(db, entity_type, entities)

@app.delete("/bulk/blocked", dependencies=[Depends(get_api_key)], summary="Bulk Remove Blocked Entities", description="Bulk remove public keys, IPs, or words from the blocked list.")
async def bulk_remove_blocked_entities(entity_type: str, entities: list[str], db: Session = Depends(get_db)):
    if entity_type not in ["pubkey", "ip", "word"]:
        raise HTTPException(status_code=400, detail="Invalid entity type")
    return crud.bulk_remove_blocked_entities(db, entity_type, entities)

@app.get("/stats", dependencies=[Depends(get_api_key)], summary="Get Statistics", description="Get statistics on blocked entities.")
async def get_statistics(db: Session = Depends(get_db)):
    return crud.get_statistics(db)

@app.get("/temp-bans/expiring", dependencies=[Depends(get_api_key)], summary="Get Expiring Temporary Bans", description="Retrieve temporary bans expiring within a specified timeframe.")
async def get_expiring_temp_bans(hours: int, db: Session = Depends(get_db)):
    return crud.get_expiring_temp_bans(db, hours)

@app.patch("/moderators", dependencies=[Depends(lambda: get_api_key(admin_only=True))], summary="Update Moderator Information", description="Update the name or private key of an existing moderator.")
async def update_moderator_info(moderator: schemas.ModeratorUpdate, db: Session = Depends(get_db)):
    return crud.update_moderator_info(db, moderator.name, moderator.new_name, moderator.new_private_key)

@app.get("/audit-logs", dependencies=[Depends(get_api_key)], summary="Audit Logs", description="Retrieve logs of all actions performed by moderators.")
async def get_audit_logs(db: Session = Depends(get_db)):
    return crud.get_audit_logs(db)

@app.post("/reports", response_model=schemas.UserReport, summary="Create User Report", description="Report a public key with a reason.")
async def create_report(report: schemas.UserReportCreate, db: Session = Depends(get_db)):
    return crud.create_user_report(db, report)

@app.patch("/reports", dependencies=[Depends(get_api_key)], response_model=schemas.UserReport, summary="Update User Report", description="Update the status of a user report.")
async def update_report(report_update: schemas.UserReportUpdate, db: Session = Depends(get_db)):
    return crud.update_user_report(db, report_update)

@app.get("/reports/{pubkey}", response_model=list[schemas.UserReport], summary="Get User Reports", description="Retrieve reports for a specific public key.")
async def get_reports(pubkey: str, db: Session = Depends(get_db)):
    return crud.get_user_reports(db, pubkey)

@app.get("/recent-activity", dependencies=[Depends(lambda: get_api_key(admin_only=True))], response_model=list[schemas.AuditLog], summary="Get Recent Activity", description="Retrieve recent actions performed by moderators.")
async def recent_activity(db: Session = Depends(get_db)):
    return crud.get_recent_activity(db)

# Approve a reported user and ban them
@app.patch("/reports/approve/{report_id}", dependencies=[Depends(get_api_key)], response_model=schemas.UserReport, summary="Approve Report", description="Approve a report and ban the reported user.")
async def approve_report(report_id: int, db: Session = Depends(get_db), moderator_name: str = Header(...)):
    return crud.approve_report(db, report_id, moderator_name)

# Public endpoint to get pending reports
@app.get("/reports/pending", response_model=list[schemas.UserReport], summary="Get Pending Reports", description="Retrieve all pending user reports.")
async def get_pending_reports(db: Session = Depends(get_db)):
    return crud.get_pending_reports(db)

# Public endpoint to get all reports
@app.get("/reports/all", response_model=list[schemas.UserReport], summary="Get All Reports", description="Retrieve all user reports.")
async def get_all_reports(db: Session = Depends(get_db)):
    return crud.get_all_reports(db)

# Public endpoint to get successful reports
@app.get("/reports/successful", response_model=list[schemas.UserReport], summary="Get Successful Reports", description="Retrieve all successfully reported and banned users.")
async def get_successful_reports(db: Session = Depends(get_db)):
    return crud.get_successful_reports(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("APP_PORT", 8010))) 
