from database import SessionLocal
from models import PublicKey, TempBan, Word, IPAddress, Moderator, AuditLog
from schemas import PublicKeyCreate, TempBanCreate
from datetime import datetime, timedelta
from pynostr.key import PublicKey as NostrPublicKey
from fastapi import HTTPException

def convert_npub_to_hex(npub: str) -> str:
    # Convert Npub to hex using pynostr
    public_key = NostrPublicKey.from_npub(npub)
    return public_key.hex()

def get_blocked_pubkeys(db: SessionLocal):
    return db.query(PublicKey).all()

def add_blocked_pubkey(db: SessionLocal, pubkey: PublicKeyCreate):
    # Check if the pubkey is in Npub format and convert it
    if pubkey.pubkey.startswith("npub"):
        hex_pubkey = convert_npub_to_hex(pubkey.pubkey)
    else:
        hex_pubkey = pubkey.pubkey

    # Check if the public key already exists
    existing_pubkey = db.query(PublicKey).filter(PublicKey.pubkey == hex_pubkey).first()
    if existing_pubkey:
        if not existing_pubkey.ban_reason and pubkey.ban_reason:
            existing_pubkey.ban_reason = pubkey.ban_reason
            db.commit()
            db.refresh(existing_pubkey)
        return {
            "message": "Public key already blocked",
            "status": "already_blocked",
            "pubkey": existing_pubkey.pubkey,
            "npub": existing_pubkey.npub,
            "ban_reason": existing_pubkey.ban_reason
        }

    db_pubkey = PublicKey(pubkey=hex_pubkey, npub=pubkey.pubkey, timestamp=datetime.utcnow(), ban_reason=pubkey.ban_reason)
    db.add(db_pubkey)
    db.commit()
    db.refresh(db_pubkey)
    return {
        "message": "Public key successfully blocked",
        "status": "blocked",
        "pubkey": db_pubkey.pubkey,
        "npub": db_pubkey.npub,
        "ban_reason": db_pubkey.ban_reason
    }

def remove_blocked_pubkey(db: SessionLocal, pubkey: PublicKeyCreate):
    db_pubkey = db.query(PublicKey).filter(PublicKey.pubkey == pubkey.pubkey).first()
    if db_pubkey:
        db.delete(db_pubkey)
        db.commit()

def temp_ban_pubkey(db: SessionLocal, pubkey: TempBanCreate):
    expiry = datetime.utcnow() + timedelta(hours=pubkey.duration)
    db_temp_ban = TempBan(pubkey=pubkey.pubkey, expiry_timestamp=expiry)
    db.add(db_temp_ban)
    db.commit()
    db.refresh(db_temp_ban)

    # Update the ban reason if provided
    if pubkey.ban_reason:
        update_ban_reason(db, pubkey.pubkey, pubkey.ban_reason)

    return db_temp_ban

def remove_temp_ban(db: SessionLocal, pubkey: PublicKeyCreate):
    db_temp_ban = db.query(TempBan).filter(TempBan.pubkey == pubkey.pubkey).first()
    if db_temp_ban:
        db.delete(db_temp_ban)
        db.commit()

def check_pubkey_status(db: SessionLocal, pubkey: str):
    # Convert Npub to hex if necessary
    if pubkey.startswith("npub"):
        hex_pubkey = convert_npub_to_hex(pubkey)
    else:
        hex_pubkey = pubkey

    # Check if the public key is blocked
    blocked_pubkey = db.query(PublicKey).filter(PublicKey.pubkey == hex_pubkey).first()
    if blocked_pubkey:
        # Check if the public key is temporarily banned
        temp_ban = db.query(TempBan).filter(TempBan.pubkey == hex_pubkey).first()
        if temp_ban:
            return {
                "status": "blocked",
                "temp_ban": True,
                "expiry_timestamp": temp_ban.expiry_timestamp
            }
        return {"status": "blocked", "temp_ban": False}

    return {"status": "not_blocked"}

def update_ban_reason(db: SessionLocal, pubkey: str, reason: str, moderator_name: str):
    hex_pubkey = convert_npub_to_hex(pubkey) if pubkey.startswith("npub") else pubkey
    db_pubkey = db.query(PublicKey).filter(PublicKey.pubkey == hex_pubkey).first()
    if db_pubkey:
        db_pubkey.ban_reason = reason
        db_pubkey.moderator_name = moderator_name
        db.commit()
        db.refresh(db_pubkey)
        return db_pubkey
    raise HTTPException(status_code=404, detail="Public key not found")

def remove_ban_reason(db: SessionLocal, pubkey: str):
    hex_pubkey = convert_npub_to_hex(pubkey) if pubkey.startswith("npub") else pubkey
    db_pubkey = db.query(PublicKey).filter(PublicKey.pubkey == hex_pubkey).first()
    if db_pubkey:
        db_pubkey.ban_reason = None
        db.commit()
        db.refresh(db_pubkey)
        return db_pubkey
    raise HTTPException(status_code=404, detail="Public key not found")

