"""
Label PDF Engine - Generates panel identification labels
"""
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, mm
from reportlab.pdfgen import canvas as pdf_canvas


def generate_label_pdf(label_data, box) -> bytes:
    """
    Generate a panel label PDF.

    Args:
        label_data: LabelInput schema with label fields.
        box: BoxModel for the panel.

    Returns:
        PDF bytes.
    """
    label_w = 100 * mm
    label_h = 60 * mm

    buffer = io.BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    page_w, page_h = A4

    # Center label on A4
    ox = (page_w - label_w) / 2
    oy = (page_h - label_h) / 2

    # Outer border (double line effect)
    c.setStrokeColor(colors.black)
    c.setLineWidth(2)
    c.rect(ox, oy, label_w, label_h)
    c.setLineWidth(0.5)
    c.rect(ox + 2, oy + 2, label_w - 4, label_h - 4)

    # DROV logo area
    logo_h = 12 * mm
    c.setFillColor(colors.Color(0.08, 0.18, 0.35))
    c.rect(ox + 2, oy + label_h - logo_h - 2, label_w - 4, logo_h, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(ox + label_w / 2, oy + label_h - logo_h + 2, "DROV Engineering")

    # Fields
    fields = [
        ("Panel", label_data.panel_name or box.name),
        ("Drawing No", label_data.drawing_number or f"DRV-{box.id.upper()}-001"),
        ("Customer", label_data.customer_name or "-"),
        ("Project", label_data.project_name or "-"),
        ("Order No", label_data.order_number or "-"),
        ("Voltage", label_data.voltage or "230V AC"),
        ("IP Rating", label_data.ip_rating or "IP66"),
        ("Date", label_data.date or datetime.now().strftime("%d.%m.%Y")),
    ]

    row_h = 5.5 * mm
    start_y = oy + label_h - logo_h - 6 * mm

    c.setFont("Helvetica", 7)
    for i, (key, val) in enumerate(fields):
        ry = start_y - i * row_h
        # Key
        c.setFillColor(colors.Color(0.3, 0.3, 0.3))
        c.drawString(ox + 5 * mm, ry, f"{key}:")
        # Value
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(ox + 28 * mm, ry, str(val)[:40])
        c.setFont("Helvetica", 7)
        # Separator line
        c.setStrokeColor(colors.Color(0.85, 0.85, 0.85))
        c.setLineWidth(0.3)
        c.line(ox + 4 * mm, ry - 1.5 * mm, ox + label_w - 4 * mm, ry - 1.5 * mm)

    # CE mark placeholder
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.Color(0.4, 0.4, 0.4))
    c.drawString(ox + label_w - 18 * mm, oy + 4 * mm, "CE")

    c.save()
    buffer.seek(0)
    return buffer.read()
