"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from enum import Enum


class HoleSideInput(BaseModel):
    """Hole specification for one side"""
    count: int = Field(0, ge=0)
    size: str = Field("M20", description="Hole size: M20, M25, M32, M40, M50")


class EJCBoxModel(BaseModel):
    """EJC series box model with additional EJC-specific properties"""
    id: str
    name: str
    internal_length: float = Field(..., gt=0)
    internal_width: float = Field(..., gt=0)
    internal_depth: float = Field(..., gt=0)
    max_holes_long: int = Field(..., ge=0)
    max_holes_short: int = Field(..., ge=0)
    rail_count: int = Field(..., ge=1)
    max_terminals: int = Field(..., ge=0)
    mounting_plate_x: float
    mounting_plate_y: float
    ip_rating: str = Field("IP66", description="Ingress protection rating")
    has_earth_plate: bool = Field(False, description="Whether the model includes an earth bonding plate")

    class Config:
        from_attributes = True


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


class ConfigurationInput(BaseModel):
    """User configuration input"""
    box_id: str = Field(..., description="Box model ID (e.g., 'ejb21')")
    terminals: int = Field(..., ge=0, description="Number of terminals")
    # Legacy simple hole counts (backward compat)
    holes_top: int = Field(0, ge=0)
    holes_bottom: int = Field(0, ge=0)
    holes_left: int = Field(0, ge=0)
    holes_right: int = Field(0, ge=0)
    # New: per-side hole specs with size
    holes_top_spec: Optional[HoleSideInput] = None
    holes_bottom_spec: Optional[HoleSideInput] = None
    holes_left_spec: Optional[HoleSideInput] = None
    holes_right_spec: Optional[HoleSideInput] = None
    prepared_by: Optional[str] = None
    controlled_by: Optional[str] = None
    controller_id: Optional[int] = None

    @model_validator(mode="after")
    def sync_hole_counts(self):
        """Sync legacy hole counts from spec if spec is provided"""
        if self.holes_top_spec:
            self.holes_top = self.holes_top_spec.count
        if self.holes_bottom_spec:
            self.holes_bottom = self.holes_bottom_spec.count
        if self.holes_left_spec:
            self.holes_left = self.holes_left_spec.count
        if self.holes_right_spec:
            self.holes_right = self.holes_right_spec.count
        return self

    def get_hole_size(self, side: str) -> str:
        spec = getattr(self, f"holes_{side}_spec", None)
        return spec.size if spec else "M20"


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


# ==================== SWITCHGEAR SCHEMAS ====================

class SwitchgearComponent(BaseModel):
    """A single switchgear component placed on a rail"""
    component_id: str = Field(..., description="Catalog ID of the component")
    quantity: int = Field(1, ge=1)
    label: Optional[str] = None
    current_rating: Optional[int] = None
    coil_voltage: Optional[int] = None


class SwitchgearRailAssignment(BaseModel):
    """Components assigned to a specific rail"""
    rail_index: int = Field(..., ge=0, description="0-based rail index")
    components: List[SwitchgearComponent] = []


class CoverElementPlacement(BaseModel):
    """A cover element placed on the panel front"""
    element_id: str = Field(..., description="Catalog ID of the cover element")
    x: float = Field(..., description="X position on cover (mm from left edge)")
    y: float = Field(..., description="Y position on cover (mm from top edge)")
    label: Optional[str] = None


class SwitchgearConfigurationInput(BaseModel):
    """Extended configuration with switchgear and cover elements"""
    box_id: str = Field(..., description="Box model ID")
    terminals: int = Field(0, ge=0)
    holes_top: int = Field(0, ge=0)
    holes_bottom: int = Field(0, ge=0)
    holes_left: int = Field(0, ge=0)
    holes_right: int = Field(0, ge=0)
    holes_top_spec: Optional[HoleSideInput] = None
    holes_bottom_spec: Optional[HoleSideInput] = None
    holes_left_spec: Optional[HoleSideInput] = None
    holes_right_spec: Optional[HoleSideInput] = None
    prepared_by: Optional[str] = None
    controlled_by: Optional[str] = None
    controller_id: Optional[int] = None
    # Switchgear assignments per rail
    switchgear_rails: List[SwitchgearRailAssignment] = []
    # Cover elements
    cover_elements: List[CoverElementPlacement] = []

    @model_validator(mode="after")
    def sync_hole_counts(self):
        if self.holes_top_spec:
            self.holes_top = self.holes_top_spec.count
        if self.holes_bottom_spec:
            self.holes_bottom = self.holes_bottom_spec.count
        if self.holes_left_spec:
            self.holes_left = self.holes_left_spec.count
        if self.holes_right_spec:
            self.holes_right = self.holes_right_spec.count
        return self

    def get_hole_size(self, side: str) -> str:
        spec = getattr(self, f"holes_{side}_spec", None)
        return spec.size if spec else "M20"


class SwitchgearPosition(BaseModel):
    """Calculated position of a switchgear component"""
    component_id: str
    rail_index: int
    x: float
    y: float
    width: float
    height: float
    label: Optional[str] = None


class CoverElementPosition(BaseModel):
    """Calculated position of a cover element"""
    element_id: str
    x: float
    y: float
    cutout_diameter: Optional[float] = None
    cutout_width: Optional[float] = None
    cutout_height: Optional[float] = None
    label: Optional[str] = None


class SwitchgearLayoutResult(BaseModel):
    """Extended layout result with switchgear positions"""
    rails: List[RailLayout]
    holes_top: List[HolePosition]
    holes_bottom: List[HolePosition]
    holes_left: List[HolePosition]
    holes_right: List[HolePosition]
    switchgear_positions: List[SwitchgearPosition] = []
    cover_element_positions: List[CoverElementPosition] = []


# ==================== ORDER / CONFIGURATION HISTORY ====================

class OrderCreate(BaseModel):
    """Request to save a configuration as an order"""
    box_id: str
    terminals: int = 0
    holes_top: int = 0
    holes_bottom: int = 0
    holes_left: int = 0
    holes_right: int = 0
    holes_top_spec: Optional[HoleSideInput] = None
    holes_bottom_spec: Optional[HoleSideInput] = None
    holes_left_spec: Optional[HoleSideInput] = None
    holes_right_spec: Optional[HoleSideInput] = None
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    """Saved order response"""
    id: int
    drawing_number: str
    box_id: str
    terminals: int
    holes_top: int
    holes_bottom: int
    holes_left: int
    holes_right: int
    notes: Optional[str] = None
    created_at: str
    creator_name: Optional[str] = None


class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int


# ==================== LABEL ====================

class LabelSize(str, Enum):
    """Available label sizes"""
    A6 = "A6"
    A5 = "A5"
    A4 = "A4"


class LabelInput(BaseModel):
    """Input for panel label PDF generation"""
    panel_name: str = Field(..., description="Panel name / pano adi")
    order_no: str = Field(..., description="Order number / siparis no")
    project_name: str = Field("", description="Project name / proje adi")
    customer: str = Field("", description="Customer name / musteri adi")
    date: Optional[str] = Field(None, description="Date in DD.MM.YYYY format; defaults to today")
    notes: str = Field("", description="Additional notes / notlar")
    label_size: LabelSize = Field(LabelSize.A5, description="Label paper size")
