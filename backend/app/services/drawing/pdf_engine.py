"""
Professional CAD-Quality Technical Drawing Engine
Uses ezdxf + matplotlib for industry-standard technical drawings

This approach creates proper CAD-quality drawings:
1. Uses ezdxf to create proper DXF drawings (industry standard)
2. Renders to PDF using matplotlib with high quality
3. Includes proper technical drawing standards (ISO/DIN)
"""

import io
import math
from datetime import datetime
from typing import List, Tuple

import ezdxf
from ezdxf import units
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdf_canvas


# ============================================================
# DXF-BASED 3D MODELS
# ============================================================

import subprocess
import os

def create_enclosure_dxf(box, config) -> ezdxf.drawing.Drawing:
    """
    Generate accurate DXF using CadQuery external script
    """
    # 1. Run CadQuery script to generate DXF
    script_path = os.path.join(os.path.dirname(__file__), '../../generate_cad.py')
    
    # Pass config as JSON string
    import json
    config_data = json.dumps({
        "width": box.internal_width,
        "length": box.internal_length,
        "depth": box.internal_depth,
        "holes_bottom": config.holes_bottom,
        "holes_top": config.holes_top
    })
    
    # Use the conda environment python
    conda_python = os.path.expanduser("~/miniconda3/envs/cadquery/bin/python")
    
    try:
        # Run in the same directory as the script so relative output paths work
        subprocess.run(
            [conda_python, script_path, config_data], 
            check=True, 
            capture_output=True,
            cwd=os.path.dirname(script_path)
        )
        
        # 2. Read the generated DXF
        dxf_path = os.path.join(os.path.dirname(script_path), 'cad_output.dxf')
        if os.path.exists(dxf_path):
            doc = ezdxf.readfile(dxf_path)
            return doc
            
    except Exception as e:
        print(f"CadQuery generation failed: {e}. Falling back to internal engine.")
    
    # Fallback to internal DXF generation if external fails
    return create_manual_dxf(box, config)

def create_manual_dxf(box, config):
    """Fallback manual DXF generation (previous implementation)"""
    doc = ezdxf.new(dxfversion='R2018')
    doc.units = units.MM
    msp = doc.modelspace()
    
    # Box dimensions
    W = box.internal_width
    H = box.internal_depth  
    D = box.internal_length
    
    # Create layers for different elements
    doc.layers.add('OUTLINE', color=0)
    doc.layers.add('HIDDEN', color=8, linetype='DASHED')
    doc.layers.add('GLAND', color=250)
    
    # ===== FRONT VIEW (Main 3D Isometric) =====
    iso_offset_x = 50
    iso_offset_y = 150
    
    # Isometric projection factors
    angle = 30
    cos30 = math.cos(math.radians(angle))
    sin30 = math.sin(math.radians(angle))
    scale = 0.5
    
    def iso_point(x, y, z):
        """Convert 3D to 2D isometric"""
        px = iso_offset_x + (x - z) * cos30 * scale
        py = iso_offset_y + y * scale + (x + z) * sin30 * scale
        return (px, py)
    
    # Front face
    p1 = iso_point(0, 0, 0)
    p2 = iso_point(W, 0, 0)
    p3 = iso_point(W, H, 0)
    p4 = iso_point(0, H, 0)
    
    # Draw front face
    msp.add_line(p1, p2, dxfattribs={'layer': 'OUTLINE'})
    msp.add_line(p2, p3, dxfattribs={'layer': 'OUTLINE'})
    msp.add_line(p3, p4, dxfattribs={'layer': 'OUTLINE'})
    msp.add_line(p4, p1, dxfattribs={'layer': 'OUTLINE'})
    
    # Top face
    p5 = iso_point(0, H, D)
    p6 = iso_point(W, H, D)
    
    msp.add_line(p4, p5, dxfattribs={'layer': 'OUTLINE'})
    msp.add_line(p3, p6, dxfattribs={'layer': 'OUTLINE'})
    msp.add_line(p5, p6, dxfattribs={'layer': 'OUTLINE'})
    
    # Right face
    p7 = iso_point(W, 0, D)
    
    msp.add_line(p2, p7, dxfattribs={'layer': 'OUTLINE'})
    msp.add_line(p7, p6, dxfattribs={'layer': 'OUTLINE'})
    
    return doc


