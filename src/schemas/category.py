from pydantic import BaseModel, ConfigDict, field_serializer
from typing import Optional
from uuid import UUID
from datetime import datetime 

# SCHEMA DEFINITIONS FOR HANDLING CATEGORY DATA
from pydantic import BaseModel, ConfigDict, field_serializer
from typing import Optional
from uuid import UUID
from datetime import datetime 

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()
