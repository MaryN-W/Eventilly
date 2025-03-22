from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel


# EVENT REGISTRATION SCHEMAS FOR MANAGING ATTENDEES AND EVENTS
class RegistrationStatus(str, Enum):
    REGISTERED = "registered"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    WAITLISTED = "waitlisted"

class RegistrationBase(BaseModel):
    event_id: UUID  
    attendee_id: UUID  
    status: RegistrationStatus = RegistrationStatus.REGISTERED

class RegistrationCreate(RegistrationBase):
    pass

class RegistrationUpdate(BaseModel):
    status: RegistrationStatus

class Registration(RegistrationBase):
    id: UUID  
    registration_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 
