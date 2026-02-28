"""
Multi-Page Professional Technical Drawing Engine
Generates A3 landscape PDF with 5-direction 2D views, cross-sections,
BOM legend, title block, and optional 3D isometric view.

Pages:
  1: Front View + Top View + Right Side View + Dimensions
  2: Left View + Bottom View + Back View (mirrored front)
  3: Section A-A + Section B-B + Internal Layout View
  4: 3D Isometric View (CadQuery SVG or fallback wireframe)

Each page includes:
  - Drawing frame with column/row markers
  - Title block (bottom-right) with DROV branding
"""

import io
import math
import os
import subprocess
import json
from datetime import datetime
from typing import List, Tuple, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdf_canvas

from app.models.box_models import HOLE_SIZES


# -- Constants --
WALL_THICKNESS = 3.0  # mm
A3_WIDTH = 420 * mm
A3_HEIGHT = 297 * mm
PAGE_SIZE = (A3_WIDTH, A3_HEIGHT)
FRAME_MARGIN = 10 * mm

# Line weights
LW_OUTLINE = 1.5
LW_HIDDEN = 0.3
LW_DIMENSION = 0.5
LW_SECTION = 0.8
LW_THIN = 0.25

# Fonts
FONT_DIM = ("Helvetica", 8)
FONT_LABEL = ("Helvetica-Bold", 10)
FONT_TITLE = ("Helvetica-Bold", 14)
FONT_SMALL = ("Helvetica", 6)
FONT_MEDIUM = ("Helvetica", 7)


# ============================================================
# UTILITY HELPERS
# ============================================================

def _drawing_number(box_id: str) -> str:
    year = datetime.now().strftime("%Y")
    seq = box_id.upper().replace("EJB", "")
    return f"DRV-{year}-{seq.zfill(4)}"


def _get_hole_diameter(config, side: str) -> float:
    size_key = config.get_hole_size(side)
    return HOLE_SIZES.get(size_key, HOLE_SIZES["M20"])["diameter"]


def _hole_positions_on_side(count: int, side_length: float) -> List[float]:
    if count <= 0:
        return []
    edge_margin = 15.0
    available = side_length - 2 * edge_margin
    spacing = available / (count + 1)
    return [edge_margin + (i + 1) * spacing for i in range(count)]


# ============================================================
# DRAWING FRAME + MARKERS
# ============================================================

def draw_frame(c, page_w: float, page_h: float, sheet_num: int, total_sheets: int) -> None:
    m = FRAME_MARGIN

    # Outer border
    c.setStrokeColor(colors.black)
    c.setLineWidth(2)
    c.rect(m, m, page_w - 2 * m, page_h - 2 * m)

    # Inner border
    c.setLineWidth(0.5)
    c.rect(m + 2, m + 2, page_w - 2 * m - 4, page_h - 2 * m - 4)

    inner_w = page_w - 2 * m
    inner_h = page_h - 2 * m

    # Column markers (1-8)
    col_w = inner_w / 8
    c.setFont(*FONT_MEDIUM)
    for i in range(8):
        x = m + col_w * (i + 0.5)
        c.drawCentredString(x, page_h - m + 3, str(i + 1))
        c.drawCentredString(x, m - 7, str(i + 1))
        if i > 0:
            c.setLineWidth(LW_THIN)
            tick = 3 * mm
            c.line(m + col_w * i, page_h - m, m + col_w * i, page_h - m - tick)
            c.line(m + col_w * i, m, m + col_w * i, m + tick)

    # Row markers (A-F)
    row_h = inner_h / 6
    for i, letter in enumerate("ABCDEF"):
        y = page_h - m - row_h * (i + 0.5)
        c.drawCentredString(m - 5, y - 2, letter)
        c.drawCentredString(page_w - m + 5, y - 2, letter)
        if i > 0:
            c.setLineWidth(LW_THIN)
            tick = 3 * mm
            c.line(m, page_h - m - row_h * i, m + tick, page_h - m - row_h * i)
            c.line(page_w - m, page_h - m - row_h * i, page_w - m - tick, page_h - m - row_h * i)


# ============================================================
# TITLE BLOCK
# ============================================================

def draw_title_block(
    c,
    page_w: float,
    page_h: float,
    box,
    config,
    sheet_num: int,
    total_sheets: int,
) -> None:
    width = 100 * mm
    height = 40 * mm
    x = page_w - FRAME_MARGIN - width - 2
    y = FRAME_MARGIN + 2

    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(x, y, width, height)

    # Logo section
    logo_w = 28 * mm
    c.setFillColor(colors.Color(0.12, 0.22, 0.38))
    c.rect(x, y, logo_w, height, fill=1, stroke=1)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(x + logo_w / 2, y + height - 14 * mm, "DROV")
    c.setFont("Helvetica", 7)
    c.drawCentredString(x + logo_w / 2, y + height - 19 * mm, "Engineering")

    # Info area
    info_x = x + logo_w + 2 * mm
    info_w = width - logo_w
    c.setFillColor(colors.black)

    row1 = y + height - 9 * mm
    row2 = y + height - 21 * mm
    row3 = y + 11 * mm

    c.setLineWidth(0.5)
    c.line(x + logo_w, row1, x + width, row1)
    c.line(x + logo_w, row2, x + width, row2)
    c.line(x + logo_w, row3, x + width, row3)

    # Vertical divider in bottom row
    mid_x = x + logo_w + info_w * 0.5
    c.line(mid_x, row3, mid_x, y)

    # Top row - prepared/controlled
    c.setFont(*FONT_SMALL)
    c.drawString(info_x, y + height - 5, "Prepared:")
    prepared = getattr(config, "prepared_by", None) or "DROV System"
    c.setFont("Helvetica", 7)
    c.drawString(info_x, row1 + 2, prepared)

    c.setFont(*FONT_SMALL)
    c.drawString(info_x + 32 * mm, y + height - 5, "Controlled:")
    controlled = getattr(config, "controlled_by", None) or "-"
    c.setFont("Helvetica", 7)
    c.drawString(info_x + 32 * mm, row1 + 2, controlled)

    # Date
    c.setFont(*FONT_SMALL)
    c.drawString(info_x + 55 * mm, y + height - 5, "Date:")
    c.setFont("Helvetica", 7)
    c.drawString(info_x + 55 * mm, row1 + 2, datetime.now().strftime("%d.%m.%Y"))

    # Middle row - title
    c.setFont(*FONT_SMALL)
    c.drawString(info_x, row1 - 4, "Title:")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(info_x, row2 + 3, f"{box.name} Configuration Drawing")

    # Bottom row left - drawing number
    c.setFont(*FONT_SMALL)
    c.drawString(info_x, row3 - 4, "Drawing No.")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(info_x, y + 2, _drawing_number(box.id))

    # Bottom row right - scale/sheet
    c.setFont(*FONT_SMALL)
    c.drawString(mid_x + 2, row3 - 4, "Scale:")
    c.setFont("Helvetica", 7)
    c.drawString(mid_x + 2, y + 8, "1:2")
    c.drawString(mid_x + 20 * mm, row3 - 4, f"Sheet: {sheet_num}/{total_sheets}")

    # Notes
    c.setFont(*FONT_SMALL)
    c.drawString(FRAME_MARGIN + 5, FRAME_MARGIN + 8, "* All dimensions in mm")
    c.drawString(FRAME_MARGIN + 5, FRAME_MARGIN + 2, "* Tolerance: +/-0.5mm unless noted")


