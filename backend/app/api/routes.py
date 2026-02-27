"""
API Routes - Main router for all endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
import io

from app.schemas import (
    BoxModel,
    EJCBoxModel,
    ConfigurationInput,
    ValidationResult,
    LayoutResult,
    OutputFormat,
    GenerateRequest,
    BOMItem,
    BOMResult,
    LabelInput,
    OrderCreate,
    OrderResponse,
)
from app.models import (
    get_all_box_models,
    get_box_model_by_id,
    SALT_MALZEME_COMPONENTS,
    get_all_ejc_box_models,
    get_ejc_box_model_by_id,
    Order,
)
from app.core.database import get_db
from app.services import (
    run_full_validation,
    calculate_full_layout,
    generate_pdf,
    generate_dxf,
    generate_cad_svg_content,
    generate_step,
    generate_label_pdf,
)

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
    Includes both user-configured components and standard salt malzeme items.
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
        item_no += 1
    
    # Salt malzeme (standard) components
    for component in SALT_MALZEME_COMPONENTS:
        items.append(BOMItem(
            item_no=item_no,
            part_name=component["part_name"],
            part_code=component["part_code"],
            quantity=component["quantity"],
            is_salt_malzeme=True
        ))
        item_no += 1
    
    return BOMResult(items=items, total_items=len(items))


@router.post("/generate/step")
async def generate_step_model(config: ConfigurationInput):
    """
    Generate a STEP 3D model for the given configuration.

    Returns STEP file as download.
    """
    validation = run_full_validation(config)
    if not validation.is_valid:
        raise HTTPException(
            status_code=400,
            detail={"message": "Invalid configuration", "errors": [e.dict() for e in validation.errors]}
        )

    try:
        step_bytes = generate_step(config)

        box = get_box_model_by_id(config.box_id)
        filename = f"DRV-{box.id.upper()}-001.step" if box else "model.step"

        return Response(
            content=step_bytes,
            media_type="application/step",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STEP generation failed: {str(e)}")


# ==================== EJC BOX MODELS ====================

@router.get("/ejc/boxes", response_model=list[EJCBoxModel])
async def list_ejc_box_models():
    """Get all available EJC box models"""
    return get_all_ejc_box_models()


@router.get("/ejc/boxes/{box_id}", response_model=EJCBoxModel)
async def get_ejc_box_model(box_id: str):
    """Get a specific EJC box model by ID"""
    box = get_ejc_box_model_by_id(box_id)
    if not box:
        raise HTTPException(status_code=404, detail=f"EJC box model '{box_id}' not found")
    return box


# ==================== LABEL ====================

@router.post("/generate/label")
async def generate_panel_label(label: LabelInput):
    """
    Generate a printable panel label PDF.

    Returns PDF file as download.
    """
    try:
        pdf_bytes = generate_label_pdf(label)
        safe_order = label.order_no.replace("/", "-").replace(" ", "_")
        filename = f"ETIKET-{safe_order}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Label generation failed: {str(e)}")


# ==================== ORDERS ====================

@router.post("/orders", response_model=OrderResponse, status_code=201)
def save_order(order_in: OrderCreate, db: Session = Depends(get_db)):
    """
    Save a configuration as an order record in the database.

    Returns the created order with its assigned ID.
    """
    box = get_box_model_by_id(order_in.box_id)
    if not box:
        raise HTTPException(status_code=404, detail=f"Box model '{order_in.box_id}' not found")

    order = Order(
        name=order_in.name,
        box_id=order_in.box_id,
        terminals=order_in.terminals,
        holes_top=order_in.holes_top,
        holes_bottom=order_in.holes_bottom,
        holes_left=order_in.holes_left,
        holes_right=order_in.holes_right,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/orders", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db)):
    """
    Return all saved orders, newest first.
    """
    return db.query(Order).order_by(Order.created_at.desc()).all()


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Return a single saved order by ID.

    The returned configuration fields can be used to reload the configurator
    state or generate PDF/DXF/STEP outputs.
    """
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    return order
