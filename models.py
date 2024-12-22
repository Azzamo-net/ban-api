from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class PublicKey(Base):
    __tablename__ = "blocked_pubkeys"
    id = Column(Integer, primary_key=True, index=True)
    pubkey = Column(String, unique=True, index=True)
    npub = Column(String, unique=True, index=True)
    timestamp = Column(DateTime)
    ban_reason = Column(String, nullable=True)

class Word(Base):
    __tablename__ = "blocked_words"
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True)
    timestamp = Column(DateTime)

class IPAddress(Base):
    __tablename__ = "blocked_ips"
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, unique=True, index=True)
    timestamp = Column(DateTime)
    ban_reason = Column(String, nullable=True)

class TempBan(Base):
    __tablename__ = "temp_bans"
    id = Column(Integer, primary_key=True, index=True)
    pubkey = Column(String, unique=True, index=True)
    expiry_timestamp = Column(DateTime)

class Moderator(Base):
    __tablename__ = "moderators"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    private_key = Column(String, unique=True)
    timestamp = Column(DateTime)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    timestamp = Column(DateTime)
    moderator_name = Column(String)
    details = Column(String)

# ... other models ... 
