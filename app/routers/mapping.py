from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..services.validator import ValidatorService
import os
import pandas as pd

router = APIRouter(
    prefix="/mappings",
    tags=["mappings"]
)

UPLOAD_DIR = "uploaded_files"

@router.post("/", response_model=schemas.MappingResponse)
def create_mapping(mapping: schemas.MappingCreate, db: Session = Depends(database.get_db)):
    # Verify template exists
    template = db.query(models.MarketplaceTemplate).filter(models.MarketplaceTemplate.id == mapping.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
        
    # Verify file exists (record)
    seller_file = db.query(models.SellerFile).filter(models.SellerFile.id == mapping.file_id).first()
    if not seller_file:
        raise HTTPException(status_code=404, detail="File record not found")

    # Save mapping
    db_mapping = models.Mapping(
        template_id=mapping.template_id,
        file_id=mapping.file_id,
        mapping_rules=mapping.mapping_rules
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

@router.get("/", response_model=List[schemas.MappingResponse])
def list_mappings(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.Mapping).offset(skip).limit(limit).all()

@router.get("/{mapping_id}", response_model=schemas.MappingResponse)
def get_mapping(mapping_id: int, db: Session = Depends(database.get_db)):
    mapping = db.query(models.Mapping).filter(models.Mapping.id == mapping_id).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return mapping

@router.get("/{mapping_id}/validate", response_model=schemas.ValidationResponse)
def validate_mapping_data(mapping_id: int, db: Session = Depends(database.get_db)):
    mapping = db.query(models.Mapping).filter(models.Mapping.id == mapping_id).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    template = db.query(models.MarketplaceTemplate).filter(models.MarketplaceTemplate.id == mapping.template_id).first()
    seller_file = db.query(models.SellerFile).filter(models.SellerFile.id == mapping.file_id).first()
    
    # Load the file
    # We assume file is in UPLOAD_DIR with the name stored.
    # Warning: Duplicate filenames in real world would overwrite. Here we assume simple case.
    file_path = os.path.join(UPLOAD_DIR, seller_file.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Source file not found on server")

    try:
        if seller_file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read file: {e}")

    # Run validation
    result = ValidatorService.validate_dataframe(df, mapping.mapping_rules, template.attributes_schema)
    result["mapping_id"] = mapping_id
    
    return result
