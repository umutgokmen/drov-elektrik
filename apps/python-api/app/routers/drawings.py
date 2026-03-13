"""
Drawing generation endpoints (PDF, DXF)
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import io

from app.schemas import GenerateRequest, OutputFormat, ConfigurationInput
from app.auth import verify_supabase_token
from app.services.drawing.pdf_engine import generate_pdf
from app.services.drawing.dxf_engine import generate_dxf
from app.services.geometry.layout_service import calculate_full_layout
from app.services.geometry.validation_service import run_full_validation as validate_configuration
from app.services.geometry.switchgear_layout import calculate_switchgear_positions

router = APIRouter()


@router.post("/generate")
async def generate_drawing(
    request: GenerateRequest,
    _user: dict = Depends(verify_supabase_token),
):
    """Generate a technical drawing in the requested format."""
    config = request.configuration

    # Validate configuration
    validation = validate_configuration(config)
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail=[e.model_dump() for e in validation.errors])

    # Calculate layout
    layout = calculate_full_layout(config)

    # Calculate switchgear positions if provided
    switchgear_positions = []
    if request.switchgear_rails:
        positions, _, _ = calculate_switchgear_positions(
            request.switchgear_rails, layout.rails, config.box_id
        )
        switchgear_positions = positions

    if request.format == OutputFormat.PDF:
        pdf_bytes = generate_pdf(config, layout, switchgear_positions=switchgear_positions)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=drawing-{config.box_id}.pdf"},
        )
    elif request.format == OutputFormat.DXF:
        dxf_bytes = generate_dxf(config, layout)
        return StreamingResponse(
            io.BytesIO(dxf_bytes),
            media_type="application/dxf",
            headers={"Content-Disposition": f"attachment; filename=drawing-{config.box_id}.dxf"},
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")


@router.post("/validate")
async def validate(
    config: ConfigurationInput,
    _user: dict = Depends(verify_supabase_token),
):
    """Validate a configuration (authoritative server-side validation)."""
    return validate_configuration(config)


@router.post("/layout")
async def calculate_layout(
    config: ConfigurationInput,
    _user: dict = Depends(verify_supabase_token),
):
    """Calculate the layout for a configuration."""
    return calculate_full_layout(config)
