from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import selectinload
from ..db.main import get_db
from ..models import models
from ..schemas import Attendee, AttendeeCreate, AttendeeWithRegistrations

router = APIRouter()
# GET ATTENDEES WITH OPTIONAL FILTERS BY EMAIL AND PHONE, OFFSET AND LIMIT APPLIED.
@router.get("", response_model=List[Attendee])
async def list_attendees(
    email: Optional[str] = None,
    phone: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    GET /attendees
    List all attendees, with optional filters by email or phone.
    """
    query = select(models.Attendee)

    if email:
        query = query.where(models.Attendee.email.contains(email))
    if phone:
        query = query.where(models.Attendee.phone.contains(phone))

    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


# CREATE NEW ATTENDEE WITH UNIQUE EMAIL CHECK BEFORE INSERTING
@router.post("", response_model=Attendee, status_code=status.HTTP_201_CREATED)
async def create_attendee(
    attendee_data: AttendeeCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    POST /attendees
    Create a new attendee.
    """
    existing = await db.execute(
        select(models.Attendee).where(models.Attendee.email == attendee_data.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="Attendee with this email already exists"
        )

    new_attendee = models.Attendee(**attendee_data.model_dump())
    db.add(new_attendee)
    await db.commit()
    await db.refresh(new_attendee)
    return new_attendee


# FETCH ATTENDEE PROFILE WITH REGISTRATIONS AND EVENTS.
@router.get("/{attendee_id}", response_model=AttendeeWithRegistrations)
async def get_attendee_profile(
    attendee_id: UUID,
    db: AsyncSession = Depends(get_db), 
):
    """
    GET /attendees/{attendee_id}
    Get attendee profile with event history and registrations.
    """
    result = await db.execute(
        select(models.Attendee).where(models.Attendee.id == attendee_id)
    )
    attendee = result.scalar_one_or_none()

    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")

    registrations_result = await db.execute(
        select(models.Registration)
        .where(models.Registration.attendee_id == attendee_id)
        .options(selectinload(models.Registration.event))
    )
    registrations = registrations_result.scalars().all()

    return AttendeeWithRegistrations(
        **attendee.__dict__,
        registrations=registrations,
        events=[registration.event for registration in registrations],
    )