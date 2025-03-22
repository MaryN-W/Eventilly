from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List
from src.database import get_db
from src.models.models import Registration, Event, Attendee
from src.schemas.registration import Registration as RegistrationSchema
from src.schemas.registration import RegistrationCreate, RegistrationUpdate

router = APIRouter()


@router.get("", response_model=List[RegistrationSchema])
# LIST REGISTRATIONS
async def list_registrations(db: AsyncSession = Depends(get_db)):
    """List all registrations."""
    result = await db.execute(select(Registration))
    registrations = result.scalars().all()  
    return registrations

#
@router.post("", response_model=RegistrationSchema, status_code=status.HTTP_201_CREATED)
async def create_registration(reg_data: RegistrationCreate, db: AsyncSession = Depends(get_db)):
    """Create a new event registration."""
    
    # CREATE REGISTRATION
    # CHECK IF EVENT EXISTS
    result = await db.execute(select(Event).filter(Event.id == reg_data.event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # CHECK IF ATTENDEE EXISTS
    result = await db.execute(select(Attendee).filter(Attendee.id == reg_data.attendee_id))
    attendee = result.scalar_one_or_none()
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")

    # ENSURE NO DUPLICATES: ATTENDEE IS ALREADY REGISTERED FOR THE EVENT
    result = await db.execute(select(Registration).filter(
        Registration.event_id == reg_data.event_id,
        Registration.attendee_id == reg_data.attendee_id
    ))
    existing_registration = result.scalar_one_or_none()

    if existing_registration:
        raise HTTPException(
            status_code=400,
            detail="Attendee is already registered for this event"
        )

    # CREATE A NEW REGISTRATION
    new_registration = Registration(
        event_id=reg_data.event_id,
        attendee_id=reg_data.attendee_id,
        status=reg_data.status.value
    )

    db.add(new_registration)
    await db.commit()
    await db.refresh(new_registration)
    return new_registration

#GET REGISTRATION BY ID
@router.get("/{registration_id}", response_model=RegistrationSchema)
async def get_registration(registration_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific registration by ID."""
    result = await db.execute(select(Registration).filter(Registration.id == registration_id))
    registration = result.scalar_one_or_none()

    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    return registration


@router.patch("/{registration_id}", response_model=RegistrationSchema)
async def update_registration_status(
    registration_id: UUID, status_update: RegistrationUpdate, db: AsyncSession = Depends(get_db)
):
    """Update the status of a registration."""
    result = await db.execute(select(Registration).filter(Registration.id == registration_id))
    registration = result.scalar_one_or_none()

    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    # UPDATE REGISTRATION STATUS
    registration.status = status_update.status.value
    await db.commit()
    await db.refresh(registration)
    return registration

#
@router.delete("/{registration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_registration(registration_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a registration."""
    result = await db.execute(select(Registration).filter(Registration.id == registration_id))
    registration = result.scalar_one_or_none()

    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    await db.delete(registration)
    await db.commit()
    return None
