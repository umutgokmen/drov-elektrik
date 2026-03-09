"""
Pydantic schemas for the Drawing/CAD API
"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional
from enum import Enum


class BoxModel(BaseModel):
    """Box model schema"""
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

    class Config:
        from_attributes = True


class EJCBoxModel(BaseModel):
    """EJC series box model"""
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
    ip_rating: str = "IP66"
    has_earth_plate: bool = False

    class Config:
        from_attributes = True


class HoleSideInput(BaseModel):
    count: int = Field(0, ge=0)
    size: str = Field("M20")


class ValidationError(BaseModel):
    field: str
    message: str
    max_possible: Optional[int] = None


class ValidationWarning(BaseModel):
    field: str
    message: str


class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []


class HolePosition(BaseModel):
    position: float
    x: Optional[float] = None
    y: Optional[float] = None


class RailLayout(BaseModel):
    id: str
    y: float
    x: float
    width: float
    terminal_count: int


class LayoutResult(BaseModel):
    rails: list[RailLayout]
    holes_top: list[HolePosition]
    holes_bottom: list[HolePosition]
    holes_left: list[HolePosition]
    holes_right: list[HolePosition]


class BOMItem(BaseModel):
    item_no: int
    part_name: str
    part_code: str
    quantity: int
    is_salt_malzeme: bool = False


class BOMResult(BaseModel):
    items: list[BOMItem]
    total_items: int


class SwitchgearPosition(BaseModel):
    component_id: str
    rail_index: int
    x: float
    y: float
    width: float
    height: float
    label: Optional[str] = None


class CoverElementPosition(BaseModel):
    element_id: str
    x: float
    y: float
    cutout_diameter: Optional[float] = None
    cutout_width: Optional[float] = None
    cutout_height: Optional[float] = None
    label: Optional[str] = None


class SwitchgearLayoutResult(BaseModel):
    rails: list[RailLayout]
    holes_top: list[HolePosition]
    holes_bottom: list[HolePosition]
    holes_left: list[HolePosition]
    holes_right: list[HolePosition]
    switchgear_positions: list[SwitchgearPosition] = []
    cover_element_positions: list[CoverElementPosition] = []


class ConfigurationInput(BaseModel):
    box_id: str
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


class SwitchgearConfigurationInput(BaseModel):
    box_id: str
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
    switchgear_rails: list["SwitchgearRailAssignment"] = []
    cover_elements: list["CoverElementPlacement"] = []

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


class SwitchgearComponent(BaseModel):
    component_id: str
    quantity: int = Field(1, ge=1)
    label: Optional[str] = None
    current_rating: Optional[int] = None
    coil_voltage: Optional[int] = None


class SwitchgearRailAssignment(BaseModel):
    rail_index: int = Field(..., ge=0)
    components: list[SwitchgearComponent] = []


class CoverElementPlacement(BaseModel):
    element_id: str
    x: float
    y: float
    label: Optional[str] = None


class OutputFormat(str, Enum):
    PDF = "pdf"
    DXF = "dxf"
    SVG = "svg"


class GenerateRequest(BaseModel):
    configuration: ConfigurationInput
    format: OutputFormat = OutputFormat.PDF
    include_bom: bool = True
    scale: str = "1:2"
    switchgear_rails: list[SwitchgearRailAssignment] = []
    cover_elements: list[CoverElementPlacement] = []


class CADRequest(BaseModel):
    box_id: str
    terminals: int = 0
    holes_top: int = 0
    holes_bottom: int = 0
    holes_left: int = 0
    holes_right: int = 0
    output_format: str = "step"


class LabelSize(str, Enum):
    A6 = "A6"
    A5 = "A5"
    A4 = "A4"


class LabelInput(BaseModel):
    panel_name: str
    order_no: str
    project_name: str = ""
    customer: str = ""
    date: Optional[str] = None
    notes: str = ""
    label_size: LabelSize = LabelSize.A5