def draw_cable_gland_iso(msp, center: Tuple[float, float], scale: float):
    """Draw an isometric cable gland"""
    cx, cy = center
    r = 4 * scale
    
    # Hexagonal nut (approximate)
    hex_points = []
    for i in range(6):
        angle = math.radians(60 * i + 30)
        hx = cx + r * math.cos(angle)
        hy = cy + r * math.sin(angle)
        hex_points.append((hx, hy))
    
    msp.add_lwpolyline(hex_points, close=True, dxfattribs={'layer': 'GLAND'})
    
    # Inner circle
    msp.add_circle(center, r * 0.5, dxfattribs={'layer': 'GLAND'})
    
    # Cable (line going down)
    msp.add_line((cx, cy - r * 0.5), (cx, cy - r * 2), dxfattribs={'layer': 'GLAND'})


# ============================================================
# PDF GENERATION WITH MATPLOTLIB BACKEND
# ============================================================

def render_dxf_to_pdf(doc: ezdxf.drawing.Drawing) -> bytes:
    """Render DXF to PDF using matplotlib"""
    fig = plt.figure(figsize=(11.69, 8.27), dpi=150)  # A4 landscape
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])
    ax.set_aspect('equal')
    
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(doc.modelspace())
    
    ax.autoscale()
    ax.set_axis_off()
    
    # Add title block and annotations via matplotlib
    add_title_block_mpl(fig, ax)
    
    buffer = io.BytesIO()
    fig.savefig(buffer, format='pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    
    buffer.seek(0)
    return buffer.read()


def add_title_block_mpl(fig, ax):
    """Add title block using matplotlib annotations"""
    # Add text for title block
    fig.text(0.85, 0.06, "DROV Engineering", fontsize=10, fontweight='bold', ha='center')
    fig.text(0.85, 0.04, datetime.now().strftime("%d.%m.%Y"), fontsize=8, ha='center')


# ============================================================
# HYBRID APPROACH: DXF + ReportLab
# ============================================================

def create_professional_pdf(config, layout) -> bytes:
    """
    Create professional technical drawing PDF
    Uses DXF for geometry + ReportLab for layout/annotations
    """
    from app.models import get_box_model_by_id
    box = get_box_model_by_id(config.box_id)
    if not box:
        raise ValueError(f"Box not found: {config.box_id}")
    
    # Create main PDF with ReportLab
    buffer = io.BytesIO()
    page_w, page_h = landscape(A4)
    c = pdf_canvas.Canvas(buffer, pagesize=landscape(A4))
    
    # Draw frame
    draw_professional_frame(c, page_w, page_h)
    
    # Draw parts list
    draw_parts_list_professional(c, 22*mm, page_h - 25*mm, config, box)
    
    # Draw main isometric view
    draw_isometric_view(c, 100*mm, page_h * 0.45, box, config)
    
    # Draw section B-B
    draw_section_bb_professional(c, 22*mm, 30*mm, box, config)
    
    # Draw section A-A  
    draw_section_aa_professional(c, page_w - 75*mm, page_h - 75*mm, box, config)
    
    # Draw internal view
    draw_internal_view_professional(c, 120*mm, 30*mm, box, config)
    
    # Draw title block
    draw_title_block_professional(c, page_w - 95*mm, 10*mm, box, config)
    
    # Add annotations
    draw_annotations_professional(c, box, config, page_w, page_h)
    
    # Technical notes
    c.setFont('Helvetica', 6)
    c.drawString(22*mm, 18*mm, "* All dimensions in mm")
    c.drawString(22*mm, 13*mm, "* Tolerance: ±0.5mm")
    
    c.save()
    buffer.seek(0)
    return buffer.read()


def draw_professional_frame(c, page_w, page_h):
    """Draw professional drawing frame with border zones"""
    margin = 10 * mm
    
    # Outer border
    c.setStrokeColor(colors.black)
    c.setLineWidth(2)
    c.rect(margin, margin, page_w - 2*margin, page_h - 2*margin)
    
    # Inner border
    c.setLineWidth(0.5)
    c.rect(margin + 2, margin + 2, page_w - 2*margin - 4, page_h - 2*margin - 4)
    
    # Column markers (1-8)
    c.setFont('Helvetica', 7)
    inner_w = page_w - 2 * margin
    col_w = inner_w / 8
    for i in range(8):
        x = margin + col_w * (i + 0.5)
        c.drawCentredString(x, page_h - margin + 3, str(i + 1))
        c.drawCentredString(x, margin - 7, str(i + 1))
        # Tick marks
        if i > 0:
            c.setLineWidth(0.3)
            c.line(margin + col_w * i, page_h - margin, margin + col_w * i, page_h - margin - 3*mm)
            c.line(margin + col_w * i, margin, margin + col_w * i, margin + 3*mm)
    
    # Row markers (A-F)
    inner_h = page_h - 2 * margin
    row_h = inner_h / 6
    for i, letter in enumerate(['A', 'B', 'C', 'D', 'E', 'F']):
        y = page_h - margin - row_h * (i + 0.5)
        c.drawCentredString(margin - 4, y - 2, letter)
        c.drawCentredString(page_w - margin + 4, y - 2, letter)


def draw_parts_list_professional(c, x, y, config, box):
    """Draw professional parts list"""
    row_h = 4.5 * mm
    col_widths = [8*mm, 8*mm, 50*mm]
    total_w = sum(col_widths)
    
    total_holes = config.holes_top + config.holes_bottom + config.holes_left + config.holes_right
    
    parts = [
        (1, 1, f"CMP_{box.id.upper()}W1RA5"),
        (2, 1, f"07-0168-{box.id.upper()}01/2"),
        (3, box.rail_count, "NS_35_15_PERF_200MM-select"),
        (4, config.terminals, "Box_3044029_22_00_UT-2.5_3D"),
        (5, 2, "pnl_302203_CLIPFIX-35-5"),
        (6, total_holes, "pnl_3047028_D-UT-2.5-10_3D"),
        (7, 1, "Drain_Valve_M20x1.5mm"),
        (8, total_holes, "CMP_20E1FW1RA5"),
    ]
    parts = [(i, q, n) for i, q, n in parts if q > 0]
    
    # Header
    c.setFillColor(colors.Color(0.9, 0.9, 0.9))
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.75)
    c.rect(x, y, total_w, row_h, fill=1, stroke=1)
    
    c.setFont('Helvetica-Bold', 6)
    c.setFillColor(colors.black)
    c.drawCentredString(x + total_w/2, y + 1.5, "Parts List")
    
    # Column headers
    header_y = y - row_h
    c.setFillColor(colors.Color(0.95, 0.95, 0.95))
    c.rect(x, header_y, total_w, row_h, fill=1, stroke=1)
    
    c.setFont('Helvetica', 5)
    c.setFillColor(colors.black)
    c.drawString(x + 1.5, header_y + 1.5, "Item")
    c.drawString(x + col_widths[0] + 1.5, header_y + 1.5, "Qty")
    c.drawString(x + col_widths[0] + col_widths[1] + 1.5, header_y + 1.5, "Part Name")
    
    # Vertical lines
    c.line(x + col_widths[0], y, x + col_widths[0], header_y - len(parts) * row_h)
    c.line(x + col_widths[0] + col_widths[1], y, x + col_widths[0] + col_widths[1], header_y - len(parts) * row_h)
    
    # Data
    c.setFont('Helvetica', 5)
    for idx, (item, qty, name) in enumerate(parts):
        row_y = header_y - (idx + 1) * row_h
        c.rect(x, row_y, total_w, row_h, fill=0, stroke=1)
        c.drawCentredString(x + col_widths[0]/2, row_y + 1.5, str(item))
        c.drawCentredString(x + col_widths[0] + col_widths[1]/2, row_y + 1.5, str(qty))
        c.drawString(x + col_widths[0] + col_widths[1] + 1.5, row_y + 1.5, name[:28])


