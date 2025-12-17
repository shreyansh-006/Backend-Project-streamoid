from fastapi import FastAPI
from .database import engine, Base
from .routers import templates, upload, mapping

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Product Listing Tool",
    description="Backend-only tool for mapping seller files to marketplace templates.",
    version="1.0.0"
)

app.include_router(templates.router)
app.include_router(upload.router)
app.include_router(mapping.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Product Listing Tool APIs. Go to /docs for Swagger UI."}
