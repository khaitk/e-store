from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import models, schemas

router = APIRouter()

@router.get("/categories", response_model=List[schemas.Category])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(models.Category).offset(skip).limit(limit).all()
    return categories

@router.get("/categories/{category_id}", response_model=schemas.Category)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/categories", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    # Check if parent category exists if parent_id is provided
    if category.parent_id:
        parent_category = db.query(models.Category).filter(models.Category.id == category.parent_id).first()
        if not parent_category:
            raise HTTPException(status_code=404, detail="Parent category not found")
    
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/categories/{category_id}", response_model=schemas.Category)
def update_category(category_id: int, category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if parent category exists if parent_id is provided
    if category.parent_id:
        parent_category = db.query(models.Category).filter(models.Category.id == category.parent_id).first()
        if not parent_category:
            raise HTTPException(status_code=404, detail="Parent category not found")
        
        # Prevent circular reference
        if category.parent_id == category_id:
            raise HTTPException(status_code=400, detail="Category cannot be its own parent")
    
    db_category.name = category.name
    db_category.description = category.description
    db_category.parent_id = category.parent_id
    
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    # Check if category has products
    products = db.query(models.Product).filter(models.Product.category_id == category_id).first()
    if products:
        raise HTTPException(status_code=400, detail="Cannot delete category with products")
    
    # Check if category has subcategories
    subcategories = db.query(models.Category).filter(models.Category.parent_id == category_id).first()
    if subcategories:
        raise HTTPException(status_code=400, detail="Cannot delete category with subcategories")
    
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(db_category)
    db.commit()
    return None