def draw_isometric_view(c, x, y, box, config):
    """
    Draw professional isometric view using generated CAD SVG.
    Parses SVG paths and renders them as vector graphics in PDF.
    """
    try:
        # 1. Generate/Get SVG
        # Reuse existing create_enclosure_dxf logic but check for SVG
        import os
        import subprocess
        import json
        
        # script_path = os.path.join(os.path.dirname(__file__), '../../generate_cad.py')
        script_path = "/Users/wazder/Documents/GitHub/Drov/backend/generate_cad.py"
        config_data = json.dumps({
            "width": box.internal_width,
            "length": box.internal_length,
            "depth": box.internal_depth,
            "holes_bottom": config.holes_bottom,
            "holes_top": config.holes_top
        })
        conda_python = os.path.expanduser("~/miniconda3/envs/cadquery/bin/python")
        
        # Prepare environment: Remove PYTHONPATH to prevent conflict with venv
        my_env = os.environ.copy()
        if 'PYTHONPATH' in my_env:
            del my_env['PYTHONPATH']
            
        # Run script
        subprocess.run(
            [conda_python, script_path, config_data], 
            check=True, 
            capture_output=True,
            cwd=os.path.dirname(script_path),
            env=my_env
        )
        
        svg_path = os.path.join(os.path.dirname(script_path), 'cad_output.svg')
        
        if os.path.exists(svg_path):
            draw_cad_svg(c, svg_path, x, y, width=150*mm)
        else:
            c.drawString(x, y, "CAD SVG Not Found")
            
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.decode()
        print(f"Subprocess Error: {err_msg}")
        c.saveState()
        c.setFillColor(colors.red)
        c.drawString(x, y, "CAD Gen Error:")
        lines = err_msg.split('\n')
        for idx, line in enumerate(lines[:5]):
            c.drawString(x, y - 12 - idx*10, line[:60])
        c.restoreState()
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error rendering isometric view: {e}")
        c.saveState()
        c.setFillColor(colors.red)
        c.drawString(x, y, f"Main Err: {str(e)[:50]}")
        c.restoreState()