# ============================================================
# DIMENSION HELPERS
# ============================================================

def draw_horizontal_dim(
    c, x1: float, x2: float, y: float, value: float, offset: float = 12 * mm
) -> None:
    dy = y - offset
    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_DIMENSION)
    c.setDash([])

    # Extension lines
    c.line(x1, y, x1, dy - 2)
    c.line(x2, y, x2, dy - 2)

    # Dimension line
    c.line(x1, dy, x2, dy)

    # Arrowheads
    _draw_arrow(c, x1, dy, 0)
    _draw_arrow(c, x2, dy, math.pi)

    # Text
    c.setFont(*FONT_DIM)
    text = f"{value:.0f}"
    tw = c.stringWidth(text, FONT_DIM[0], FONT_DIM[1])
    mid = (x1 + x2) / 2
    c.setFillColor(colors.white)
    c.rect(mid - tw / 2 - 1, dy - 4, tw + 2, 8, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.drawCentredString(mid, dy - 3, text)


def draw_vertical_dim(
    c, y1: float, y2: float, x: float, value: float, offset: float = 12 * mm
) -> None:
    dx = x + offset
    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_DIMENSION)
    c.setDash([])

    # Extension lines
    c.line(x, y1, dx + 2, y1)
    c.line(x, y2, dx + 2, y2)

    # Dimension line
    c.line(dx, y1, dx, y2)

    # Arrowheads
    _draw_arrow(c, dx, y1, -math.pi / 2)
    _draw_arrow(c, dx, y2, math.pi / 2)

    # Text
    c.setFont(*FONT_DIM)
    text = f"{value:.0f}"
    mid = (y1 + y2) / 2
    c.saveState()
    c.translate(dx + 4, mid)
    c.rotate(90)
    tw = c.stringWidth(text, FONT_DIM[0], FONT_DIM[1])
    c.setFillColor(colors.white)
    c.rect(-tw / 2 - 1, -4, tw + 2, 8, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.drawCentredString(0, -3, text)
    c.restoreState()


def _draw_arrow(c, x: float, y: float, angle: float, length: float = 2.5 * mm) -> None:
    c.setFillColor(colors.black)
    a1 = angle - math.radians(20)
    a2 = angle + math.radians(20)
    p = c.beginPath()
    p.moveTo(x, y)
    p.lineTo(x + length * math.cos(a1), y + length * math.sin(a1))
    p.lineTo(x + length * math.cos(a2), y + length * math.sin(a2))
    p.close()
    c.drawPath(p, fill=1, stroke=0)


# ============================================================
# VIEW LABEL
# ============================================================

def draw_view_label(c, x: float, y: float, label: str) -> None:
    c.setFont(*FONT_LABEL)
    c.setFillColor(colors.black)
    c.drawCentredString(x, y, label)
    # Underline
    tw = c.stringWidth(label, FONT_LABEL[0], FONT_LABEL[1])
    c.setLineWidth(LW_DIMENSION)
    c.line(x - tw / 2, y - 2, x + tw / 2, y - 2)


# ============================================================
# HOLE DRAWING (circle with crosshair - 2D technical style)
# ============================================================

def draw_hole_circle(c, cx: float, cy: float, diameter: float, scale: float) -> None:
    r = (diameter / 2) * scale
    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_OUTLINE)
    c.setDash([])
    c.circle(cx, cy, r, fill=0, stroke=1)
    # Crosshair
    c.setLineWidth(LW_THIN)
    ch = r * 0.6
    c.line(cx - ch, cy, cx + ch, cy)
    c.line(cx, cy - ch, cx, cy + ch)


# ============================================================
# SECTION HATCH PATTERN
# ============================================================

def draw_hatch(c, x: float, y: float, w: float, h: float, gap: float = 2 * mm) -> None:
    c.saveState()
    p = c.beginPath()
    p.rect(x, y, w, h)
    c.clipPath(p, stroke=0)
    c.setStrokeColor(colors.Color(0.6, 0.6, 0.6))
    c.setLineWidth(0.15)
    total = w + h
    steps = int(total / gap) + 2
    for i in range(steps):
        sx = x + i * gap
        c.line(sx, y, sx - h, y + h)
    c.restoreState()


# ============================================================
# MOUNTING PLATE
# ============================================================

def draw_mounting_plate(
    c, origin_x: float, origin_y: float, plate_w: float, plate_h: float, scale: float
) -> None:
    pw = plate_w * scale
    ph = plate_h * scale
    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_HIDDEN)
    c.setDash([3, 2])
    c.rect(origin_x, origin_y, pw, ph)
    c.setDash([])

    # Corner screw holes
    screw_inset = 8 * scale
    screw_r = 2 * scale
    for dx in [screw_inset, pw - screw_inset]:
        for dy in [screw_inset, ph - screw_inset]:
            c.circle(origin_x + dx, origin_y + dy, screw_r, fill=0, stroke=1)


# ============================================================
# FRONT VIEW (Width x Depth)
# ============================================================

def draw_front_view(
    c, ox: float, oy: float, box, config, layout, scale: float
) -> None:
    W = box.internal_width * scale
    D = box.internal_depth * scale
    wall = WALL_THICKNESS * scale

    # Outer box
    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_OUTLINE)
    c.setDash([])
    c.rect(ox, oy, W, D)

    # Inner cavity
    c.setLineWidth(LW_HIDDEN)
    c.setDash([3, 2])
    c.rect(ox + wall, oy + wall, W - 2 * wall, D - 2 * wall)
    c.setDash([])

    # Top holes
    hole_d_top = _get_hole_diameter(config, "top")
    for hp in layout.holes_top:
        hx = ox + hp.position * scale
        hy = oy + D  # top edge of front view
        draw_hole_circle(c, hx, hy, hole_d_top, scale)

    # Bottom holes
    hole_d_bot = _get_hole_diameter(config, "bottom")
    for hp in layout.holes_bottom:
        hx = ox + hp.position * scale
        hy = oy  # bottom edge
        draw_hole_circle(c, hx, hy, hole_d_bot, scale)

    # Section line A-A (horizontal through mid-depth)
    mid_y = oy + D / 2
    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_SECTION)
    c.setDash([8, 3, 2, 3])
    c.line(ox - 8 * mm, mid_y, ox + W + 8 * mm, mid_y)
    c.setDash([])
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(ox - 12 * mm, mid_y - 3, "A")
    c.drawCentredString(ox + W + 12 * mm, mid_y - 3, "A")

    # Dimensions
    draw_horizontal_dim(c, ox, ox + W, oy, box.internal_width)
    draw_vertical_dim(c, oy, oy + D, ox + W, box.internal_depth)

    # Label
    draw_view_label(c, ox + W / 2, oy - 18 * mm, "FRONT VIEW")


# ============================================================
# TOP VIEW (Width x Length) - looking down
# ============================================================

