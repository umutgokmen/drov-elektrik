"""
STEP File Parser - Extract enclosure dimensions from STEP files.

Used by issue #27 (EJC integration) to populate EJC box model data once
customer-supplied STEP files are available.
"""
import re
from typing import Dict, Optional


def extract_dimensions_from_step(step_content: str) -> Optional[Dict[str, float]]:
    """
    Parse a STEP AP214/AP242 file and extract bounding box dimensions.

    The parser scans CARTESIAN_POINT entities to determine the axis-aligned
    bounding box of the model. This gives internal_length, internal_width
    and internal_depth values suitable for populating a box model entry.

    Args:
        step_content: Raw text content of the STEP file.

    Returns:
        Dictionary with keys ``internal_length``, ``internal_width``,
        ``internal_depth`` (all floats in mm), or ``None`` when no
        geometry could be extracted.
    """
    # STEP CARTESIAN_POINT: (#nnn, 'label', (x, y, z));
    pattern = re.compile(
        r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*"
        r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*,\s*"
        r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*,\s*"
        r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*\)\s*\)",
        re.IGNORECASE,
    )

    xs, ys, zs = [], [], []
    for match in pattern.finditer(step_content):
        try:
            xs.append(float(match.group(1)))
            ys.append(float(match.group(2)))
            zs.append(float(match.group(3)))
        except ValueError:
            continue

    if not xs:
        return None

    return {
        "internal_length": round(max(xs) - min(xs), 2),
        "internal_width": round(max(ys) - min(ys), 2),
        "internal_depth": round(max(zs) - min(zs), 2),
    }


def extract_dimensions_from_step_file(file_path: str) -> Optional[Dict[str, float]]:
    """
    Convenience wrapper: read a STEP file from disk and return dimensions.

    Args:
        file_path: Absolute path to the STEP file.

    Returns:
        Same as :func:`extract_dimensions_from_step`.

    Raises:
        FileNotFoundError: When the file does not exist.
        OSError: When the file cannot be read.
    """
    with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
        content = fh.read()
    return extract_dimensions_from_step(content)
