# Drov Industrial Backend

FastAPI-based backend for the Drov Engineering Configurator.

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

## API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Structure

```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Config, settings
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic schemas
│   └── services/     # Business logic
│       ├── drawing/  # PDF/DXF generation
│       └── validation/ # Validation engine
├── requirements.txt
└── main.py
```