def draw_top_view(
    c, ox: float, oy: float, box, config, layout, scale: float
) -> None:
    W = box.internal_width * scale
    L = box.internal_length * scale
    wall = WALL_THICKNESS * scale

    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_OUTLINE)
    c.setDash([])
    c.rect(ox, oy, W, L)

    # Inner cavity
    c.setLineWidth(LW_HIDDEN)
    c.setDash([3, 2])
    c.rect(ox + wall, oy + wall, W - 2 * wall, L - 2 * wall)
    c.setDash([])

    # Mounting plate
    if hasattr(box, "mounting_plate_x") and hasattr(box, "mounting_plate_y"):
        mp_w = box.mounting_plate_x * scale
        mp_h = box.mounting_plate_y * scale
        mp_ox = ox + (W - mp_w) / 2
        mp_oy = oy + (L - mp_h) / 2
        draw_mounting_plate(c, mp_ox, mp_oy, box.mounting_plate_x, box.mounting_plate_y, scale)

    # DIN Rails (horizontal lines)
    for rail in layout.rails:
        ry = oy + rail.y * scale
        rx = ox + rail.x * scale
        rw = rail.width * scale
        c.setStrokeColor(colors.Color(0.5, 0.5, 0.5))
        c.setLineWidth(0.75)
        c.setDash([])
        c.rect(rx, ry - 2.5 * scale, rw, 5 * scale)

        # Terminals
        tw = 5.2 * scale
        th = 10 * scale
        for t in range(rail.terminal_count):
            tx = rx + 5 * scale + t * (tw + 0.5 * scale)
            if tx + tw > rx + rw - 5 * scale:
                break
            c.setStrokeColor(colors.Color(0.4, 0.4, 0.4))
            c.setLineWidth(LW_THIN)
            c.rect(tx, ry - th / 2, tw, th)

    # Left holes (on left edge of top view)
    hole_d_left = _get_hole_diameter(config, "left")
    for hp in layout.holes_left:
        hy = oy + hp.position * scale
        hx = ox
        draw_hole_circle(c, hx, hy, hole_d_left, scale)

    # Right holes
    hole_d_right = _get_hole_diameter(config, "right")
    for hp in layout.holes_right:
        hy = oy + hp.position * scale
        hx = ox + W
        draw_hole_circle(c, hx, hy, hole_d_right, scale)

    # Section line B-B (vertical through mid-width)
    mid_x = ox + W / 2
    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_SECTION)
    c.setDash([8, 3, 2, 3])
    c.line(mid_x, oy - 6 * mm, mid_x, oy + L + 6 * mm)
    c.setDash([])
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(mid_x, oy - 10 * mm, "B")
    c.drawCentredString(mid_x, oy + L + 8 * mm, "B")

    # Dimensions
    draw_horizontal_dim(c, ox, ox + W, oy + L, box.internal_width, offset=-10 * mm)
    draw_vertical_dim(c, oy, oy + L, ox, box.internal_length, offset=-12 * mm)

    # Label
    draw_view_label(c, ox + W / 2, oy + L + 14 * mm, "TOP VIEW")


# ============================================================
# RIGHT SIDE VIEW (Length x Depth)
# ============================================================

def draw_right_view(
    c, ox: float, oy: float, box, config, layout, scale: float
) -> None:
    L = box.internal_length * scale
    D = box.internal_depth * scale
    wall = WALL_THICKNESS * scale

    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_OUTLINE)
    c.setDash([])
    c.rect(ox, oy, L, D)

    c.setLineWidth(LW_HIDDEN)
    c.setDash([3, 2])
    c.rect(ox + wall, oy + wall, L - 2 * wall, D - 2 * wall)
    c.setDash([])

    # Right-side holes
    hole_d_right = _get_hole_diameter(config, "right")
    for hp in layout.holes_right:
        hx = ox + hp.position * scale
        hy = oy + D / 2
        draw_hole_circle(c, hx, hy, hole_d_right, scale)

    # DIN Rails shown as horizontal hidden lines
    for rail in layout.rails:
        ry = oy + D * 0.6  # approximate vertical position of rails in side view
        c.setStrokeColor(colors.Color(0.6, 0.6, 0.6))
        c.setLineWidth(LW_HIDDEN)
        c.setDash([2, 2])
        rail_y_pos = oy + rail.y * scale * (D / (box.internal_length * scale))
        c.line(ox + wall, rail_y_pos, ox + L - wall, rail_y_pos)
    c.setDash([])

    # Dimensions
    draw_horizontal_dim(c, ox, ox + L, oy, box.internal_length)
    draw_vertical_dim(c, oy, oy + D, ox + L, box.internal_depth)

    draw_view_label(c, ox + L / 2, oy - 18 * mm, "RIGHT VIEW")


# ============================================================
# LEFT SIDE VIEW (Length x Depth)
# ============================================================

def draw_left_view(
    c, ox: float, oy: float, box, config, layout, scale: float
) -> None:
    L = box.internal_length * scale
    D = box.internal_depth * scale
    wall = WALL_THICKNESS * scale

    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_OUTLINE)
    c.setDash([])
    c.rect(ox, oy, L, D)

    c.setLineWidth(LW_HIDDEN)
    c.setDash([3, 2])
    c.rect(ox + wall, oy + wall, L - 2 * wall, D - 2 * wall)
    c.setDash([])

    # Left-side holes
    hole_d_left = _get_hole_diameter(config, "left")
    for hp in layout.holes_left:
        hx = ox + hp.position * scale
        hy = oy + D / 2
        draw_hole_circle(c, hx, hy, hole_d_left, scale)

    # DIN Rails as hidden lines
    for rail in layout.rails:
        c.setStrokeColor(colors.Color(0.6, 0.6, 0.6))
        c.setLineWidth(LW_HIDDEN)
        c.setDash([2, 2])
        rail_y_pos = oy + rail.y * scale * (D / (box.internal_length * scale))
        c.line(ox + wall, rail_y_pos, ox + L - wall, rail_y_pos)
    c.setDash([])

    draw_horizontal_dim(c, ox, ox + L, oy, box.internal_length)
    draw_vertical_dim(c, oy, oy + D, ox + L, box.internal_depth)

    draw_view_label(c, ox + L / 2, oy - 18 * mm, "LEFT VIEW")


# ============================================================
# BOTTOM VIEW (Width x Length)
# ============================================================

def draw_bottom_view(
    c, ox: float, oy: float, box, config, layout, scale: float
) -> None:
    W = box.internal_width * scale
    L = box.internal_length * scale
    wall = WALL_THICKNESS * scale

    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_OUTLINE)
    c.setDash([])
    c.rect(ox, oy, W, L)

    c.setLineWidth(LW_HIDDEN)
    c.setDash([3, 2])
    c.rect(ox + wall, oy + wall, W - 2 * wall, L - 2 * wall)
    c.setDash([])

    # Drain valve marker (center bottom)
    drain_x = ox + W / 2
    drain_y = oy + L / 2
    c.setLineWidth(LW_OUTLINE)
    c.setDash([])
    c.circle(drain_x, drain_y, 10 * scale, fill=0, stroke=1)
    c.setFont(*FONT_SMALL)
    c.drawCentredString(drain_x, drain_y - 3, "DRAIN")

    draw_horizontal_dim(c, ox, ox + W, oy, box.internal_width)
    draw_vertical_dim(c, oy, oy + L, ox + W, box.internal_length)

    draw_view_label(c, ox + W / 2, oy + L + 10 * mm, "BOTTOM VIEW")


# ============================================================
# BACK VIEW (Width x Depth) - mirrored front
# ============================================================

