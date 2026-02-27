"""
Validation Service - Engineering rule enforcement
"""
from typing import List, Tuple
from app.schemas import (
    BoxModel,
    ConfigurationInput,
    ValidationResult,
    ValidationError,
    ValidationWarning,
)
from app.models import (
    COMPONENTS,
    get_box_model_by_id,
    EJC_MIN_EDGE_MARGIN,
    EJC_MIN_HOLE_CLEARANCE,
    get_ejc_box_model_by_id,
)


# Engineering constants
HOLE_DIAMETER = COMPONENTS["HOLE_M20"]["diameter"]
MIN_HOLE_CLEARANCE = COMPONENTS["HOLE_M20"]["clearance"]
MIN_EDGE_MARGIN = 15  # 15mm from box edge
TERMINAL_WIDTH = COMPONENTS["TERMINAL_2_5"]["width"]
RAIL_MARGIN = 20  # 20mm from each side of the rail

# EJC prefix used to detect EJC box IDs
_EJC_PREFIX = "ejc"


def _is_ejc(box_id: str) -> bool:
    return box_id.lower().startswith(_EJC_PREFIX)


def validate_hole_placement(hole_count: int, side_length: float, *, ejc: bool = False) -> Tuple[bool, str, int]:
    """
    Validates if the requested number of holes can physically fit on a side.

    Args:
        hole_count: Number of holes requested.
        side_length: Length of the side in mm.
        ejc: When True, applies EJC-specific tighter tolerances.

    Returns:
        Tuple of (is_valid, error_message, max_possible)
    """
    if hole_count == 0:
        return True, "", 0

    edge_margin = EJC_MIN_EDGE_MARGIN if ejc else MIN_EDGE_MARGIN
    hole_clearance = EJC_MIN_HOLE_CLEARANCE if ejc else MIN_HOLE_CLEARANCE

    available_length = side_length - (2 * edge_margin)
    space_per_hole = HOLE_DIAMETER + hole_clearance
    max_possible = int((available_length + hole_clearance) / space_per_hole)

    if hole_count > max_possible:
        return (
            False,
            f"Fiziksel olarak en fazla {max_possible} adet M20 delik sığar. (Kenar: {side_length}mm)",
            max_possible
        )

    return True, "", max_possible


def validate_terminal_placement(terminal_count: int, box: BoxModel) -> Tuple[bool, str, int]:
    """
    Validates terminal count against rail capacity.
    
    Returns:
        Tuple of (is_valid, error_message, max_possible)
    """
    available_rail_length = box.internal_width - (2 * RAIL_MARGIN)
    max_per_rail = int(available_rail_length / TERMINAL_WIDTH)
    max_total = max_per_rail * box.rail_count
    
    if terminal_count > max_total:
        return (
            False,
            f"Ray kapasitesi aşıldı. Fiziksel maksimum: {max_total} klemens.",
            max_total
        )
    
    if terminal_count > box.max_terminals:
        return (
            False,
            f"Kutu kapasitesi aşıldı. Maksimum: {box.max_terminals} klemens.",
            box.max_terminals
        )
    
    return True, "", box.max_terminals


def run_full_validation(config: ConfigurationInput) -> ValidationResult:
    """
    Runs all validations and returns a complete result.
    Supports both EJB and EJC box types.
    """
    errors: List[ValidationError] = []
    warnings: List[ValidationWarning] = []

    ejc = _is_ejc(config.box_id)

    # Resolve box model (EJC or EJB)
    if ejc:
        box = get_ejc_box_model_by_id(config.box_id)
    else:
        box = get_box_model_by_id(config.box_id)

    if not box:
        return ValidationResult(
            is_valid=False,
            errors=[ValidationError(field="box_id", message=f"Geçersiz kutu modeli: {config.box_id}")],
            warnings=[]
        )
    
    # Hole validations
    hole_validations = [
        ("holes_top", config.holes_top, box.internal_width),
        ("holes_bottom", config.holes_bottom, box.internal_width),
        ("holes_left", config.holes_left, box.internal_length),
        ("holes_right", config.holes_right, box.internal_length),
    ]
    
    for field, count, length in hole_validations:
        is_valid, message, max_possible = validate_hole_placement(count, length, ejc=ejc)
        if not is_valid:
            errors.append(ValidationError(field=field, message=message, max_possible=max_possible))
    
    # Terminal validation
    term_valid, term_message, term_max = validate_terminal_placement(config.terminals, box)
    if not term_valid:
        errors.append(ValidationError(field="terminals", message=term_message, max_possible=term_max))
    
    # Capacity warnings (approaching limits)
    if config.terminals > box.max_terminals * 0.9 and term_valid:
        warnings.append(ValidationWarning(
            field="terminals",
            message="Klemens kapasitesinin %90'ına yaklaştınız."
        ))
    
    total_holes = config.holes_top + config.holes_bottom + config.holes_left + config.holes_right
    max_total_holes = box.max_holes_long * 2 + box.max_holes_short * 2
    if max_total_holes > 0 and total_holes > max_total_holes * 0.9:
        warnings.append(ValidationWarning(
            field="holes",
            message="Toplam delik kapasitesinin %90'ına yaklaştınız."
        ))
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )
