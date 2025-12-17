from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class TemplateBase(BaseModel):
    name: str
    attributes_schema: Dict[str, Any]

class TemplateCreate(TemplateBase):
    pass

class TemplateResponse(TemplateBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class FileUploadResponse(BaseModel):
    id: int
    filename: str
    headers: List[str]
    preview: List[Dict[str, Any]]
    total_rows: int

class MappingCreate(BaseModel):
    template_id: int
    file_id: int
    mapping_rules: Dict[str, str] # template_attr -> seller_col

class MappingResponse(BaseModel):
    id: int
    template_id: int
    file_id: int
    mapping_rules: Dict[str, str]
    created_at: datetime

    class Config:
        orm_mode = True

class ValidationRow(BaseModel):
    row_index: int
    data: Dict[str, Any]
    errors: List[str]
    is_valid: bool

class ValidationResponse(BaseModel):
    mapping_id: int
    total_rows: int
    valid_rows: int
    invalid_rows_count: int
    sample_invalid_rows: List[ValidationRow]
    # In a real app, we might perform pagination or return a download link for full report