def draw_back_view(
    c, ox: float, oy: float, box, config, layout, scale: float
) -> None:
    W = box.internal_width * scale
    D = box.internal_depth * scale
    wall = WALL_THICKNESS * scale

    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_OUTLINE)
    c.setDash([])
    c.rect(ox, oy, W, D)

    c.setLineWidth(LW_HIDDEN)
    c.setDash([3, 2])
    c.rect(ox + wall, oy + wall, W - 2 * wall, D - 2 * wall)
    c.setDash([])

    # Back holes are mirrored front holes (top->top, bottom->bottom, reversed x)
    hole_d_top = _get_hole_diameter(config, "top")
    for hp in layout.holes_top:
        # Mirror: x position is reversed
        hx = ox + W - hp.position * scale
        hy = oy + D
        draw_hole_circle(c, hx, hy, hole_d_top, scale)

    hole_d_bot = _get_hole_diameter(config, "bottom")
    for hp in layout.holes_bottom:
        hx = ox + W - hp.position * scale
        hy = oy
        draw_hole_circle(c, hx, hy, hole_d_bot, scale)

    draw_horizontal_dim(c, ox, ox + W, oy, box.internal_width)
    draw_vertical_dim(c, oy, oy + D, ox + W, box.internal_depth)

    draw_view_label(c, ox + W / 2, oy - 18 * mm, "BACK VIEW (REAR)")


# ============================================================
# SECTION A-A (Horizontal cut - Width x Length at mid-depth)
# ============================================================

def draw_section_aa(
    c, ox: float, oy: float, box, config, layout, scale: float
) -> None:
    W = box.internal_width * scale
    L = box.internal_length * scale
    wall = WALL_THICKNESS * scale

    # Outer wall
    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_OUTLINE)
    c.setDash([])
    c.rect(ox, oy, W, L)

    # Inner cavity
    c.rect(ox + wall, oy + wall, W - 2 * wall, L - 2 * wall)

    # Hatch the cut walls
    draw_hatch(c, ox, oy, wall, L)  # left wall
    draw_hatch(c, ox + W - wall, oy, wall, L)  # right wall
    draw_hatch(c, ox + wall, oy, W - 2 * wall, wall)  # bottom wall
    draw_hatch(c, ox + wall, oy + L - wall, W - 2 * wall, wall)  # top wall

    # DIN Rails
    for rail in layout.rails:
        ry = oy + rail.y * scale
        rx = ox + rail.x * scale
        rw = rail.width * scale
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.5)
        c.setFillColor(colors.Color(0.9, 0.9, 0.9))
        c.rect(rx, ry - 2 * scale, rw, 4 * scale, fill=1, stroke=1)

        # Terminals
        tw = 5.2 * scale
        th = 12 * scale
        c.setFillColor(colors.white)
        for t in range(rail.terminal_count):
            tx = rx + 3 * scale + t * (tw + 0.3 * scale)
            if tx + tw > rx + rw - 3 * scale:
                break
            c.rect(tx, ry - th / 2, tw, th, fill=1, stroke=1)

    # Mounting plate outline
    if hasattr(box, "mounting_plate_x") and hasattr(box, "mounting_plate_y"):
        draw_mounting_plate(
            c,
            ox + (W - box.mounting_plate_x * scale) / 2,
            oy + (L - box.mounting_plate_y * scale) / 2,
            box.mounting_plate_x,
            box.mounting_plate_y,
            scale,
        )

    draw_view_label(c, ox + W / 2, oy + L + 10 * mm, "SECTION A-A")


# ============================================================
# SECTION B-B (Vertical cut - Width x Depth at mid-length)
# ============================================================

def draw_section_bb(
    c, ox: float, oy: float, box, config, layout, scale: float
) -> None:
    W = box.internal_width * scale
    D = box.internal_depth * scale
    wall = WALL_THICKNESS * scale

    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_OUTLINE)
    c.setDash([])
    c.rect(ox, oy, W, D)

    # Inner cavity
    c.rect(ox + wall, oy + wall, W - 2 * wall, D - 2 * wall)

    # Hatch cut walls
    draw_hatch(c, ox, oy, wall, D)  # left
    draw_hatch(c, ox + W - wall, oy, wall, D)  # right
    draw_hatch(c, ox + wall, oy, W - 2 * wall, wall)  # bottom
    draw_hatch(c, ox + wall, oy + D - wall, W - 2 * wall, wall)  # top

    # Rails shown as rectangles (cross-section)
    rail_count = box.rail_count
    inner_w = W - 2 * wall
    rail_spacing = inner_w / (rail_count + 1)
    rail_section_h = 7.5 * scale  # DIN rail depth
    rail_section_w = 35 * scale  # DIN rail width (35mm standard)

    # Rails are attached to mounting plate; show in cross-section at base
    mount_y = oy + wall + 15 * scale  # approximate mounting plate position from bottom

    for i in range(rail_count):
        rx = ox + wall + rail_spacing * (i + 1) - rail_section_w / 2
        c.setFillColor(colors.Color(0.85, 0.87, 0.9))
        c.setStrokeColor(colors.Color(0.5, 0.5, 0.5))
        c.setLineWidth(0.5)
        c.rect(rx, mount_y, rail_section_w, rail_section_h, fill=1, stroke=1)

        # Terminals on rail (side profile)
        term_w = 5.2 * scale
        term_h = 47 * scale
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.black)
        c.setLineWidth(LW_THIN)
        rx_center = rx + rail_section_w / 2
        c.rect(
            rx_center - term_w / 2,
            mount_y + rail_section_h,
            term_w,
            min(term_h, D - 2 * wall - 15 * scale - rail_section_h),
            fill=1,
            stroke=1,
        )

    draw_view_label(c, ox + W / 2, oy + D + 10 * mm, "SECTION B-B")


# ============================================================
# INTERNAL LAYOUT VIEW (Top-down, showing rails + terminals)
# ============================================================

def _draw_switchgear_on_rails(
    c, ox: float, oy: float, layout, switchgear_positions: list, scale: float
) -> None:
    """Draw switchgear components on rails in top-down view."""
    if not switchgear_positions:
        return
    from app.models import get_switchgear_by_id

    sw_colors = {
        "fuse": colors.Color(0.9, 0.6, 0.2),
        "mcb": colors.Color(0.3, 0.5, 0.8),
        "relay": colors.Color(0.6, 0.3, 0.7),
        "contactor": colors.Color(0.2, 0.6, 0.5),
        "switch": colors.Color(0.7, 0.7, 0.3),
        "terminal": colors.Color(0.5, 0.7, 0.5),
        "surge_protector": colors.Color(0.8, 0.4, 0.4),
        "timer": colors.Color(0.4, 0.6, 0.8),
        "power_supply": colors.Color(0.6, 0.6, 0.3),
    }

    for pos in switchgear_positions:
        comp = get_switchgear_by_id(pos.component_id)
        cat = comp.get("category", "") if comp else ""
        fill = sw_colors.get(cat, colors.Color(0.7, 0.7, 0.7))

        px = ox + pos.x * scale
        py = oy + pos.y * scale - (pos.height * scale) / 2
        pw = pos.width * scale
        ph = pos.height * scale

        c.setFillColor(fill)
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.4)
        c.rect(px, py, pw, ph, fill=1, stroke=1)

        if pos.label:
            c.setFont("Helvetica", max(3, min(5, pw * 0.6)))
            c.setFillColor(colors.black)
            c.drawCentredString(px + pw / 2, py + ph / 2 - 1.5, pos.label[:4])


