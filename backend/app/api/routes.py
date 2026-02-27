"""
API Routes - Main router for all endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
import io
import os
import json
import subprocess
from datetime import datetime

from app.schemas import (
    BoxModel,
    ConfigurationInput,
    ValidationResult,
    LayoutResult,
    OutputFormat,
    GenerateRequest,
    BOMItem,
    BOMResult,
    SwitchgearConfigurationInput,
    CoverElementPlacement,
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    LabelInput,
)
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.configuration import Configuration
from app.models import (
    get_all_box_models,
    get_box_model_by_id,
    HOLE_SIZES,
    get_all_switchgear,
    get_switchgear_by_id,
    get_switchgear_by_category,
    get_all_cover_elements,
    get_cover_element_by_id,
    get_cover_elements_by_category,
)
from app.services import (
    run_full_validation,
    calculate_full_layout,
    generate_pdf,
    generate_dxf,
    generate_cad_svg_content,
    validate_cover_elements,
    calculate_switchgear_positions,
    auto_distribute_components,
)
from app.schemas import SwitchgearLayoutResult

router = APIRouter()


# ==================== BOX MODELS ====================

@router.get("/boxes", response_model=list[BoxModel])
async def list_box_models():
    """Get all available box models"""
    return get_all_box_models()


@router.get("/boxes/{box_id}", response_model=BoxModel)
async def get_box_model(box_id: str):
    """Get a specific box model by ID"""
    box = get_box_model_by_id(box_id)
    if not box:
        raise HTTPException(status_code=404, detail=f"Box model '{box_id}' not found")
    return box


@router.get("/hole-sizes")
async def list_hole_sizes():
    """Get available hole sizes"""
    return HOLE_SIZES


# ==================== VALIDATION ====================

@router.post("/validate", response_model=ValidationResult)
async def validate_configuration(config: ConfigurationInput):
    """
    Validate a configuration against engineering rules.
    
    Returns validation errors and warnings.
    """
    return run_full_validation(config)


# ==================== GEOMETRY ====================

@router.post("/layout", response_model=LayoutResult)
async def calculate_layout(config: ConfigurationInput):
    """
    Calculate complete layout for a configuration.
    
    Returns rail positions and hole coordinates.
    """
    # First validate
    validation = run_full_validation(config)
    if not validation.is_valid:
        raise HTTPException(
            status_code=400, 
            detail={"message": "Invalid configuration", "errors": [e.dict() for e in validation.errors]}
        )
    
    try:
        return calculate_full_layout(config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== DRAWING GENERATION ====================

@router.post("/generate/pdf")
async def generate_pdf_drawing(config: ConfigurationInput):
    """
    Generate a professional PDF drawing.
    
    Returns PDF file as download.
    """
    # Validate first
    validation = run_full_validation(config)
    if not validation.is_valid:
        raise HTTPException(
            status_code=400,
            detail={"message": "Invalid configuration", "errors": [e.dict() for e in validation.errors]}
        )
    
    try:
        # Calculate layout
        layout = calculate_full_layout(config)
        
        # Generate PDF
        pdf_bytes = generate_pdf(config, layout)
        
        # Get box for filename
        box = get_box_model_by_id(config.box_id)
        filename = f"DRV-{box.id.upper()}-001.pdf" if box else "drawing.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/generate/dxf")
async def generate_dxf_drawing(config: ConfigurationInput):
    """
    Generate an AutoCAD-compatible DXF drawing.
    
    Returns DXF file as download.
    """
    # Validate first
    validation = run_full_validation(config)
    if not validation.is_valid:
        raise HTTPException(
            status_code=400,
            detail={"message": "Invalid configuration", "errors": [e.dict() for e in validation.errors]}
        )
    
    try:
        # Calculate layout
        layout = calculate_full_layout(config)
        
        # Generate DXF
        dxf_bytes = generate_dxf(config, layout)
        
        # Get box for filename
        box = get_box_model_by_id(config.box_id)
        filename = f"DRV-{box.id.upper()}-001.dxf" if box else "drawing.dxf"
        
        return Response(
            content=dxf_bytes,
            media_type="application/dxf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DXF generation failed: {str(e)}")


@router.post("/generate/step")
async def generate_step_drawing(config: ConfigurationInput):
    """
    Generate a STEP file via CadQuery subprocess.
    Returns the .step file as a download.
    """
    validation = run_full_validation(config)
    if not validation.is_valid:
        raise HTTPException(
            status_code=400,
            detail={"message": "Invalid configuration", "errors": [e.dict() for e in validation.errors]}
        )

    box = get_box_model_by_id(config.box_id)
    if not box:
        raise HTTPException(status_code=404, detail=f"Box model '{config.box_id}' not found")

    script_path = os.path.join(os.path.dirname(__file__), "../../generate_cad.py")
    if not os.path.exists(script_path):
        script_path = os.path.expanduser("~/Documents/GitHub/Drov/backend/generate_cad.py")
    if not os.path.exists(script_path):
        raise HTTPException(status_code=500, detail="CadQuery script not found")

    conda_python = os.path.expanduser("~/miniconda3/envs/cadquery/bin/python")
    if not os.path.exists(conda_python):
        raise HTTPException(status_code=500, detail="CadQuery environment not found")

    config_data = json.dumps({
        "width": box.internal_width,
        "length": box.internal_length,
        "depth": box.internal_depth,
        "holes_bottom": config.holes_bottom,
        "holes_top": config.holes_top,
        "output_format": "step",
    })

    my_env = os.environ.copy()
    my_env.pop("PYTHONPATH", None)

    try:
        subprocess.run(
            [conda_python, script_path, config_data],
            check=True,
            capture_output=True,
            cwd=os.path.dirname(script_path),
            env=my_env,
            timeout=60,
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"STEP generation failed: {e.stderr.decode()[:200]}")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="STEP generation timed out")

    step_path = os.path.join(os.path.dirname(script_path), "cad_output.step")
    if not os.path.exists(step_path):
        raise HTTPException(status_code=500, detail="STEP output file not found")

    with open(step_path, "rb") as f:
        step_bytes = f.read()

    filename = f"DRV-{box.id.upper()}-001.step"

    return Response(
        content=step_bytes,
        media_type="application/step",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/generate/preview")
async def generate_preview(config: ConfigurationInput):
    """
    Generate High-Fidelity 3D Preview (SVG).
    """
    # Validate first
    validation = run_full_validation(config)
    if not validation.is_valid:
        raise HTTPException(
            status_code=400,
            detail={"message": "Invalid configuration", "errors": [e.dict() for e in validation.errors]}
        )
    
    try:
        svg_bytes = generate_cad_svg_content(config)
        return Response(content=svg_bytes, media_type="image/svg+xml")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Preview generation failed: {str(e)}")


# ==================== BOM ====================

@router.post("/bom", response_model=BOMResult)
async def generate_bom(config: ConfigurationInput):
    """
    Generate Bill of Materials for a configuration.
    """
    box = get_box_model_by_id(config.box_id)
    if not box:
        raise HTTPException(status_code=404, detail=f"Box model '{config.box_id}' not found")
    
    total_holes = config.holes_top + config.holes_bottom + config.holes_left + config.holes_right
    
    items = []
    item_no = 1
    
    # Enclosure
    items.append(BOMItem(
        item_no=item_no,
        part_name=f"{box.name} Enclosure",
        part_code=f"P+F-{box.id.upper()}",
        quantity=1
    ))
    item_no += 1
    
    # DIN Rails
    if box.rail_count > 0:
        items.append(BOMItem(
            item_no=item_no,
            part_name="NS 35 DIN Rail",
            part_code="NS35-DIN",
            quantity=box.rail_count
        ))
        item_no += 1
    
    # Terminals
    if config.terminals > 0:
        items.append(BOMItem(
            item_no=item_no,
            part_name="UT 2,5 Terminal Block",
            part_code="PHX-UT2.5",
            quantity=config.terminals
        ))
        item_no += 1
    
    # Cable Glands
    if total_holes > 0:
        items.append(BOMItem(
            item_no=item_no,
            part_name="M20 Cable Gland",
            part_code="M20-GL",
            quantity=total_holes
        ))
    
    return BOMResult(items=items, total_items=len(items))


# ==================== SWITCHGEAR CATALOG ====================

@router.get("/switchgear")
async def list_switchgear(category: str | None = None):
    """Get available switchgear components, optionally filtered by category"""
    if category:
        return get_switchgear_by_category(category)
    return get_all_switchgear()


@router.get("/switchgear/{component_id}")
async def get_switchgear(component_id: str):
    """Get a specific switchgear component by ID"""
    component = get_switchgear_by_id(component_id)
    if not component:
        raise HTTPException(status_code=404, detail=f"Switchgear '{component_id}' not found")
    return component


# ==================== COVER ELEMENTS CATALOG ====================

@router.get("/cover-elements")
async def list_cover_elements(category: str | None = None):
    """Get available cover elements, optionally filtered by category"""
    if category:
        return get_cover_elements_by_category(category)
    return get_all_cover_elements()


@router.get("/cover-elements/{element_id}")
async def get_cover_element(element_id: str):
    """Get a specific cover element by ID"""
    element = get_cover_element_by_id(element_id)
    if not element:
        raise HTTPException(status_code=404, detail=f"Cover element '{element_id}' not found")
    return element


# ==================== EXTENDED VALIDATION ====================

@router.post("/validate/cover-elements", response_model=ValidationResult)
async def validate_cover(config: SwitchgearConfigurationInput):
    """Validate cover element placements for collisions and boundary violations"""
    errors, warnings = validate_cover_elements(config.cover_elements, config.box_id)
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


# ==================== SWITCHGEAR LAYOUT ====================

@router.post("/switchgear/layout", response_model=SwitchgearLayoutResult)
async def calculate_switchgear_layout(config: SwitchgearConfigurationInput):
    """
    Calculate complete layout including switchgear positions.
    Returns base layout + switchgear positions + cover element positions.
    """
    # First validate the base config
    base_config = ConfigurationInput(
        box_id=config.box_id,
        terminals=config.terminals,
        holes_top=config.holes_top,
        holes_bottom=config.holes_bottom,
        holes_left=config.holes_left,
        holes_right=config.holes_right,
        holes_top_spec=config.holes_top_spec,
        holes_bottom_spec=config.holes_bottom_spec,
        holes_left_spec=config.holes_left_spec,
        holes_right_spec=config.holes_right_spec,
    )
    validation = run_full_validation(base_config)
    if not validation.is_valid:
        raise HTTPException(
            status_code=400,
            detail={"message": "Invalid configuration", "errors": [e.dict() for e in validation.errors]}
        )

    base_layout = calculate_full_layout(base_config)

    # Calculate switchgear positions
    sw_positions, sw_errors, sw_warnings = calculate_switchgear_positions(
        config.switchgear_rails,
        base_layout.rails,
        config.box_id,
    )
    if sw_errors:
        raise HTTPException(
            status_code=400,
            detail={"message": "Switchgear layout error", "errors": [e.dict() for e in sw_errors]}
        )

    # Resolve cover element positions
    cover_positions = []
    for ce in config.cover_elements:
        from app.models import get_cover_element_by_id
        elem = get_cover_element_by_id(ce.element_id)
        if elem:
            from app.schemas import CoverElementPosition
            cover_positions.append(CoverElementPosition(
                element_id=ce.element_id,
                x=ce.x,
                y=ce.y,
                cutout_diameter=elem.get("cutout_diameter"),
                cutout_width=elem.get("cutout_width"),
                cutout_height=elem.get("cutout_height"),
                label=ce.label,
            ))

    return SwitchgearLayoutResult(
        rails=base_layout.rails,
        holes_top=base_layout.holes_top,
        holes_bottom=base_layout.holes_bottom,
        holes_left=base_layout.holes_left,
        holes_right=base_layout.holes_right,
        switchgear_positions=sw_positions,
        cover_element_positions=cover_positions,
    )


@router.post("/switchgear/generate/pdf")
async def generate_switchgear_pdf(config: SwitchgearConfigurationInput):
    """Generate PDF with switchgear components and cover elements."""
    base_config = ConfigurationInput(
        box_id=config.box_id,
        terminals=config.terminals,
        holes_top=config.holes_top,
        holes_bottom=config.holes_bottom,
        holes_left=config.holes_left,
        holes_right=config.holes_right,
        holes_top_spec=config.holes_top_spec,
        holes_bottom_spec=config.holes_bottom_spec,
        holes_left_spec=config.holes_left_spec,
        holes_right_spec=config.holes_right_spec,
    )
    validation = run_full_validation(base_config)
    if not validation.is_valid:
        raise HTTPException(
            status_code=400,
            detail={"message": "Invalid configuration", "errors": [e.dict() for e in validation.errors]}
        )

    base_layout = calculate_full_layout(base_config)

    sw_positions, sw_errors, _ = calculate_switchgear_positions(
        config.switchgear_rails, base_layout.rails, config.box_id,
    )
    if sw_errors:
        raise HTTPException(
            status_code=400,
            detail={"message": "Switchgear layout error", "errors": [e.dict() for e in sw_errors]}
        )

    cover_data = []
    for ce in config.cover_elements:
        cover_data.append({
            "element_id": ce.element_id,
            "x": ce.x,
            "y": ce.y,
            "label": ce.label,
        })

    pdf_bytes = generate_pdf(
        base_config, base_layout,
        cover_elements=cover_data if cover_data else None,
        switchgear_positions=sw_positions if sw_positions else None,
    )

    box = get_box_model_by_id(config.box_id)
    filename = f"DRV-{box.id.upper()}-SW-001.pdf" if box else "switchgear-drawing.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ==================== ORDER HISTORY ====================

def _generate_drawing_number(db: Session) -> str:
    """Generate unique drawing number DRV-YYYY-XXXX"""
    year = datetime.now().year
    last = db.query(Configuration).filter(
        Configuration.drawing_number.like(f"DRV-{year}-%")
    ).order_by(Configuration.id.desc()).first()
    seq = 1
    if last:
        try:
            seq = int(last.drawing_number.split("-")[-1]) + 1
        except ValueError:
            pass
    return f"DRV-{year}-{seq:04d}"


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a configuration as an order"""
    box = get_box_model_by_id(order.box_id)
    if not box:
        raise HTTPException(status_code=404, detail=f"Box model '{order.box_id}' not found")

    drawing_number = _generate_drawing_number(db)
    config = Configuration(
        user_id=current_user.id,
        box_id=order.box_id,
        terminals=order.terminals,
        holes_top=order.holes_top,
        holes_bottom=order.holes_bottom,
        holes_left=order.holes_left,
        holes_right=order.holes_right,
        drawing_number=drawing_number,
        notes=order.notes,
    )
    db.add(config)
    db.commit()
    db.refresh(config)

    return OrderResponse(
        id=config.id,
        drawing_number=config.drawing_number,
        box_id=config.box_id,
        terminals=config.terminals,
        holes_top=config.holes_top,
        holes_bottom=config.holes_bottom,
        holes_left=config.holes_left,
        holes_right=config.holes_right,
        notes=config.notes,
        created_at=config.created_at.isoformat() if config.created_at else "",
        creator_name=current_user.full_name,
    )


