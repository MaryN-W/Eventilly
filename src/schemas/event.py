from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

# EVENT MODELS FOR EVENT MANAGEMENT AND REGISTRATION
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    location: Optional[str] = None
    max_capacity: Optional[int] = None
    is_active: bool = True

class EventCreate(EventBase):
    category_id: UUID

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    max_capacity: Optional[int] = None
    is_active: Optional[bool] = None
    category_id: Optional[UUID] = None

class Event(EventBase):
    id: UUID
    category_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SimpleRegistration(BaseModel):
    id: UUID
    event_id: UUID
    attendee_id: UUID
    status: str
    registration_date: datetime

    class Config:
        from_attributes = True

class EventWithAttendees(Event):
    event_attendees: List[SimpleRegistration] = []

    class Config:
        from_attributes = True
