"""
Switchgear Layout Algorithm - Auto-placement of components on DIN rails.
"""
from typing import List, Tuple
from app.schemas import (
    SwitchgearRailAssignment,
    SwitchgearComponent,
    SwitchgearPosition,
    RailLayout,
    ValidationError,
    ValidationWarning,
)
from app.models import get_switchgear_by_id, get_box_model_by_id

RAIL_MARGIN = 20  # mm from each side of the rail
COMPONENT_GAP = 2  # mm gap between components on a rail


def calculate_switchgear_positions(
    rail_assignments: List[SwitchgearRailAssignment],
    rails: List[RailLayout],
    box_id: str,
) -> Tuple[List[SwitchgearPosition], List[ValidationError], List[ValidationWarning]]:
    """
    Calculate positions for switchgear components on DIN rails.
    Components are placed left-to-right on each rail.

    Args:
        rail_assignments: Components assigned per rail
        rails: Calculated rail layouts from geometry service
        box_id: Box model ID for dimension reference

    Returns:
        Tuple of (positions, errors, warnings)
    """
    positions: List[SwitchgearPosition] = []
    errors: List[ValidationError] = []
    warnings: List[ValidationWarning] = []

    box = get_box_model_by_id(box_id)
    if not box:
        errors.append(ValidationError(
            field="box_id",
            message=f"Gecersiz kutu modeli: {box_id}",
        ))
        return positions, errors, warnings

    for assignment in rail_assignments:
        if assignment.rail_index >= len(rails):
            errors.append(ValidationError(
                field=f"switchgear_rails[{assignment.rail_index}]",
                message=f"Ray indeksi gecersiz: {assignment.rail_index}. Maksimum: {len(rails) - 1}",
            ))
            continue

        rail = rails[assignment.rail_index]
        available_width = rail.width
        cursor_x = rail.x  # start from rail left edge

        total_width = 0
        for comp_spec in assignment.components:
            comp_data = get_switchgear_by_id(comp_spec.component_id)
            if not comp_data:
                errors.append(ValidationError(
                    field=f"switchgear_rails[{assignment.rail_index}]",
                    message=f"Bilinmeyen bilesen: {comp_spec.component_id}",
                ))
                continue

            comp_width = comp_data["width"]
            comp_height = comp_data["height"]

            for _ in range(comp_spec.quantity):
                if total_width + comp_width > available_width:
                    errors.append(ValidationError(
                        field=f"switchgear_rails[{assignment.rail_index}]",
                        message=(
                            f"Ray {assignment.rail_index} kapasitesi asildi. "
                            f"Toplam: {total_width + comp_width:.1f}mm, "
                            f"Kapasite: {available_width:.1f}mm"
                        ),
                        max_possible=int(available_width),
                    ))
                    break

                positions.append(SwitchgearPosition(
                    component_id=comp_spec.component_id,
                    rail_index=assignment.rail_index,
                    x=cursor_x,
                    y=rail.y - comp_height / 2,
                    width=comp_width,
                    height=comp_height,
                    label=comp_spec.label,
                ))

                cursor_x += comp_width + COMPONENT_GAP
                total_width += comp_width + COMPONENT_GAP

        # Capacity warning
        usage_pct = (total_width / available_width) * 100 if available_width > 0 else 0
        if 80 < usage_pct <= 100:
            warnings.append(ValidationWarning(
                field=f"switchgear_rails[{assignment.rail_index}]",
                message=f"Ray {assignment.rail_index} %{usage_pct:.0f} dolu.",
            ))

    return positions, errors, warnings


def auto_distribute_components(
    components: List[SwitchgearComponent],
    rails: List[RailLayout],
) -> List[SwitchgearRailAssignment]:
    """
    Automatically distribute components across rails using first-fit decreasing.
    Tries to balance load across rails.

    Args:
        components: List of components to place
        rails: Available rail layouts

    Returns:
        List of SwitchgearRailAssignment with optimized distribution
    """
    if not rails or not components:
        return []

    # Expand components by quantity and get their widths
    expanded = []
    for comp in components:
        comp_data = get_switchgear_by_id(comp.component_id)
        if not comp_data:
            continue
        for i in range(comp.quantity):
            expanded.append({
                "component": SwitchgearComponent(
                    component_id=comp.component_id,
                    quantity=1,
                    label=f"{comp.label or comp.component_id}-{i+1}" if comp.quantity > 1 else comp.label,
                    current_rating=comp.current_rating,
                    coil_voltage=comp.coil_voltage,
                ),
                "width": comp_data["width"],
            })

    # Sort by width descending (first-fit decreasing)
    expanded.sort(key=lambda x: x["width"], reverse=True)

    # Initialize rail buckets
    rail_buckets = [
        {"index": i, "remaining": rail.width, "components": []}
        for i, rail in enumerate(rails)
    ]

    # Place each component in the first rail that fits
    for item in expanded:
        placed = False
        for bucket in rail_buckets:
            if bucket["remaining"] >= item["width"] + COMPONENT_GAP:
                bucket["components"].append(item["component"])
                bucket["remaining"] -= item["width"] + COMPONENT_GAP
                placed = True
                break
        if not placed:
            # Place on least full rail (overflow will be caught by validation)
            rail_buckets[-1]["components"].append(item["component"])

    return [
        SwitchgearRailAssignment(
            rail_index=bucket["index"],
            components=bucket["components"],
        )
        for bucket in rail_buckets
        if bucket["components"]
    ]
