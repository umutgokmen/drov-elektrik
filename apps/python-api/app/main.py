"""
Drov Elektrik - Python API
Drawing/CAD generation services
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import drawings, cad, labels
from app.config import settings

app = FastAPI(
    title="Drov Elektrik - Drawing API",
    description="PDF/DXF/STEP/Label generation services",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drawings.router, prefix="/api/v1", tags=["drawings"])
app.include_router(cad.router, prefix="/api/v1", tags=["cad"])
app.include_router(labels.router, prefix="/api/v1", tags=["labels"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "python-api", "version": "1.0.0"}