def draw_cad_svg(c, svg_file, cx, cy, width):
    """
    Robust Regex-based SVG Parser for CadQuery output.
    Handles global transforms and paths without XML dependency issues.
    """
    import re
    
    try:
        with open(svg_file, 'r') as f:
            content = f.read()
            
        # 1. Extract Global Transform (Group level)
        # CadQuery SVG usually wraps in <g transform="...">
        # Format: transform="scale(0.9, -0.9) translate(286, -292)"
        
        sx, sy = 1.0, -1.0 # Default SVG flip
        tx, ty = 0.0, 0.0
        
        # Simple regex for scale and translate
        # Note: Order matters in SVG matrix, but CQ output is predictable
        scale_match = re.search(r'scale\(([^,)]+)(?:,\s*([^)]+))?\)', content)
        trans_match = re.search(r'translate\(([^,)]+)(?:,\s*([^)]+))?\)', content)
        
        if scale_match:
            sx = float(scale_match.group(1))
            if scale_match.group(2):
                sy = float(scale_match.group(2))
            else:
                sy = sx # Uniform scale
                
        if trans_match:
            tx = float(trans_match.group(1))
            if trans_match.group(2):
                ty = float(trans_match.group(2))
                
        # 2. Extract ViewBox for scaling to target
        vb_match = re.search(r'viewBox="([^"]+)"', content)
        vw, vh = 1000, 750 # Defaults
        if vb_match:
            parts = vb_match.group(1).split()
            if len(parts) == 4:
                vw, vh = float(parts[2]), float(parts[3])
        
        # Calculate final PDF scale
        pdf_scale = width / vw 
        
        # Center adjustment
        offset_x = cx - (vw * pdf_scale) / 2
        offset_y = cy + (vh * pdf_scale) / 2 # PDF Y is up
        
        # 3. Process Paths
        # Find all <path ... d="..." ... /> tags
        # We also need to check for dashed lines (hidden)
        
        path_pattern = re.compile(r'<path([^>]+)>')
        d_pattern = re.compile(r'd="([^"]+)"')
        style_pattern = re.compile(r'style="([^"]+)"')
        stroke_pattern = re.compile(r'stroke="([^"]+)"')
        
        c.setLineWidth(0.3)
        
        for match in path_pattern.finditer(content):
            attrs = match.group(1)
            
            d_match = d_pattern.search(attrs)
            if not d_match: continue
            d = d_match.group(1)
            
            # Check style
            is_hidden = False
            if 'stroke-dasharray' in attrs:
                is_hidden = True
            
            # Additional check for color if dasharray missing
            if 'rgb(100,100,100)' in attrs or 'rgb(100, 100, 100)' in attrs:
                is_hidden = True
                
            if is_hidden:
                c.setStrokeColor(colors.Color(0.6, 0.6, 0.6))
                c.setDash([2, 1])
            else:
                c.setStrokeColor(colors.black)
                c.setDash([])
            
            # Parse Path Data
            p = c.beginPath()
            
            # Tokenize: M, L, C, Z and numbers
            tokens = re.findall(r'([MmLlCcZz])|([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)', d)
            
            flat_tokens = []
            for t in tokens:
                if t[0]: 
                    flat_tokens.append(t[0])
                elif t[1] and t[1].strip():
                    try:
                        flat_tokens.append(float(t[1]))
                    except ValueError:
                        pass
            
            i = 0
            current_x, current_y = 0, 0
            
            # State machine for implicit commands
            last_cmd = 'M'
            
            while i < len(flat_tokens):
                cmd = flat_tokens[i]
                if isinstance(cmd, str):
                    last_cmd = cmd
                    i += 1
                
                # Apply Transform logic:
                # Raw Point (px, py) -> Scaled/Trans (tx, ty) -> PDF (final_x, final_y)
                # SVG Transform: x' = x*sx + tx
                # PDF Transform: X = x' * pdf_scale + offset_x
                # Final X = (x*sx + tx) * pdf_scale + offset_x
                
                def transform_pt(px, py):
                    # Apply group transform
                    gx = px * sx + tx
                    gy = py * sy + ty
                    
                    # Apply PDF placement
                    # Note: SVG Y is down, but 'sy' usually handles flip (-0.9).
                    # If sy is negative, Y is flipped.
                    # PDF Y is up.
                    
                    fx = gx * pdf_scale + offset_x
                    # Since SVG coords with negative scale are already inverted relative to origin,
                    # we just map them to PDF space.
                    # But if sy is negative (standard CQ export), higher Y means 'lower' in drawing (more negative).
                    # PDF Y=0 is bottom.
                    # Let's trust the math: offset_y + gy * pdf_scale
                    
                    fy = offset_y + gy * pdf_scale
                    return fx, fy
                
                if last_cmd == 'M': # Move
                    if i + 1 >= len(flat_tokens): break
                    x, y = flat_tokens[i], flat_tokens[i+1]
                    fx, fy = transform_pt(x, y)
                    p.moveTo(fx, fy)
                    current_x, current_y = fx, fy
                    i += 2
                    # Implicit L after M
                    last_cmd = 'L' 
                    
                elif last_cmd == 'L': # Line
                    if i + 1 >= len(flat_tokens): break
                    x, y = flat_tokens[i], flat_tokens[i+1]
                    fx, fy = transform_pt(x, y)
                    p.lineTo(fx, fy)
                    current_x, current_y = fx, fy
                    i += 2
                    
                elif last_cmd == 'C': # Cubic
                    if i + 5 >= len(flat_tokens): break
                    x1, y1 = flat_tokens[i], flat_tokens[i+1]
                    x2, y2 = flat_tokens[i+2], flat_tokens[i+3]
                    x3, y3 = flat_tokens[i+4], flat_tokens[i+5]
                    
                    fx1, fy1 = transform_pt(x1, y1)
                    fx2, fy2 = transform_pt(x2, y2)
                    fx3, fy3 = transform_pt(x3, y3)
                    
                    p.curveTo(fx1, fy1, fx2, fy2, fx3, fy3)
                    current_x, current_y = fx3, fy3
                    i += 6
                    
                elif last_cmd == 'Z':
                    p.close()
                    # Z consumes no args, resets loop
                    # Often followed by M
                    pass
                else:
                    i += 1
            
            c.drawPath(p, stroke=1, fill=0)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        c.saveState()
        c.setFillColor(colors.red)
        # Hata mesajını çok satırlı yazdır
        lines = str(e).split('\n')
        for idx, line in enumerate(lines[:3]): # İlk 3 satır
            c.drawString(cx - 100, cy - idx*10, f"SVG Err: {line[:50]}")
        c.restoreState()
            
    except Exception as e:
        print(f"SVG Parse Error: {e}")
        c.drawString(cx, cy, "SVG Parse Error")


