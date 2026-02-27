"""
STEP Dimension Extractor
Parses ISO 10303-21 (STEP/STP) files to extract bounding box dimensions.
All extracted dimensions are in millimeters.
"""
import re
from pathlib import Path
from dataclasses import dataclass


@dataclass
class StepDimensions:
    """Bounding box dimensions extracted from a STEP file."""
    length: float
    width: float
    depth: float
    source_file: str


def extract_cartesian_points(content: str) -> tuple[list[float], list[float], list[float]]:
    """
    Extract all CARTESIAN_POINT coordinates from STEP file content.

    Returns:
        Tuple of (x_values, y_values, z_values) lists.
    """
    pattern = re.compile(
        r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*"
        r"([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)\s*,\s*"
        r"([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)\s*,\s*"
        r"([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)\s*\)"
    )

    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []

    for match in pattern.finditer(content):
        xs.append(float(match.group(1)))
        ys.append(float(match.group(2)))
        zs.append(float(match.group(3)))

    return xs, ys, zs


def extract_dimensions_from_step(file_path: str) -> StepDimensions:
    """
    Extract bounding box dimensions from a STEP file.

    The bounding box is computed from the range of all CARTESIAN_POINT
    coordinates in the file. This gives the overall external envelope.
    Internal cavity dimensions must be derived by subtracting wall thickness
    or by referencing product-specific engineering data.

    Args:
        file_path: Absolute path to the .stp / .step file.

    Returns:
        StepDimensions with length, width and depth in mm.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If no valid coordinate data is found in the file.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"STEP file not found: {file_path}")

    content = path.read_text(encoding="utf-8", errors="ignore")

    xs, ys, zs = extract_cartesian_points(content)

    if not xs:
        raise ValueError(f"No CARTESIAN_POINT data found in: {file_path}")

    x_span = max(xs) - min(xs)
    y_span = max(ys) - min(ys)
    z_span = max(zs) - min(zs)

    # Sort spans descending so length >= width >= depth
    spans = sorted([x_span, y_span, z_span], reverse=True)

    return StepDimensions(
        length=round(spans[0], 1),
        width=round(spans[1], 1),
        depth=round(spans[2], 1),
        source_file=path.name,
    )
