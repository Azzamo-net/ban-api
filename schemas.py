from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PublicKeyBase(BaseModel):
    pubkey: str

class PublicKeyCreate(BaseModel):
    pubkey: str
    ban_reason: str | None = None

    class Config:
        json_schema_extra = {
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
        from_attributes = True

class IPAddressBase(BaseModel):
    ip: str

class IPAddressCreate(IPAddressBase):
    pass

class IPAddress(IPAddressBase):
    id: int
    timestamp: str

    class Config:
        from_attributes = True

class TempBanCreate(BaseModel):
    pubkey: str
    duration: int = 24
    ban_reason: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "pubkey": "npub1examplepublickey",
                "duration": 24,
                "ban_reason": "Spamming"
            }
        }

class ModeratorCreate(BaseModel):
    name: str
    private_key: str

class ModeratorDelete(BaseModel):
    name: str

class ModeratorUpdate(BaseModel):
    name: str
    new_name: str | None = None
    new_private_key: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "current_moderator_name",
                "new_name": "new_moderator_name",
                "new_private_key": "new_private_key_123"
            }
        }

class UserReportCreate(BaseModel):
    pubkey: str
    report_reason: Optional[str] = None
    reported_by: Optional[str] = None

    class Config:
        orm_mode = True

class UserReportUpdate(BaseModel):
    id: int
    status: str
    handled_by: str
    action_taken: str | None = None

class UserReport(BaseModel):
    id: int
    pubkey: str
    report_reason: Optional[str] = None
    reported_by: Optional[str] = None
    handled_by: Optional[str] = None
    action_taken: Optional[str] = None
    timestamp: datetime

    class Config:
        orm_mode = True

class AuditLog(BaseModel):
    id: int
    action: str
    timestamp: datetime
    performed_by: str

    class Config:
        from_attributes = True

class UserReportResponse(BaseModel):
    id: int
    timestamp: datetime
    reported_by: Optional[str]
    handled_by: Optional[str]
    action_taken: Optional[str]
    message: str
    status: str
    pubkey: str
    report_reason: Optional[str]

class ReportApproval(BaseModel):
    report_id: Optional[int] = None
    pubkey: Optional[str] = None
    moderator_name: str

class BanReasonUpdate(BaseModel):
    pubkey: str
    reason: str

    class Config:
        json_schema_extra = {
            "example": {
                "pubkey": "npub1examplepublickey",
                "reason": "Updated ban reason"
            }
        }

# ... other schemas ... 
