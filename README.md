# Product Listing Tool

A backend-only tool built with FastAPI to manage marketplace templates, upload seller files (CSV/Excel), and map them to specific marketplace attributes with validation.

## Features

- **Marketplace Template Management**: Create and store JSON templates for marketplaces like Myntra or Flipkart.
- **Seller File Upload**: Upload CSV or Excel files, extracting headers and preview data.
- **Mapping**: Define rules to map seller file columns to template attributes.
- **Validation**:
    - Type checking (String, Number, Integer).
    - Enum validation (e.g., specific sizes or colors).
    - Logic checks (e.g., Price <= MRP).
    - Required field validation.

## Tech Stack

- **Python 3.9+**
- **FastAPI**: REST API framework.
- **Pandas**: For parsing and processing CSV/Excel files.
- **SQLAlchemy + SQLite**: Data persistence.
- **Pydantic**: Data validation schemas.
- **Docker**: Containerization.

## Setup & Usage

### Method 1: Docker (Recommended)

1.  **Build and Run**:
    ```bash
    docker-compose up --build
    ```
2.  The API will be available at `http://localhost:8000`.
3.  Access the interactive API docs at `http://localhost:8000/docs`.

### Method 2: Local Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the App**:
    ```bash
    uvicorn app.main:app --reload
    ```

## Running Tests

Unit and integration tests are located in the `tests/` directory.

To run them inside the container:
```bash
docker-compose run web pytest
```

To run them locally:
```bash
pytest
```

## API Endpoints

-   `POST /templates/`: Create a new marketplace template.
-   `GET /templates/`: List all templates.
-   `POST /upload/`: Upload a seller file (CSV/Excel).
-   `POST /mappings/`: Create a mapping between file columns and template attributes.
-   `GET /mappings/{id}/validate`: Run validation on the mapped parameters and get a report of valid/invalid rows.

## Project Structure

-   `app/`: Main application code.
    -   `routers/`: API endpoints.
    -   `services/`: Business logic (parser, validator).
    -   `models.py`: Database models.
-   `tests/`: Pytest tests.
-   `flow.md`: Documentation of the code flow and architecture.
