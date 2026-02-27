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
from app.models import COMPONENTS, HOLE_SIZES, get_box_model_by_id


# Engineering constants
MIN_EDGE_MARGIN = 15  # 15mm from box edge
TERMINAL_WIDTH = COMPONENTS["TERMINAL_2_5"]["width"]
RAIL_MARGIN = 20  # 20mm from each side of the rail


def validate_hole_placement(
    hole_count: int,
    side_length: float,
    hole_size: str = "M20",
) -> Tuple[bool, str, int]:
    """
    Validates if the requested number of holes can physically fit on a side.
    """
    if hole_count == 0:
        return True, "", 0

    size_spec = HOLE_SIZES.get(hole_size, HOLE_SIZES["M20"])
    diameter = size_spec["diameter"]
    clearance = size_spec["clearance"]

    available_length = side_length - (2 * MIN_EDGE_MARGIN)
    space_per_hole = diameter + clearance
    max_possible = int((available_length + clearance) / space_per_hole)

    if hole_count > max_possible:
        return (
            False,
            f"Fiziksel olarak en fazla {max_possible} adet {hole_size} delik sigar. (Kenar: {side_length}mm)",
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
    """
    errors: List[ValidationError] = []
    warnings: List[ValidationWarning] = []
    
    # Get box model
    box = get_box_model_by_id(config.box_id)
    if not box:
        return ValidationResult(
            is_valid=False,
            errors=[ValidationError(field="box_id", message=f"Geçersiz kutu modeli: {config.box_id}")],
            warnings=[]
        )
    
    # Hole validations
    hole_validations = [
        ("holes_top", config.holes_top, box.internal_width, config.get_hole_size("top")),
        ("holes_bottom", config.holes_bottom, box.internal_width, config.get_hole_size("bottom")),
        ("holes_left", config.holes_left, box.internal_length, config.get_hole_size("left")),
        ("holes_right", config.holes_right, box.internal_length, config.get_hole_size("right")),
    ]

    for field, count, length, hole_size in hole_validations:
        is_valid, message, max_possible = validate_hole_placement(count, length, hole_size)
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
    if total_holes > max_total_holes * 0.9:
        warnings.append(ValidationWarning(
            field="holes",
            message="Toplam delik kapasitesinin %90'ına yaklaştınız."
        ))
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )
