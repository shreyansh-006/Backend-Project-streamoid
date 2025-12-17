from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class MarketplaceTemplate(Base):
    __tablename__ = "marketplace_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    attributes_schema = Column(JSON)  # Stores the entire template as JSON
    created_at = Column(DateTime, default=datetime.utcnow)

class SellerFile(Base):
    __tablename__ = "seller_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    extracted_headers = Column(JSON) # List of column names found
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class Mapping(Base):
    __tablename__ = "mappings"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("marketplace_templates.id"))
    file_id = Column(Integer, ForeignKey("seller_files.id")) # Optional: link to a specific file upload session
    mapping_rules = Column(JSON) # Dictionary: {template_attr: seller_column}
    created_at = Column(DateTime, default=datetime.utcnow)

    template = relationship("MarketplaceTemplate")
    file = relationship("SellerFile")
