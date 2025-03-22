from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from src.schemas import event as schemas
from src.database import get_db 
from src.models import models
from src.schemas.attendee import Attendee 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter()

@router.get("", response_model=List[schemas.Event])
async def list_events(
    category_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)  
):
    """
    GET /events
    List all events with optional filters.
    """
    query = select(models.Event)
    
    # FILTER BY CATEGORY ID IF PROVIDED
    if category_id:
        query = query.where(models.Event.category_id == category_id)
    # FILTER BY ACTIVE STATUS IF PROVIDED
    if is_active is not None:
        query = query.where(models.Event.is_active == is_active)
    # FILTER BY EVENTS OCCURRING WITHIN THE SPECIFIED START AND END DATES
    if start_date and end_date:
        query = query.where(
            and_(
                models.Event.start_date >= start_date,
                models.Event.end_date <= end_date
            )
        )
    result = await db.execute(query)
    return result.scalars().all() 

@router.post("", response_model=schemas.Event, status_code=status.HTTP_201_CREATED)
def create_event(event_data: schemas.EventCreate, db: Session = Depends(get_db)):
    """
    POST /events
    Create a new event.
    """
    # VERIFY THE CATEGORY EXISTS
    category = db.query(models.Category).filter(models.Category.id == event_data.category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    new_event = models.Event(**event_data.model_dump())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

@router.get("/{event_id}", response_model=schemas.EventWithAttendees)
def get_event_details(event_id: UUID, db: Session = Depends(get_db)):
    """
    GET /events/{event_id}
    Get specific event details with current attendees.
    """
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # LOAD ALL EVENT ATTENDEES FOR THIS EVENT
    event_attendees = db.query(models.Registration).filter(models.Registration.event_id == event_id).all()
    
    # CREATE A DICTIONARY FROM THE EVENT OBJECT - to ensure proper API serialization
    event_dict = {k: v for k, v in event.__dict__.items() if not k.startswith('_')}
    # RETURN EVENT WITH ATTENDEES SCHEMA
    return schemas.EventWithAttendees(
        **event_dict,
        event_attendees=event_attendees
    )

@router.put("/{event_id}", response_model=schemas.Event)
def update_event(event_id: UUID, event_update: schemas.EventUpdate, db: Session = Depends(get_db)):
    """
    PUT /events/{event_id}
    Update event details (e.g., max_capacity, is_active, etc.).
    """
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # APPLY PARTIAL UPDATES
    update_data = event_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)
    
    db.commit()
    db.refresh(event)
    return event

@router.get("/{event_id}/attendees", response_model=List[Attendee])
def list_event_attendees(
    event_id: UUID,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    GET /events/{event_id}/attendees
    List all attendees for a specific event, optionally filtered by registration status.
    """
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    query = db.query(models.Attendee).join(models.Registration)
    query = query.filter(models.Registration.event_id == event_id)
    
    if status:
        query = query.filter(models.Registration.status == status)
    
    return query.all()