def draw_internal_view(
    c, ox: float, oy: float, box, config, layout, scale: float,
    switchgear_positions: list | None = None
) -> None:
    W = box.internal_width * scale
    L = box.internal_length * scale
    wall = WALL_THICKNESS * scale

    # Box outline
    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_OUTLINE)
    c.setDash([])
    c.rect(ox, oy, W, L)

    # Internal area
    c.setFillColor(colors.Color(0.98, 0.98, 0.98))
    c.rect(ox + wall, oy + wall, W - 2 * wall, L - 2 * wall, fill=1, stroke=1)

    # Mounting plate
    if hasattr(box, "mounting_plate_x") and hasattr(box, "mounting_plate_y"):
        mp_w = box.mounting_plate_x * scale
        mp_h = box.mounting_plate_y * scale
        mp_ox = ox + (W - mp_w) / 2
        mp_oy = oy + (L - mp_h) / 2
        c.setStrokeColor(colors.Color(0.7, 0.7, 0.7))
        c.setLineWidth(0.5)
        c.setDash([4, 2])
        c.rect(mp_ox, mp_oy, mp_w, mp_h)
        c.setDash([])

    # DIN Rails
    for rail in layout.rails:
        ry = oy + rail.y * scale
        rx = ox + rail.x * scale
        rw = rail.width * scale
        c.setStrokeColor(colors.Color(0.5, 0.5, 0.5))
        c.setLineWidth(0.75)
        c.setFillColor(colors.Color(0.9, 0.91, 0.93))
        c.rect(rx, ry - 3 * scale, rw, 6 * scale, fill=1, stroke=1)

        # Terminals
        tw = 5.2 * scale
        th = 10 * scale
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.Color(0.3, 0.3, 0.3))
        c.setLineWidth(LW_THIN)
        for t in range(rail.terminal_count):
            tx = rx + 3 * scale + t * (tw + 0.3 * scale)
            if tx + tw > rx + rw - 3 * scale:
                break
            c.rect(tx, ry - th / 2, tw, th, fill=1, stroke=1)

    # Hole positions as circles on edges
    hole_d_top = _get_hole_diameter(config, "top")
    for hp in layout.holes_top:
        draw_hole_circle(c, ox + hp.position * scale, oy + L, hole_d_top, scale)

    hole_d_bot = _get_hole_diameter(config, "bottom")
    for hp in layout.holes_bottom:
        draw_hole_circle(c, ox + hp.position * scale, oy, hole_d_bot, scale)

    hole_d_left = _get_hole_diameter(config, "left")
    for hp in layout.holes_left:
        draw_hole_circle(c, ox, oy + hp.position * scale, hole_d_left, scale)

    hole_d_right = _get_hole_diameter(config, "right")
    for hp in layout.holes_right:
        draw_hole_circle(c, ox + W, oy + hp.position * scale, hole_d_right, scale)

    # Switchgear components on rails
    if switchgear_positions:
        _draw_switchgear_on_rails(c, ox, oy, layout, switchgear_positions, scale)

    draw_view_label(c, ox + W / 2, oy + L + 10 * mm, "INTERNAL LAYOUT")


# ============================================================
# BOM / PARTS LIST LEGEND
# ============================================================

def draw_bom(c, x: float, y: float, box, config, layout, switchgear_positions: list | None = None) -> None:
    row_h = 5 * mm
    col_widths = [10 * mm, 10 * mm, 55 * mm, 18 * mm]
    total_w = sum(col_widths)

    total_holes = config.holes_top + config.holes_bottom + config.holes_left + config.holes_right

    # Collect unique hole sizes for BOM
    hole_entries = []
    for side in ["top", "bottom", "left", "right"]:
        count = getattr(config, f"holes_{side}", 0)
        if count > 0:
            size_key = config.get_hole_size(side)
            hole_entries.append((count, size_key))

    # Merge same sizes
    size_counts = {}
    for cnt, sz in hole_entries:
        size_counts[sz] = size_counts.get(sz, 0) + cnt

    parts = [
        (1, 1, f"{box.name} Enclosure", f"P+F-{box.id.upper()}"),
        (2, 1, "Enclosure Cover", f"CVR-{box.id.upper()}"),
    ]
    item_no = 3

    if box.rail_count > 0:
        parts.append((item_no, box.rail_count, "NS 35 DIN Rail", "NS35-DIN"))
        item_no += 1

    if config.terminals > 0:
        parts.append((item_no, config.terminals, "UT 2,5 Terminal Block", "PHX-UT2.5"))
        item_no += 1
        parts.append((item_no, 2, "End Stop CLIPFIX 35-5", "CF35-5"))
        item_no += 1

    for sz, cnt in size_counts.items():
        info = HOLE_SIZES.get(sz, HOLE_SIZES["M20"])
        parts.append((item_no, cnt, info["name"], info["code"]))
        item_no += 1

    parts.append((item_no, 1, "Drain Valve M20x1.5", "DRN-M20"))
    item_no += 1

    if hasattr(box, "mounting_plate_x"):
        parts.append((item_no, 1, "Mounting Plate", f"MP-{box.id.upper()}"))
        item_no += 1

    # Switchgear components
    if switchgear_positions:
        from app.models import get_switchgear_by_id
        sw_counts: dict[str, int] = {}
        for pos in switchgear_positions:
            sw_counts[pos.component_id] = sw_counts.get(pos.component_id, 0) + 1
        for comp_id, qty in sw_counts.items():
            comp = get_switchgear_by_id(comp_id)
            if comp:
                parts.append((item_no, qty, comp["name"][:30], comp_id.upper()))
                item_no += 1

    # Header
    c.setFillColor(colors.Color(0.88, 0.88, 0.88))
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.75)
    c.rect(x, y, total_w, row_h, fill=1, stroke=1)

    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(colors.black)
    c.drawCentredString(x + total_w / 2, y + 1.5, "PARTS LIST / BOM")

    # Column headers
    hdr_y = y - row_h
    c.setFillColor(colors.Color(0.93, 0.93, 0.93))
    c.rect(x, hdr_y, total_w, row_h, fill=1, stroke=1)

    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(colors.black)
    cx = x
    for label, cw in zip(["Item", "Qty", "Description", "Part Code"], col_widths):
        c.drawCentredString(cx + cw / 2, hdr_y + 1.5, label)
        cx += cw

    # Vertical lines through all rows
    total_rows = len(parts) + 2  # header + col header + data
    bottom_y = hdr_y - len(parts) * row_h
    cx = x
    for cw in col_widths:
        c.setLineWidth(0.3)
        c.line(cx, y + row_h, cx, bottom_y)
        cx += cw
    c.line(x + total_w, y + row_h, x + total_w, bottom_y)

    # Data rows
    c.setFont("Helvetica", 6)
    for idx, (item, qty, desc, code) in enumerate(parts):
        ry = hdr_y - (idx + 1) * row_h
        c.rect(x, ry, total_w, row_h, fill=0, stroke=1)
        cx = x
        c.drawCentredString(cx + col_widths[0] / 2, ry + 1.5, str(item))
        cx += col_widths[0]
        c.drawCentredString(cx + col_widths[1] / 2, ry + 1.5, str(qty))
        cx += col_widths[1]
        c.drawString(cx + 1.5, ry + 1.5, desc[:30])
        cx += col_widths[2]
        c.drawString(cx + 1.5, ry + 1.5, code[:12])


# ============================================================
# 3D ISOMETRIC VIEW (CadQuery SVG or fallback wireframe)
# ============================================================

