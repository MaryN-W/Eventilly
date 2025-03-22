from sqlalchemy import (Column,String,Text,DateTime,ForeignKey,Boolean,Integer,String, Text, Boolean)
from datetime import datetime, timezone
from src.db.base import Base
from enum import Enum  
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
# CATEGORY TABLE (MATCHES ERD CORRECTLY)
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # RELATIONSHIP: ONE CATEGORY HAS MANY EVENTS (ONE-TO-MANY)
    events = relationship("Event", back_populates="category", cascade="all, delete-orphan", lazy='selectin')


# EVENT TABLE (MATCHES ERD)
class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(255), nullable=True)
    max_capacity = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # FOREIGN KEY RELATIONSHIP WITH CATEGORY
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="events")

    # ONE-TO-MANY WITH REGISTRATION
    event_attendees = relationship("Registration", back_populates="event", cascade="all, delete-orphan")


# ATTENDEE TABLE (MATCHES ERD)
class Attendee(Base):
    __tablename__ = "attendees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ONE-TO-MANY RELATIONSHIP WITH REGISTRATION
    registrations = relationship("Registration", back_populates="attendee", cascade="all, delete-orphan")


# REGISTRATION TABLE (EVENT_ATTENDEE)
class RegistrationStatus(str, Enum):
    REGISTERED = "registered"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    WAITLISTED = "waitlisted"


class Registration(Base):
    """REGISTRATION RECORD LINKING EVENT AND ATTENDEE WITH STATUS, CREATED & UPDATED TIMESTAMPS."""
    __tablename__ = "registrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # FOREIGN KEY RELATIONSHIPS
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    attendee_id = Column(UUID(as_uuid=True), ForeignKey("attendees.id"), nullable=False)
    status = Column(String(20), default=RegistrationStatus.REGISTERED.value, nullable=False)
    registration_date = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # RELATIONSHIPS WITH EVENT AND ATTENDEE
    event = relationship("Event", back_populates="event_attendees")
    attendee = relationship("Attendee", back_populates="registrations")
