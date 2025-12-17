from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..services.file_parser import FileParserService
import os
import shutil

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=schemas.FileUploadResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    # 1. Parse content (in memory for now to extract headers)
    # Note: FileParserService reads the file. We need to handle the stream carefully.
    # The service reads it. We might want to save it first then read from disk
    # to avoid cursor issues, or read memory then save.
    
    # Save file to disk
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Re-open for parsing (safest way)
    # Create a mock UploadFile or just pass path if we refactor service.
    # But current service expects UploadFile.
    # Let's adjust the usage: read from the saved file.
    
    # Actually, let's just use the pandas read directly on the saved file path in logic here
    # or create a fresh file-like object.
    import pandas as pd
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid file: {e}")

    # Extract info
    preview_data = FileParserService.get_preview(df)
    
    # Save metadata to DB
    db_file = models.SellerFile(
        filename=file.filename,
        extracted_headers=preview_data["headers"]
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    # Add ID and headers to response
    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "headers": preview_data["headers"],
        "preview": preview_data["preview"],
        "total_rows": preview_data["total_rows"]
    }