@router.get("/orders", response_model=OrderListResponse)
async def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List orders for the current user"""
    orders = db.query(Configuration).filter(
        Configuration.user_id == current_user.id
    ).order_by(Configuration.created_at.desc()).all()

    items = []
    for o in orders:
        items.append(OrderResponse(
            id=o.id,
            drawing_number=o.drawing_number,
            box_id=o.box_id,
            terminals=o.terminals,
            holes_top=o.holes_top,
            holes_bottom=o.holes_bottom,
            holes_left=o.holes_left,
            holes_right=o.holes_right,
            notes=o.notes,
            created_at=o.created_at.isoformat() if o.created_at else "",
            creator_name=current_user.full_name,
        ))
    return OrderListResponse(orders=items, total=len(items))


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific order by ID"""
    order = db.query(Configuration).filter(
        Configuration.id == order_id,
        Configuration.user_id == current_user.id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderResponse(
        id=order.id,
        drawing_number=order.drawing_number,
        box_id=order.box_id,
        terminals=order.terminals,
        holes_top=order.holes_top,
        holes_bottom=order.holes_bottom,
        holes_left=order.holes_left,
        holes_right=order.holes_right,
        notes=order.notes,
        created_at=order.created_at.isoformat() if order.created_at else "",
        creator_name=current_user.full_name,
    )


# ==================== LABEL ====================

@router.post("/generate/label")
async def generate_label(label: LabelInput):
    """Generate a panel identification label as PDF"""
    from app.services.drawing.label_engine import generate_label_pdf

    box = get_box_model_by_id(label.box_id)
    if not box:
        raise HTTPException(status_code=404, detail=f"Box model '{label.box_id}' not found")

    pdf_bytes = generate_label_pdf(label, box)
    filename = f"LABEL-{box.id.upper()}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
