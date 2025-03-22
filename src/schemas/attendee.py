from __future__ import annotations
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import List, Optional, TYPE_CHECKING
import uuid

# Import type definitions for type checking only
if TYPE_CHECKING:
    from .event import Event
    from .registration import Registration

# Base Schema for Attendee (only the fields that should be provided by clients)
class AttendeeBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str

# Schema for Creating a New Attendee (only what the client provides)
class AttendeeCreate(AttendeeBase):
    pass  # Inherits everything from AttendeeBase

# Schema for an Attendee response (what gets returned from the API)
class Attendee(AttendeeBase):
    id: uuid.UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Schema for Attendee with Event Details
class AttendeeWithEvents(Attendee):
    events: List["Event"] = []
    
    model_config = ConfigDict(from_attributes=True)

# Schema for Attendee with Registrations
class AttendeeWithRegistrations(Attendee):
    registrations: List["Registration"] = []
    events: List["Event"] = []
    
    model_config = ConfigDict(from_attributes=True)

# Import at runtime to resolve forward references
from .event import Event
from .registration import Registration

# Update forward references
AttendeeWithEvents.model_rebuild()
AttendeeWithRegistrations.model_rebuild()