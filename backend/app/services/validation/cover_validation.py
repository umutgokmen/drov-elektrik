"""
Cover element validation - collision and distance checks
"""
from typing import List, Tuple
from app.schemas import CoverElementPlacement, ValidationError, ValidationWarning
from app.models import get_box_model_by_id, get_cover_element_by_id
import math

MIN_EDGE_MARGIN = 15  # mm from panel edge
MIN_ELEMENT_SPACING = 10  # mm between element bezels


def _get_element_radius(element: dict) -> float:
    """Get the effective radius of a cover element for collision checking"""
    if "cutout_diameter" in element:
        return element["bezel_diameter"] / 2
    # Rectangular elements (meters)
    return max(element.get("bezel_width", 0), element.get("bezel_height", 0)) / 2


def validate_cover_elements(
    placements: List[CoverElementPlacement],
    box_id: str,
) -> Tuple[List[ValidationError], List[ValidationWarning]]:
    """
    Validate cover element placements for collisions and boundary violations.

    Returns:
        Tuple of (errors, warnings)
    """
    errors: List[ValidationError] = []
    warnings: List[ValidationWarning] = []

    box = get_box_model_by_id(box_id)
    if not box:
        return errors, warnings

    # Use mounting plate dimensions as the cover area
    cover_w = box.mounting_plate_x
    cover_h = box.mounting_plate_y

    resolved = []
    for i, placement in enumerate(placements):
        elem = get_cover_element_by_id(placement.element_id)
        if not elem:
            errors.append(ValidationError(
                field=f"cover_elements[{i}]",
                message=f"Bilinmeyen kapak elemani: {placement.element_id}",
            ))
            continue
        resolved.append((i, placement, elem))

    # Boundary checks
    for i, placement, elem in resolved:
        radius = _get_element_radius(elem)

        if placement.x - radius < MIN_EDGE_MARGIN:
            errors.append(ValidationError(
                field=f"cover_elements[{i}]",
                message=f"Sol kenara cok yakin ({placement.x:.0f}mm). Min: {MIN_EDGE_MARGIN + radius:.0f}mm",
            ))
        if placement.x + radius > cover_w - MIN_EDGE_MARGIN:
            errors.append(ValidationError(
                field=f"cover_elements[{i}]",
                message=f"Sag kenara cok yakin. Max X: {cover_w - MIN_EDGE_MARGIN - radius:.0f}mm",
            ))
        if placement.y - radius < MIN_EDGE_MARGIN:
            errors.append(ValidationError(
                field=f"cover_elements[{i}]",
                message=f"Ust kenara cok yakin ({placement.y:.0f}mm). Min: {MIN_EDGE_MARGIN + radius:.0f}mm",
            ))
        if placement.y + radius > cover_h - MIN_EDGE_MARGIN:
            errors.append(ValidationError(
                field=f"cover_elements[{i}]",
                message=f"Alt kenara cok yakin. Max Y: {cover_h - MIN_EDGE_MARGIN - radius:.0f}mm",
            ))

    # Collision checks (pairwise)
    for a_idx in range(len(resolved)):
        i_a, p_a, e_a = resolved[a_idx]
        r_a = _get_element_radius(e_a)
        for b_idx in range(a_idx + 1, len(resolved)):
            i_b, p_b, e_b = resolved[b_idx]
            r_b = _get_element_radius(e_b)

            dist = math.sqrt((p_a.x - p_b.x) ** 2 + (p_a.y - p_b.y) ** 2)
            min_dist = r_a + r_b + MIN_ELEMENT_SPACING

            if dist < r_a + r_b:
                errors.append(ValidationError(
                    field=f"cover_elements[{i_a}]",
                    message=f"Eleman {i_a} ve {i_b} cakisiyor! Mesafe: {dist:.1f}mm, min: {r_a + r_b:.1f}mm",
                ))
            elif dist < min_dist:
                warnings.append(ValidationWarning(
                    field=f"cover_elements[{i_a}]",
                    message=f"Eleman {i_a} ve {i_b} arasi cok dar ({dist:.1f}mm). Onerilen min: {min_dist:.1f}mm",
                ))

    return errors, warnings
