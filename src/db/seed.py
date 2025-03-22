#To run seed.py file use :  python -m src.db.seed
from src.db.main import AsyncSessionLocal
from src.models import Category, Event, Attendee, Registration, RegistrationStatus 
from datetime import datetime, timezone
import asyncio
from sqlalchemy import text

async def seed_database():
    async with AsyncSessionLocal() as db:
        try:
            # CLEAR EXISTING DATA IN CORRECT ORDER
            await db.execute(text("DELETE FROM registrations"))
            await db.execute(text("DELETE FROM events")) 
            await db.execute(text("DELETE FROM attendees"))
            await db.execute(text("DELETE FROM categories"))
            await db.commit()

            # ADD CATEGORIES
            tech = Category(name="Tech Conference", description="Tech events")
            music = Category(name="Music Festival", description="Music events")
            db.add_all([tech, music])
            await db.commit()

            # CREATE EVENTS (REFERENCE CATEGORY OBJECTS DIRECTLY)
            event1 = Event(
                title="AI Summit 2025",
                description="Global AI conference",
                category=tech,  # Use relationship instead of category_id
                start_date=datetime(2025, 5, 10, 9, 0, tzinfo=timezone.utc),
                end_date=datetime(2025, 5, 12, 18, 0, tzinfo=timezone.utc),
                location="San Francisco",
                max_capacity=1000
            )

            event2 = Event(
                title="Rock Nation 2025",
                description="Annual rock festival",
                category=music,  # Use relationship
                start_date=datetime(2025, 7, 15, 16, 0, tzinfo=timezone.utc),
                end_date=datetime(2025, 7, 17, 23, 0, tzinfo=timezone.utc),
                location="Chicago",
                max_capacity=5000
            )

            db.add_all([event1, event2])
            await db.commit()

            # CREATE ATTENDEES
            attendee1 = Attendee(
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                phone="+1234567890"
            )

            attendee2 = Attendee(
                first_name="Jane",
                last_name="Smith",
                email="jane@example.com",
                phone="+0987654321"
            )

            db.add_all([attendee1, attendee2])
            await db.commit()

            # CREATE REGISTRATIONS (REFERENCE COMMITTED OBJECTS)
            registration1 = Registration(
                event=event1,
                attendee=attendee1,
                status=RegistrationStatus.REGISTERED
            )

            registration2 = Registration(
                event=event2,
                attendee=attendee2,
                status=RegistrationStatus.CONFIRMED
            )

            db.add_all([registration1, registration2])
            await db.commit()

            print("...Database seeded successfully!")

        except Exception as e:
            await db.rollback()
            print("... Error seeding database:", e)
            raise

if __name__ == "__main__":
    asyncio.run(seed_database())