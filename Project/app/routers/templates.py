from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

router = APIRouter(
    prefix="/templates",
    tags=["templates"]
)

@router.post("/", response_model=schemas.TemplateResponse)
def create_template(template: schemas.TemplateCreate, db: Session = Depends(database.get_db)):
    db_template = models.MarketplaceTemplate(
        name=template.name,
        attributes_schema=template.attributes_schema
    )
    try:
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return db_template
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Template with this name may already exist.")

@router.get("/", response_model=List[schemas.TemplateResponse])
def read_templates(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.MarketplaceTemplate).offset(skip).limit(limit).all()

@router.get("/{template_id}", response_model=schemas.TemplateResponse)
def read_template(template_id: int, db: Session = Depends(database.get_db)):
    db_template = db.query(models.MarketplaceTemplate).filter(models.MarketplaceTemplate.id == template_id).first()
    if db_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return db_template