def draw_cable_gland(c, cx, cy, scale=1.0):
    """Draw a detailed cable gland"""
    # Cable
    c.setFillColor(colors.Color(0.15, 0.15, 0.15))
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.3)
    
    cable_w = 3 * mm * scale
    cable_h = 10 * mm * scale
    c.rect(cx - cable_w/2, cy - cable_h, cable_w, cable_h, fill=1, stroke=1)
    
    # Gland body
    body_w = 7 * mm * scale
    body_h = 5 * mm * scale
    c.setFillColor(colors.Color(0.35, 0.35, 0.35))
    c.rect(cx - body_w/2, cy, body_w, body_h, fill=1, stroke=1)
    
    # Hex nut
    nut_w = 9 * mm * scale
    nut_h = 4 * mm * scale
    c.setFillColor(colors.Color(0.25, 0.25, 0.25))
    c.rect(cx - nut_w/2, cy + body_h, nut_w, nut_h, fill=1, stroke=1)
    
    # Hex lines
    c.setStrokeColor(colors.Color(0.45, 0.45, 0.45))
    c.setLineWidth(0.2)
    for dx in [-nut_w/3, 0, nut_w/3]:
        c.line(cx + dx, cy + body_h, cx + dx, cy + body_h + nut_h)


def draw_section_bb_professional(c, x, y, box, config):
    """Draw professional B-B cross-section"""
    scale = 0.4
    W = box.internal_width * scale
    H = box.internal_length * scale
    
    # Outer frame
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.rect(x, y, W, H)
    
    # Wall
    wall = 3 * scale
    c.setFillColor(colors.Color(0.95, 0.95, 0.95))
    c.rect(x + wall, y + wall, W - 2*wall, H - 2*wall, fill=1, stroke=1)
    
    # Hatch pattern for cut areas
    c.setStrokeColor(colors.Color(0.7, 0.7, 0.7))
    c.setLineWidth(0.15)
    hatch_gap = 2 * mm
    for i in range(int((W + H) / hatch_gap) + 1):
        start_x = x + i * hatch_gap
        if start_x < x + wall:
            c.line(start_x, y, start_x, y + min(i * hatch_gap, wall))
        elif start_x > x + W - wall:
            offset = start_x - (x + W - wall)
            c.line(start_x, y, x + W, y + offset)
    
    # DIN Rails and terminals
    rail_count = box.rail_count
    inner_h = H - 2 * wall
    rail_spacing = inner_h / (rail_count + 1)
    
    for i in range(rail_count):
        rail_y = y + wall + rail_spacing * (i + 1)
        rail_x = x + wall + 3
        rail_w = W - 2*wall - 6
        
        # Rail
        c.setFillColor(colors.Color(0.85, 0.87, 0.9))
        c.setStrokeColor(colors.Color(0.6, 0.6, 0.6))
        c.setLineWidth(0.5)
        c.rect(rail_x, rail_y - 2, rail_w, 4, fill=1, stroke=1)
        
        # Terminals
        terms = min(config.terminals // rail_count, 50)
        term_w = 2.2
        term_h = 12
        
        c.setFillColor(colors.Color(0.7, 0.88, 0.55))
        c.setStrokeColor(colors.Color(0.5, 0.7, 0.4))
        c.setLineWidth(0.3)
        
        for t in range(terms):
            tx = rail_x + 3 + t * (term_w + 0.3)
            if tx + term_w > rail_x + rail_w - 3:
                break
            c.rect(tx, rail_y - term_h/2, term_w, term_h, fill=1, stroke=1)
            
            # Screw details every 5th terminal
            if t % 5 == 0:
                c.setFillColor(colors.Color(0.4, 0.4, 0.4))
                c.circle(tx + term_w/2, rail_y - term_h/2 + 1.5, 0.6, fill=1, stroke=0)
                c.circle(tx + term_w/2, rail_y + term_h/2 - 1.5, 0.6, fill=1, stroke=0)
                c.setFillColor(colors.Color(0.7, 0.88, 0.55))
    
    # Label
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(colors.black)
    c.drawString(x, y + H + 4, "B-B (1:4)")
    
    # Section markers
    c.setFont('Helvetica-Bold', 12)
    c.drawCentredString(x - 10, y + H/2 - 3, "B")
    c.drawCentredString(x + W + 10, y + H/2 - 3, "B")


def draw_section_aa_professional(c, x, y, box, config):
    """Draw professional A-A side section"""
    scale = 0.25
    W = box.internal_length * scale
    H = box.internal_depth * scale
    
    # Outer frame
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(x, y, W, H)
    
    # Wall
    wall = 3 * scale
    c.setFillColor(colors.Color(0.96, 0.96, 0.96))
    c.rect(x + wall, y + wall, W - 2*wall, H - 2*wall, fill=1, stroke=1)
    
    # Rails from side
    rail_count = box.rail_count
    inner_h = H - 2*wall
    rail_spacing = inner_h / (rail_count + 1)
    
    c.setFillColor(colors.Color(0.85, 0.87, 0.9))
    for i in range(rail_count):
        ry = y + wall + rail_spacing * (i + 1)
        c.rect(x + wall + 3, ry - 1.5, W - 2*wall - 6, 3, fill=1, stroke=1)
    
    # Label
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(colors.black)
    c.drawString(x + W + 3, y + H + 3, "A-A (1:4)")
    
    # Section marker
    c.setFont('Helvetica-Bold', 12)
    c.drawCentredString(x + W/2, y + H + 12, "A")


def draw_internal_view_professional(c, x, y, box, config):
    """Draw internal top view with terminal layout"""
    scale = 0.3
    W = box.internal_width * scale
    H = box.internal_length * scale
    
    # Frame
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(x, y, W, H)
    
    # Internal area
    wall = 3 * scale
    c.setFillColor(colors.Color(0.97, 0.97, 0.97))
    c.rect(x + wall, y + wall, W - 2*wall, H - 2*wall, fill=1, stroke=1)
    
    # DIN rails (from top - vertical lines)
    rail_count = box.rail_count
    inner_w = W - 2*wall
    rail_spacing = inner_w / (rail_count + 1)
    
    c.setStrokeColor(colors.Color(0.6, 0.6, 0.6))
    c.setLineWidth(0.75)
    
    for i in range(rail_count):
        rx = x + wall + rail_spacing * (i + 1)
        c.line(rx, y + wall + 3, rx, y + H - wall - 3)
        
        # Terminal positions
        terms = min(config.terminals // rail_count, 50)
        term_h = 1.5
        term_spacing = (H - 2*wall - 6) / max(terms, 1)
        
        c.setFillColor(colors.Color(0.7, 0.88, 0.55))
        c.setStrokeColor(colors.Color(0.5, 0.7, 0.4))
        c.setLineWidth(0.2)
        
        for t in range(min(terms, 40)):
            ty = y + wall + 3 + t * term_spacing
            if ty + term_h > y + H - wall - 3:
                break
            c.rect(rx - 4, ty, 8, term_h, fill=1, stroke=1)


def draw_title_block_professional(c, x, y, box, config):
    """Draw professional title block"""
    width = 90 * mm
    height = 35 * mm
    
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(x, y, width, height)
    
    # Logo section
    logo_w = 26 * mm
    c.setFillColor(colors.Color(0.12, 0.22, 0.38))
    c.rect(x, y, logo_w, height, fill=1, stroke=1)
    
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(x + logo_w/2, y + height - 12*mm, "DROV")
    c.setFont('Helvetica', 7)
    c.drawCentredString(x + logo_w/2, y + height - 17*mm, "Engineering")
    
    # Info section
    info_x = x + logo_w + 2*mm
    c.setFillColor(colors.black)
    
    # Horizontal dividers
    c.setLineWidth(0.5)
    row1 = y + height - 8*mm
    row2 = y + height - 20*mm
    row3 = y + 10*mm
    
    c.line(x + logo_w, row1, x + width, row1)
    c.line(x + logo_w, row2, x + width, row2)
    c.line(x + logo_w, row3, x + width, row3)
    
    # Text
    c.setFont('Helvetica', 6)
    c.drawString(info_x, y + height - 5, "Drawn by:")
    c.drawString(info_x + 35*mm, y + height - 5, datetime.now().strftime("%d.%m.%Y"))
    
    c.setFont('Helvetica', 8)
    c.drawString(info_x, row1 + 2, "DROV System")
    
    c.setFont('Helvetica', 6)
    c.drawString(info_x, row1 - 5, "Title:")
    c.setFont('Helvetica-Bold', 11)
    c.drawString(info_x, row2 + 3, f"{box.name} Config")
    
    c.setFont('Helvetica', 6)
    c.drawString(info_x, row3 - 5, "Drawing No.")
    c.setFont('Helvetica-Bold', 9)
    c.drawString(info_x, y + 2, f"DRV-{box.id.upper()}-001")
    
    c.setFont('Helvetica', 6)
    c.drawString(info_x + 38*mm, row3 - 5, "Scale: 1:2")
    c.drawString(info_x + 53*mm, row3 - 5, "Sheet: 1/1")


def draw_annotations_professional(c, box, config, page_w, page_h):
    """Add professional annotation balloons"""
    balloon_r = 3.5 * mm
    
    annotations = [
        (1, 170*mm, page_h - 40*mm, 140*mm, page_h - 80*mm),  # Enclosure
        (2, 185*mm, page_h - 55*mm, 155*mm, page_h - 90*mm),  # Cover
    ]
    
    if config.holes_bottom > 0 or config.holes_top > 0:
        annotations.append((6, 85*mm, page_h - 95*mm, 105*mm, page_h - 85*mm))  # Glands
    
    for num, bx, by, tx, ty in annotations:
        # Leader line
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.4)
        c.line(bx, by - balloon_r, tx, ty)
        
        # Arrow
        angle = math.atan2(ty - (by - balloon_r), tx - bx)
        arrow_len = 2.5 * mm
        angle1 = angle - math.radians(25)
        angle2 = angle + math.radians(25)
        
        ax1 = tx - arrow_len * math.cos(angle1)
        ay1 = ty - arrow_len * math.sin(angle1)
        ax2 = tx - arrow_len * math.cos(angle2)
        ay2 = ty - arrow_len * math.sin(angle2)
        
        c.setFillColor(colors.black)
        arrow = c.beginPath()
        arrow.moveTo(tx, ty)
        arrow.lineTo(ax1, ay1)
        arrow.lineTo(ax2, ay2)
        arrow.close()
        c.drawPath(arrow, fill=1)
        
        # Balloon
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.6)
        c.circle(bx, by, balloon_r, fill=1, stroke=1)
        
        # Number
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 9)
        tw = c.stringWidth(str(num), 'Helvetica', 9)
        c.drawString(bx - tw/2, by - 3, str(num))


# ============================================================
# MAIN EXPORT
# ============================================================

def generate_pdf(config, layout) -> bytes:
    """Main PDF generation entry point"""
    return create_professional_pdf(config, layout)
