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

# ... other models ... 