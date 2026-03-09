"""
Label generation endpoints
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import io

from app.schemas import LabelInput
from app.auth import verify_supabase_token
from app.services.drawing.label_engine import generate_label_pdf

router = APIRouter()


@router.post("/label")
async def generate_label(
    label_input: LabelInput,
    _user: dict = Depends(verify_supabase_token),
):
    """Generate a panel label PDF."""
    pdf_bytes = generate_label_pdf(label_input)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=label-{label_input.panel_name}.pdf"},
    )
