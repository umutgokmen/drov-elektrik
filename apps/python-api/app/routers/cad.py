"""
CAD/STEP generation endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import io

from app.schemas import CADRequest
from app.auth import verify_supabase_token

router = APIRouter()


@router.post("/generate-cad")
async def generate_cad(
    request: CADRequest,
    _user: dict = Depends(verify_supabase_token),
):
    """Generate a 3D CAD model (STEP format)."""
    try:
        from app.services.drawing.cad_service import generate_step

        step_bytes = generate_step(request)
        return StreamingResponse(
            io.BytesIO(step_bytes),
            media_type="application/step",
            headers={"Content-Disposition": f"attachment; filename=model-{request.box_id}.step"},
        )
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="CadQuery is not available. Install with: pip install cadquery",
        )
