"""
Geometry Service - Layout and position calculations
"""
from typing import List
import numpy as np
from app.schemas import (
    BoxModel,
    ConfigurationInput,
    HolePosition,
    RailLayout,
    LayoutResult,
)
from app.models import COMPONENTS, get_box_model_by_id


# Engineering constants
HOLE_DIAMETER = COMPONENTS["HOLE_M20"]["diameter"]
TERMINAL_WIDTH = COMPONENTS["TERMINAL_2_5"]["width"]
MIN_EDGE_MARGIN = 15
RAIL_MARGIN = 20
VERTICAL_MARGIN = 30


def calculate_hole_positions(count: int, side_length: float) -> List[HolePosition]:
    """
    Calculates evenly spaced positions for holes on a side.
    
    Args:
        count: Number of holes
        side_length: Length of the side in mm
        
    Returns:
        List of HolePosition objects
    """
    if count <= 0:
        return []
    
    # Calculate available space (with margins from corners)
    total_internal_space = side_length - (2 * (HOLE_DIAMETER / 2 + 10))
    spacing = total_internal_space / (count + 1)
    
    positions = []
    for i in range(count):
        pos = (i + 1) * spacing + 10 + HOLE_DIAMETER / 2
        positions.append(HolePosition(position=pos))
    
    return positions


def calculate_rail_layout(box: BoxModel, terminal_count: int) -> List[RailLayout]:
    """
    Calculates terminal and rail layout.
    
    Args:
        box: BoxModel instance
        terminal_count: Number of terminals
        
    Returns:
        List of RailLayout objects
    """
    rails = []
    terminals_per_rail = int(np.ceil(terminal_count / box.rail_count)) if terminal_count > 0 else 0
    
    # Calculate rail vertical positions (distributed vertically)
    available_height = box.internal_length - (2 * VERTICAL_MARGIN)
    rail_spacing = available_height / (box.rail_count - 1) if box.rail_count > 1 else 0
    
    for i in range(box.rail_count):
        if box.rail_count > 1:
            y = VERTICAL_MARGIN + i * rail_spacing
        else:
            y = box.internal_length / 2
        
        # Calculate terminals on this rail
        if i == box.rail_count - 1:
            count_on_rail = terminal_count - (i * terminals_per_rail)
        else:
            count_on_rail = min(terminals_per_rail, terminal_count - (i * terminals_per_rail))
        
        count_on_rail = max(0, count_on_rail)
        
        rails.append(RailLayout(
            id=f"rail-{i}",
            y=y,
            x=RAIL_MARGIN,
            width=box.internal_width - (2 * RAIL_MARGIN),
            terminal_count=count_on_rail
        ))
    
    return rails


def calculate_full_layout(config: ConfigurationInput) -> LayoutResult:
    """
    Calculates complete layout for a configuration.
    
    Args:
        config: Configuration input
        
    Returns:
        LayoutResult with all positions
    """
    box = get_box_model_by_id(config.box_id)
    if not box:
        raise ValueError(f"Invalid box model: {config.box_id}")
    
    # Calculate all positions
    rails = calculate_rail_layout(box, config.terminals)
    
    holes_top = calculate_hole_positions(config.holes_top, box.internal_width)
    holes_bottom = calculate_hole_positions(config.holes_bottom, box.internal_width)
    holes_left = calculate_hole_positions(config.holes_left, box.internal_length)
    holes_right = calculate_hole_positions(config.holes_right, box.internal_length)
    
    # Add X/Y coordinates for holes
    for hole in holes_top:
        hole.x = hole.position
        hole.y = -15  # Outside box
    
    for hole in holes_bottom:
        hole.x = hole.position
        hole.y = box.internal_length + 15
    
    for hole in holes_left:
        hole.x = -15
        hole.y = hole.position
    
    for hole in holes_right:
        hole.x = box.internal_width + 15
        hole.y = hole.position
    
    return LayoutResult(
        rails=rails,
        holes_top=holes_top,
        holes_bottom=holes_bottom,
        holes_left=holes_left,
        holes_right=holes_right
    )
