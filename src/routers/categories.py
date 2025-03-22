from sqlalchemy.exc import IntegrityError  
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from ..db.main import get_db
from ..models import models  
from typing import List
from ..schemas.category import Category, CategoryCreate, CategoryBase

router = APIRouter()
# GET ALL CATEGORIES FROM DB
@router.get("", response_model=List[Category])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Category))
    categories = result.scalars().all()
    # EXPLICITLY LOAD EVENTS IF NEEDED (OPTIONAL)
    for category in categories:
        await db.refresh(category, attribute_names=['id', 'name', 'description', 'created_at', 'updated_at'])
    
    return categories

# ENDPOINT TO CREATE A NEW CATEGORY IN THE DATABASE.
@router.post("", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(category_data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    try:
        new_category = models.Category(**category_data.model_dump())
        db.add(new_category)
        await db.commit()
    
        await db.refresh(new_category, attribute_names=['id', 'name', 'description', 'created_at', 'updated_at'])
        
        return new_category
    except IntegrityError as e:
        await db.rollback()
        if "ix_categories_name" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category '{category_data.name}' already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database error"
        )

# UPDATE CATEGORY: FETCH, MODIFY, COMMIT, THEN RETURN THE UPDATED CATEGORY INSTANCE.
@router.put("/{category_id}", response_model=Category)
async def update_category(category_id: UUID, category_update: CategoryBase, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Category).filter(models.Category.id == category_id))
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in category_update.model_dump(exclude_unset=True).items():
        setattr(category, key, value)

    await db.commit()
    await db.refresh(category)
    return category

# DELETE CATEGORY IF FOUND AND COMMITS THE DATABASE TRANSACTION.
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Category).filter(models.Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await db.delete(category)
    await db.commit()