def add_blacklisted_word(db: SessionLocal, word: str):
    existing_word = db.query(Word).filter(Word.word == word).first()
    if existing_word:
        return {"message": "Word already blacklisted", "status": "already_blacklisted"}
    
    db_word = Word(word=word, timestamp=datetime.utcnow())
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return {"message": "Word successfully blacklisted", "status": "blacklisted", "word": db_word.word}

def remove_blacklisted_word(db: SessionLocal, word: str):
    db_word = db.query(Word).filter(Word.word == word).first()
    if db_word:
        db.delete(db_word)
        db.commit()
        return {"message": "Word removed from blacklist"}
    raise HTTPException(status_code=404, detail="Word not found")

def add_blocked_ip(db: SessionLocal, ip: str, ban_reason: str = None):
    existing_ip = db.query(IPAddress).filter(IPAddress.ip == ip).first()
    if existing_ip:
        raise HTTPException(status_code=400, detail="IP address already blocked")
    
    db_ip = IPAddress(ip=ip, timestamp=datetime.utcnow(), ban_reason=ban_reason)
    db.add(db_ip)
    db.commit()
    db.refresh(db_ip)
    return db_ip

def remove_blocked_ip(db: SessionLocal, ip: str):
    db_ip = db.query(IPAddress).filter(IPAddress.ip == ip).first()
    if db_ip:
        db.delete(db_ip)
        db.commit()
        return {"message": "IP address removed from blacklist"}
    raise HTTPException(status_code=404, detail="IP address not found")

def get_blocked_words(db: SessionLocal):
    return db.query(Word).all()

def add_moderator(db: SessionLocal, name: str, private_key: str):
    existing_moderator = db.query(Moderator).filter(Moderator.name == name).first()
    if existing_moderator:
        raise HTTPException(status_code=400, detail="Moderator already exists")
    
    db_moderator = Moderator(name=name, private_key=private_key, timestamp=datetime.utcnow())
    db.add(db_moderator)
    db.commit()
    db.refresh(db_moderator)
    return db_moderator

def remove_moderator(db: SessionLocal, name: str):
    db_moderator = db.query(Moderator).filter(Moderator.name == name).first()
    if db_moderator:
        db.delete(db_moderator)
        db.commit()
        return {"message": "Moderator removed"}
    raise HTTPException(status_code=404, detail="Moderator not found")

def list_moderators(db: SessionLocal):
    return db.query(Moderator).all()

def search_blocked_entities(db: SessionLocal, entity_type: str, query: str):
    if entity_type == "pubkey":
        return db.query(PublicKey).filter(PublicKey.pubkey.contains(query)).all()
    elif entity_type == "ip":
        return db.query(IPAddress).filter(IPAddress.ip.contains(query)).all()
    elif entity_type == "word":
        return db.query(Word).filter(Word.word.contains(query)).all()
    return []

def bulk_add_blocked_entities(db: SessionLocal, entity_type: str, entities: list[str]):
    if entity_type == "pubkey":
        for pubkey in entities:
            add_blocked_pubkey(db, PublicKeyCreate(pubkey=pubkey))
    elif entity_type == "ip":
        for ip in entities:
            add_blocked_ip(db, ip)
    elif entity_type == "word":
        for word in entities:
            add_blacklisted_word(db, word)
    return {"message": "Entities added successfully"}

def bulk_remove_blocked_entities(db: SessionLocal, entity_type: str, entities: list[str]):
    if entity_type == "pubkey":
        for pubkey in entities:
            remove_blocked_pubkey(db, PublicKeyCreate(pubkey=pubkey))
    elif entity_type == "ip":
        for ip in entities:
            remove_blocked_ip(db, ip)
    elif entity_type == "word":
        for word in entities:
            remove_blacklisted_word(db, word)
    return {"message": "Entities removed successfully"}

def get_statistics(db: SessionLocal):
    pubkey_count = db.query(PublicKey).count()
    ip_count = db.query(IPAddress).count()
    word_count = db.query(Word).count()
    temp_ban_count = db.query(TempBan).count()
    return {
        "blocked_pubkeys": pubkey_count,
        "blocked_ips": ip_count,
        "blocked_words": word_count,
        "temporary_bans": temp_ban_count
    }

def get_expiring_temp_bans(db: SessionLocal, hours: int):
    expiry_threshold = datetime.utcnow() + timedelta(hours=hours)
    return db.query(TempBan).filter(TempBan.expiry_timestamp <= expiry_threshold).all()

def update_moderator_info(db: SessionLocal, name: str, new_name: str = None, new_private_key: str = None):
    db_moderator = db.query(Moderator).filter(Moderator.name == name).first()
    if not db_moderator:
        raise HTTPException(status_code=404, detail="Moderator not found")
    if new_name:
        db_moderator.name = new_name
    if new_private_key:
        db_moderator.private_key = new_private_key
    db.commit()
    db.refresh(db_moderator)
    return db_moderator

def get_audit_logs(db: SessionLocal):
    # Assuming you have an AuditLog model
    return db.query(AuditLog).all()

# ... other CRUD operations ... 