def draw_isometric_view(
    c, ox: float, oy: float, box, config, scale: float
) -> None:
    """Draw isometric wireframe as fallback 3D view."""
    W = box.internal_width * scale
    L = box.internal_length * scale
    D = box.internal_depth * scale

    cos30 = math.cos(math.radians(30))
    sin30 = math.sin(math.radians(30))

    def iso(x: float, y: float, z: float) -> Tuple[float, float]:
        px = ox + (x - z) * cos30
        py = oy + y + (x + z) * sin30
        return (px, py)

    # Front face
    p1 = iso(0, 0, 0)
    p2 = iso(W, 0, 0)
    p3 = iso(W, D, 0)
    p4 = iso(0, D, 0)

    # Back face
    p5 = iso(0, 0, L)
    p6 = iso(W, 0, L)
    p7 = iso(W, D, L)
    p8 = iso(0, D, L)

    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_OUTLINE)
    c.setDash([])

    # Visible edges (front face)
    for a, b in [(p1, p2), (p2, p3), (p3, p4), (p4, p1)]:
        c.line(a[0], a[1], b[0], b[1])

    # Top face
    for a, b in [(p4, p8), (p3, p7), (p8, p7)]:
        c.line(a[0], a[1], b[0], b[1])

    # Right face
    for a, b in [(p2, p6), (p6, p7)]:
        c.line(a[0], a[1], b[0], b[1])

    # Hidden edges
    c.setLineWidth(LW_HIDDEN)
    c.setDash([2, 2])
    for a, b in [(p1, p5), (p5, p6), (p5, p8)]:
        c.line(a[0], a[1], b[0], b[1])
    c.setDash([])

    # Hole indicators on front face (top edge)
    hole_d_top = _get_hole_diameter(config, "top")
    for hp in _hole_positions_on_side(config.holes_top, box.internal_width):
        hx = hp * scale
        # Position on top edge of front face
        pt = iso(hx, D, 0)
        r = (hole_d_top / 2) * scale * 0.5
        c.setLineWidth(LW_THIN)
        c.circle(pt[0], pt[1], r, fill=0, stroke=1)

    draw_view_label(c, ox, oy - 15 * mm, "3D ISOMETRIC VIEW")


def try_cadquery_svg(
    c, ox: float, oy: float, width: float, box, config
) -> bool:
    """
    Attempt to render CadQuery-generated SVG into the PDF.
    Returns True on success, False on failure.
    """
    import re

    _backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    script_path = os.path.join(_backend_dir, "generate_cad.py")
    if not os.path.exists(script_path):
        return False

    config_data = json.dumps(
        {
            "width": box.internal_width,
            "length": box.internal_length,
            "depth": box.internal_depth,
            "holes_bottom": config.holes_bottom,
            "holes_top": config.holes_top,
        }
    )

    conda_python = os.path.expanduser("~/miniconda3/envs/cadquery/bin/python")
    if not os.path.exists(conda_python):
        return False

    my_env = os.environ.copy()
    my_env.pop("PYTHONPATH", None)

    try:
        subprocess.run(
            [conda_python, script_path, config_data],
            check=True,
            capture_output=True,
            cwd=os.path.dirname(script_path),
            env=my_env,
            timeout=30,
        )
    except Exception:
        return False

    svg_path = os.path.join(os.path.dirname(script_path), "cad_output.svg")
    if not os.path.exists(svg_path):
        return False

    try:
        _render_svg_to_canvas(c, svg_path, ox, oy, width)
        return True
    except Exception:
        return False


def _render_svg_to_canvas(
    c, svg_file: str, cx: float, cy: float, width: float
) -> None:
    """Parse CadQuery SVG and render paths onto ReportLab canvas."""
    import re

    with open(svg_file, "r") as f:
        content = f.read()

    sx, sy = 1.0, -1.0
    tx, ty = 0.0, 0.0

    scale_match = re.search(r"scale\(([^,)]+)(?:,\s*([^)]+))?\)", content)
    trans_match = re.search(r"translate\(([^,)]+)(?:,\s*([^)]+))?\)", content)

    if scale_match:
        sx = float(scale_match.group(1))
        sy = float(scale_match.group(2)) if scale_match.group(2) else sx

    if trans_match:
        tx = float(trans_match.group(1))
        ty = float(trans_match.group(2)) if trans_match.group(2) else 0.0

    vb_match = re.search(r'viewBox="([^"]+)"', content)
    vw, vh = 1000.0, 750.0
    if vb_match:
        parts = vb_match.group(1).split()
        if len(parts) == 4:
            vw, vh = float(parts[2]), float(parts[3])

    pdf_scale = width / vw
    offset_x = cx - (vw * pdf_scale) / 2
    offset_y = cy + (vh * pdf_scale) / 2

    path_pattern = re.compile(r"<path([^>]+)>")
    d_pattern = re.compile(r'd="([^"]+)"')

    c.setLineWidth(0.3)

    for match in path_pattern.finditer(content):
        attrs = match.group(1)
        d_match = d_pattern.search(attrs)
        if not d_match:
            continue
        d = d_match.group(1)

        is_hidden = "stroke-dasharray" in attrs or "rgb(100,100,100)" in attrs
        if is_hidden:
            c.setStrokeColor(colors.Color(0.6, 0.6, 0.6))
            c.setDash([2, 1])
        else:
            c.setStrokeColor(colors.black)
            c.setDash([])

        p = c.beginPath()
        tokens = re.findall(
            r"([MmLlCcZz])|([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)", d
        )

        flat = []
        for t in tokens:
            if t[0]:
                flat.append(t[0])
            elif t[1] and t[1].strip():
                flat.append(float(t[1]))

        def transform_pt(px: float, py: float) -> Tuple[float, float]:
            gx = px * sx + tx
            gy = py * sy + ty
            return gx * pdf_scale + offset_x, offset_y + gy * pdf_scale

        i = 0
        last_cmd = "M"
        while i < len(flat):
            cmd = flat[i]
            if isinstance(cmd, str):
                last_cmd = cmd
                i += 1
                if last_cmd == "Z":
                    p.close()
                continue

            if last_cmd == "M" and i + 1 < len(flat):
                fx, fy = transform_pt(flat[i], flat[i + 1])
                p.moveTo(fx, fy)
                i += 2
                last_cmd = "L"
            elif last_cmd == "L" and i + 1 < len(flat):
                fx, fy = transform_pt(flat[i], flat[i + 1])
                p.lineTo(fx, fy)
                i += 2
            elif last_cmd == "C" and i + 5 < len(flat):
                pts = [transform_pt(flat[i + j], flat[i + j + 1]) for j in range(0, 6, 2)]
                p.curveTo(pts[0][0], pts[0][1], pts[1][0], pts[1][1], pts[2][0], pts[2][1])
                i += 6
            else:
                i += 1

        c.drawPath(p, stroke=1, fill=0)

    c.setDash([])


# ============================================================
# PAGE BUILDERS
# ============================================================

def _auto_scale(box, max_w: float, max_h: float, view_w: float, view_h: float) -> float:
    """Calculate scale factor to fit a view into available space."""
    scale_x = max_w / view_w if view_w > 0 else 1.0
    scale_y = max_h / view_h if view_h > 0 else 1.0
    return min(scale_x, scale_y) * 0.85  # 85% fill


