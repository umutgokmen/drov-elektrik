"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class BoxModelBase(BaseModel):
    """Base schema for box models"""
    id: str
    name: str
    internal_length: float = Field(..., gt=0, description="Internal length in mm")
    internal_width: float = Field(..., gt=0, description="Internal width in mm")
    internal_depth: float = Field(..., gt=0, description="Internal depth in mm")
    max_holes_long: int = Field(..., ge=0)
    max_holes_short: int = Field(..., ge=0)
    rail_count: int = Field(..., ge=1)
    max_terminals: int = Field(..., ge=0)


class BoxModel(BoxModelBase):
    """Full box model with all properties"""
    mounting_plate_x: float
    mounting_plate_y: float
    
    class Config:
        from_attributes = True


class EJCBoxModel(BoxModelBase):
    """EJC series box model with additional EJC-specific properties"""
    mounting_plate_x: float
    mounting_plate_y: float
    ip_rating: str = Field("IP66", description="Ingress protection rating")
    has_earth_plate: bool = Field(False, description="Whether the model includes an earth bonding plate")

    class Config:
        from_attributes = True


class ConfigurationInput(BaseModel):
    """User configuration input"""
    box_id: str = Field(..., description="Box model ID (e.g., 'ejb21')")
    terminals: int = Field(..., ge=0, description="Number of terminals")
    holes_top: int = Field(0, ge=0, description="Number of M20 holes on top")
    holes_bottom: int = Field(0, ge=0, description="Number of M20 holes on bottom")
    holes_left: int = Field(0, ge=0, description="Number of M20 holes on left")
    holes_right: int = Field(0, ge=0, description="Number of M20 holes on right")


class ValidationError(BaseModel):
    """Single validation error"""
    field: str
    message: str
    max_possible: Optional[int] = None


class ValidationWarning(BaseModel):
    """Single validation warning"""
    field: str
    message: str


class ValidationResult(BaseModel):
    """Complete validation result"""
    is_valid: bool
    errors: List[ValidationError] = []
    warnings: List[ValidationWarning] = []


class GeometryPoint(BaseModel):
    """2D point"""
    x: float
    y: float


class HolePosition(BaseModel):
    """Position of a single hole"""
    position: float  # Distance from edge in mm
    x: Optional[float] = None
    y: Optional[float] = None


class RailLayout(BaseModel):
    """Layout of a single rail"""
    id: str
    y: float  # Vertical position
    x: float  # Horizontal start
    width: float
    terminal_count: int


class LayoutResult(BaseModel):
    """Complete layout calculation result"""
    rails: List[RailLayout]
    holes_top: List[HolePosition]
    holes_bottom: List[HolePosition]
    holes_left: List[HolePosition]
    holes_right: List[HolePosition]


class OutputFormat(str, Enum):
    """Available output formats"""
    PDF = "pdf"
    DXF = "dxf"
    SVG = "svg"


class GenerateRequest(BaseModel):
    """Request for drawing generation"""
    configuration: ConfigurationInput
    format: OutputFormat = OutputFormat.PDF
    include_bom: bool = True
    scale: str = "1:2"


class BOMItem(BaseModel):
    """Single BOM item"""
    item_no: int
    part_name: str
    part_code: str
    quantity: int
    is_salt_malzeme: bool = False


class BOMResult(BaseModel):
    """Bill of Materials result"""
    items: List[BOMItem]
    total_items: int


class LabelSize(str, Enum):
    """Available label sizes"""
    A6 = "A6"
    A5 = "A5"
    A4 = "A4"


class LabelInput(BaseModel):
    """Input for panel label PDF generation"""
    panel_name: str = Field(..., description="Panel name / pano adı")
    order_no: str = Field(..., description="Order number / sipariş no")
    project_name: str = Field("", description="Project name / proje adı")
    customer: str = Field("", description="Customer name / müşteri adı")
    date: Optional[str] = Field(None, description="Date in DD.MM.YYYY format; defaults to today")
    notes: str = Field("", description="Additional notes / notlar")
    label_size: LabelSize = Field(LabelSize.A5, description="Label paper size")
