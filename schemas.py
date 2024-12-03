from pydantic import BaseModel
from datetime import datetime

class PublicKeyBase(BaseModel):
    pubkey: str

class PublicKeyCreate(PublicKeyBase):
    ban_reason: str | None = None

    class Config:
        schema_extra = {
            "example": {
                "pubkey": "npub1examplepublickey",
                "ban_reason": "Violation of terms"
            }
        }

class PublicKey(PublicKeyBase):
    id: int
    npub: str
    timestamp: datetime
    ban_reason: str | None = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "pubkey": "npub1examplepublickey",
                "ban_reason": "Violation of terms"
            }
        }

class WordBase(BaseModel):
    word: str

class WordCreate(BaseModel):
    word: str

class Word(WordBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class IPAddressBase(BaseModel):
    ip: str

class IPAddressCreate(IPAddressBase):
    pass

class IPAddress(IPAddressBase):
    id: int
    timestamp: str

    class Config:
        orm_mode = True

class TempBanCreate(BaseModel):
    pubkey: str
    duration: int = 24
    ban_reason: str | None = None

    class Config:
        schema_extra = {
            "example": {
                "pubkey": "npub1examplepublickey",
                "duration": 24,
                "ban_reason": "Spamming"
            }
        }

# ... other schemas ... 