def build_page1(c, page_w: float, page_h: float, box, config, layout) -> None:
    """Page 1: Front + Top + Right views in 3rd angle projection."""
    draw_frame(c, page_w, page_h, 1, 4)

    usable_w = page_w - 2 * FRAME_MARGIN - 110 * mm  # leave room for title block area
    usable_h = page_h - 2 * FRAME_MARGIN - 50 * mm

    # 3rd angle projection layout:
    #   Top view above Front view, Right view to the right of Front
    # Front view: Width x Depth
    # Top view: Width x Length
    # Right view: Length x Depth

    front_w = box.internal_width
    front_h = box.internal_depth
    top_w = box.internal_width
    top_h = box.internal_length
    right_w = box.internal_length
    right_h = box.internal_depth

    # Calculate unified scale
    # Front+Right horizontal: front_w + right_w + gap
    # Front+Top vertical: front_h + top_h + gap
    gap = 40  # mm gap between views
    total_horiz = front_w + right_w + gap
    total_vert = front_h + top_h + gap

    s = _auto_scale(box, usable_w, usable_h, total_horiz, total_vert)

    # Front view origin (bottom-left area)
    front_ox = FRAME_MARGIN + 30 * mm
    front_oy = FRAME_MARGIN + 55 * mm

    draw_front_view(c, front_ox, front_oy, box, config, layout, s)

    # Top view above front (aligned horizontally)
    top_ox = front_ox
    top_oy = front_oy + front_h * s + gap * s * 0.5
    draw_top_view(c, top_ox, top_oy, box, config, layout, s)

    # Right view to the right of front (aligned vertically)
    right_ox = front_ox + front_w * s + gap * s * 0.5
    right_oy = front_oy
    draw_right_view(c, right_ox, right_oy, box, config, layout, s)

    draw_title_block(c, page_w, page_h, box, config, 1, 4)


def build_page2(c, page_w: float, page_h: float, box, config, layout) -> None:
    """Page 2: Left + Bottom + Back views."""
    draw_frame(c, page_w, page_h, 2, 4)

    usable_w = page_w - 2 * FRAME_MARGIN - 110 * mm
    usable_h = page_h - 2 * FRAME_MARGIN - 50 * mm

    left_w = box.internal_length
    left_h = box.internal_depth
    bottom_w = box.internal_width
    bottom_h = box.internal_length
    back_w = box.internal_width
    back_h = box.internal_depth

    gap = 40
    total_horiz = max(left_w, bottom_w) + back_w + gap
    total_vert = max(left_h + bottom_h + gap, back_h)

    s = _auto_scale(box, usable_w, usable_h, total_horiz, total_vert)

    base_x = FRAME_MARGIN + 30 * mm
    base_y = FRAME_MARGIN + 55 * mm

    # Left view (bottom-left)
    draw_left_view(c, base_x, base_y, box, config, layout, s)

    # Bottom view above left
    bottom_ox = base_x
    bottom_oy = base_y + left_h * s + gap * s * 0.5
    draw_bottom_view(c, bottom_ox, bottom_oy, box, config, layout, s)

    # Back view to the right
    back_ox = base_x + max(left_w, bottom_w) * s + gap * s * 0.5
    back_oy = base_y
    draw_back_view(c, back_ox, back_oy, box, config, layout, s)

    draw_title_block(c, page_w, page_h, box, config, 2, 4)


def build_page3(c, page_w: float, page_h: float, box, config, layout,
                switchgear_positions: list | None = None) -> None:
    """Page 3: Section A-A + Section B-B + Internal layout."""
    draw_frame(c, page_w, page_h, 3, 4)

    usable_w = page_w - 2 * FRAME_MARGIN - 20 * mm
    usable_h = page_h - 2 * FRAME_MARGIN - 50 * mm

    # Three views side by side
    aa_w = box.internal_width
    aa_h = box.internal_length
    bb_w = box.internal_width
    bb_h = box.internal_depth
    int_w = box.internal_width
    int_h = box.internal_length

    gap = 30
    total_horiz = aa_w + bb_w + int_w + 2 * gap
    total_vert = max(aa_h, bb_h, int_h)

    s = _auto_scale(box, usable_w, usable_h, total_horiz, total_vert)

    base_x = FRAME_MARGIN + 20 * mm
    base_y = FRAME_MARGIN + 55 * mm

    # Section A-A
    draw_section_aa(c, base_x, base_y, box, config, layout, s)

    # Section B-B
    bb_ox = base_x + aa_w * s + gap * s
    draw_section_bb(c, bb_ox, base_y, box, config, layout, s)

    # Internal layout
    int_ox = bb_ox + bb_w * s + gap * s
    draw_internal_view(c, int_ox, base_y, box, config, layout, s,
                       switchgear_positions=switchgear_positions)

    # BOM in top-left area
    bom_x = FRAME_MARGIN + 15 * mm
    bom_y = page_h - FRAME_MARGIN - 20 * mm
    draw_bom(c, bom_x, bom_y, box, config, layout,
             switchgear_positions=switchgear_positions)

    draw_title_block(c, page_w, page_h, box, config, 3, 4)


def build_page4(c, page_w: float, page_h: float, box, config, layout) -> None:
    """Page 4: 3D isometric view (CadQuery or fallback wireframe)."""
    draw_frame(c, page_w, page_h, 4, 4)

    center_x = page_w / 2
    center_y = page_h / 2 + 20 * mm

    # Try CadQuery SVG first
    success = try_cadquery_svg(c, center_x, center_y, 250 * mm, box, config)

    if not success:
        # Fallback wireframe isometric
        max_dim = max(box.internal_width, box.internal_length, box.internal_depth)
        iso_scale = min(180 * mm / max_dim, 0.5)
        draw_isometric_view(c, center_x - 40 * mm, center_y - 60 * mm, box, config, iso_scale)

        c.setFont("Helvetica", 8)
        c.setFillColor(colors.Color(0.5, 0.5, 0.5))
        c.drawCentredString(
            center_x,
            FRAME_MARGIN + 55 * mm,
            "Note: CadQuery not available. Showing simplified wireframe isometric view.",
        )

    draw_title_block(c, page_w, page_h, box, config, 4, 4)


# ============================================================
# PAGE 5: COVER VIEW (conditional)
# ============================================================

# Symbol drawing helpers for cover elements
COVER_SYMBOL_COLORS = {
    "green": colors.Color(0.2, 0.7, 0.2),
    "red": colors.Color(0.8, 0.2, 0.2),
    "yellow": colors.Color(0.9, 0.8, 0.1),
    "blue": colors.Color(0.2, 0.4, 0.8),
    "white": colors.Color(0.9, 0.9, 0.9),
    "black": colors.Color(0.2, 0.2, 0.2),
}


def _draw_circular_element(c, cx: float, cy: float, elem: dict, label: str, scale: float) -> None:
    """Draw a circular cover element (button, lamp, switch)"""
    bezel_r = elem.get("bezel_diameter", 30) / 2 * scale
    cutout_r = elem.get("cutout_diameter", 22) / 2 * scale
    color = COVER_SYMBOL_COLORS.get(elem.get("color", "black"), colors.Color(0.5, 0.5, 0.5))
    category = elem.get("category", "")

    # Bezel outline
    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_OUTLINE)
    c.circle(cx, cy, bezel_r)

    # Filled inner
    c.setFillColor(color)
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.circle(cx, cy, cutout_r, fill=1)

    # Category-specific symbol
    c.setStrokeColor(colors.white)
    c.setLineWidth(0.8)
    if category == "pushbutton":
        # Small inner circle
        c.circle(cx, cy, cutout_r * 0.5)
    elif category == "indicator_lamp":
        # Cross pattern
        r2 = cutout_r * 0.5
        c.line(cx - r2, cy, cx + r2, cy)
        c.line(cx, cy - r2, cx, cy + r2)
    elif category == "selector_switch":
        # Arrow
        r2 = cutout_r * 0.6
        c.line(cx, cy - r2, cx, cy + r2)
        c.line(cx, cy + r2, cx - r2 * 0.4, cy + r2 * 0.5)
        c.line(cx, cy + r2, cx + r2 * 0.4, cy + r2 * 0.5)
    elif category == "emergency_stop":
        # X mark
        r2 = cutout_r * 0.5
        c.setStrokeColor(colors.white)
        c.setLineWidth(1.5)
        c.line(cx - r2, cy - r2, cx + r2, cy + r2)
        c.line(cx - r2, cy + r2, cx + r2, cy - r2)

    # Label
    if label:
        c.setFont("Helvetica", max(6, 7 * scale))
        c.setFillColor(colors.black)
        c.drawCentredString(cx, cy - bezel_r - 8 * scale, label)


