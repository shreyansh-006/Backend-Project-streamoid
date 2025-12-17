import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
import pandas as pd
import io
import os

# Create test DB
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Product Listing Tool APIs. Go to /docs for Swagger UI."}

def test_create_template():
    payload = {
        "name": "Myntra",
        "attributes_schema": {
            "productName": {"type": "string", "max_length": 150},
            "brand": {"type": "string"},
            "price": {"type": "number"},
            "mrp": {"type": "number"}
        }
    }
    response = client.post("/templates/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Myntra"
    assert "id" in data

def test_upload_file():
    # Create a dummy CSV
    csv_content = b"Name,Brand,MRP,SellingPrice\nShirt,Nike,1000,800\nShoe,Adidas,2000,2500" # Note: 2nd row has Price > MRP
    
    files = {'file': ('test_products.csv', csv_content, 'text/csv')}
    response = client.post("/upload/", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["headers"] == ["Name", "Brand", "MRP", "SellingPrice"]
    return data["id"] # Return file_id for next test if we were chaining, but tests separate

def test_full_flow():
    # 1. Create Template
    t_payload = {
        "name": "TestMkt",
        "attributes_schema": {
            "title": {"type": "string"},
            "mrp": {"type": "number"},
            "price": {"type": "number"},
            "color": {"type": "string"}
        }
    }
    t_res = client.post("/templates/", json=t_payload)
    template_id = t_res.json()["id"]

    # 2. Upload File
    csv_content = b"Item,Cost,Retail,Hue\nItem1,500,400,Red\nItem2,200,100,Blue"
    # Row 1: Price(400) <= MRP(500) -> Valid
    # Row 2: Price(100) <= MRP(200) -> Valid (Wait, Cost usually is lower... let's match mappings)
    # Let's say: mrp <- Cost, price <- Retail
    # Item1: mrp=500, price=400. OK.
    # Item2: mrp=200, price=100. OK.
    
    # Let's add an invalid one
    csv_content = b"Item,Cost,Retail,Hue\nVal1,500,400,Red\nInv1,200,300,Blue"
    # Inv1: mrp=200, price=300. Invalid (Price > MRP).
    
    files = {'file': ('flow_test.csv', csv_content, 'text/csv')}
    f_res = client.post("/upload/", files=files)
    file_id = f_res.json()["id"]

    # 3. Create Mapping
    m_payload = {
        "template_id": template_id,
        "file_id": file_id,
        "mapping_rules": {
            "title": "Item",
            "mrp": "Cost",
            "price": "Retail",
            "color": "Hue"
        }
    }
    m_res = client.post("/mappings/", json=m_payload)
    assert m_res.status_code == 200
    mapping_id = m_res.json()["id"]

    # 4. Validate
    v_res = client.get(f"/mappings/{mapping_id}/validate")
    assert v_res.status_code == 200
    v_data = v_res.json()
    
    assert v_data["total_rows"] == 2
    assert v_data["valid_rows"] == 1
    assert v_data["invalid_rows_count"] == 1
    assert v_data["sample_invalid_rows"][0]["errors"][0] == "Price (300) cannot be greater than MRP (200)."