def _draw_rectangular_element(c, cx: float, cy: float, elem: dict, label: str, scale: float) -> None:
    """Draw a rectangular cover element (ammeter, voltmeter)"""
    bw = elem.get("bezel_width", 72) / 2 * scale
    bh = elem.get("bezel_height", 72) / 2 * scale

    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_OUTLINE)
    c.rect(cx - bw, cy - bh, bw * 2, bh * 2)

    # Inner display area
    cw = elem.get("cutout_width", 68) / 2 * scale
    ch = elem.get("cutout_height", 68) / 2 * scale
    c.setFillColor(colors.Color(0.95, 0.95, 0.95))
    c.rect(cx - cw, cy - ch, cw * 2, ch * 2, fill=1)

    # Category label
    c.setFont("Helvetica", max(5, 6 * scale))
    c.setFillColor(colors.black)
    cat = elem.get("category", "")
    display_text = "A" if cat == "ammeter" else "V" if cat == "voltmeter" else "?"
    c.drawCentredString(cx, cy - 3 * scale, display_text)

    if label:
        c.setFont("Helvetica", max(6, 7 * scale))
        c.drawCentredString(cx, cy - bh - 8 * scale, label)


def build_page5_cover(c, page_w: float, page_h: float, box, config, cover_elements, total_sheets: int) -> None:
    """Page 5: Panel cover front view with element positions."""
    sheet_num = 5
    draw_frame(c, page_w, page_h, sheet_num, total_sheets)

    # Drawing area
    da_left = FRAME_MARGIN + 20 * mm
    da_bottom = FRAME_MARGIN + 55 * mm
    da_width = page_w - 2 * FRAME_MARGIN - 40 * mm
    da_height = page_h - FRAME_MARGIN - 75 * mm - da_bottom + FRAME_MARGIN

    # Cover dimensions (mounting plate)
    cover_w = box.mounting_plate_x
    cover_h = box.mounting_plate_y

    # Scale to fit
    scale_x = da_width / (cover_w * mm)
    scale_y = da_height / (cover_h * mm)
    scale = min(scale_x, scale_y) * 0.85

    # Origin (centered in drawing area)
    ox = da_left + (da_width - cover_w * scale * mm) / 2
    oy = da_bottom + (da_height - cover_h * scale * mm) / 2

    # Title
    c.setFont(*FONT_LABEL)
    c.setFillColor(colors.black)
    c.drawString(da_left, page_h - FRAME_MARGIN - 25 * mm, "COVER VIEW - Panel Front")

    # Draw cover outline
    c.setStrokeColor(colors.black)
    c.setLineWidth(LW_OUTLINE)
    c.rect(ox, oy, cover_w * scale * mm, cover_h * scale * mm)

    # Dimension annotations
    c.setFont(*FONT_DIM)
    c.setStrokeColor(colors.Color(0.3, 0.3, 0.3))
    c.setLineWidth(LW_DIMENSION)
    # Width dimension
    dim_y = oy - 12 * mm
    c.line(ox, dim_y, ox + cover_w * scale * mm, dim_y)
    c.drawCentredString(ox + cover_w * scale * mm / 2, dim_y - 4 * mm, f"{cover_w:.0f}")
    # Height dimension
    dim_x = ox - 12 * mm
    c.line(dim_x, oy, dim_x, oy + cover_h * scale * mm)
    c.saveState()
    c.translate(dim_x - 4 * mm, oy + cover_h * scale * mm / 2)
    c.rotate(90)
    c.drawCentredString(0, 0, f"{cover_h:.0f}")
    c.restoreState()

    # Draw cover elements
    from app.models import get_cover_element_by_id

    for ce_data in cover_elements:
        elem = get_cover_element_by_id(ce_data.get("element_id", ce_data.get("id", "")))
        if not elem:
            continue

        ex = ce_data.get("x", 0)
        ey = ce_data.get("y", 0)
        label = ce_data.get("label", "")

        # Convert to PDF coordinates (y is inverted: panel y=0 is top, PDF y=0 is bottom)
        pdf_x = ox + ex * scale * mm
        pdf_y = oy + (cover_h - ey) * scale * mm

        if "cutout_diameter" in elem:
            _draw_circular_element(c, pdf_x, pdf_y, elem, label, scale)
        else:
            _draw_rectangular_element(c, pdf_x, pdf_y, elem, label, scale)

    # Element legend table
    if cover_elements:
        legend_x = ox + cover_w * scale * mm + 15 * mm
        legend_y = oy + cover_h * scale * mm
        c.setFont("Helvetica-Bold", 8)
        c.drawString(legend_x, legend_y, "ELEMENT LIST")
        c.setFont("Helvetica", 7)
        for i, ce_data in enumerate(cover_elements):
            elem = get_cover_element_by_id(ce_data.get("element_id", ce_data.get("id", "")))
            if not elem:
                continue
            label = ce_data.get("label", f"E{i+1}")
            row_y = legend_y - (i + 1) * 12
            c.drawString(legend_x, row_y, f"{label}: {elem['name']}")
            c.drawString(legend_x, row_y - 8, f"  X={ce_data.get('x', 0):.0f} Y={ce_data.get('y', 0):.0f}")

    draw_title_block(c, page_w, page_h, box, config, sheet_num, total_sheets)


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def generate_pdf(config, layout, cover_elements=None, switchgear_positions=None) -> bytes:
    """
    Generate multi-page A3 landscape technical drawing PDF.

    Args:
        config: ConfigurationInput with box_id, terminals, holes, etc.
        layout: LayoutResult with rails, holes_top/bottom/left/right.
        cover_elements: Optional list of cover element placements.
        switchgear_positions: Optional list of SwitchgearPosition objects.

    Returns:
        PDF file content as bytes.
    """
    from app.models import get_box_model_by_id

    box = get_box_model_by_id(config.box_id)
    if not box:
        raise ValueError(f"Box model not found: {config.box_id}")

    has_cover = cover_elements and len(cover_elements) > 0
    total_sheets = 5 if has_cover else 4

    buffer = io.BytesIO()
    page_w, page_h = PAGE_SIZE
    c = pdf_canvas.Canvas(buffer, pagesize=PAGE_SIZE)

    # Page 1: Front + Top + Right
    build_page1(c, page_w, page_h, box, config, layout)
    c.showPage()

    # Page 2: Left + Bottom + Back
    build_page2(c, page_w, page_h, box, config, layout)
    c.showPage()

    # Page 3: Sections + Internal + BOM
    build_page3(c, page_w, page_h, box, config, layout,
                switchgear_positions=switchgear_positions)
    c.showPage()

    # Page 4: 3D Isometric
    build_page4(c, page_w, page_h, box, config, layout)

    # Page 5: Cover View (only if cover elements exist)
    if has_cover:
        c.showPage()
        build_page5_cover(c, page_w, page_h, box, config, cover_elements, total_sheets)

    c.save()
    buffer.seek(0)
    return buffer.read()
