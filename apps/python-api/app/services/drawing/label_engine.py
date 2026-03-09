"""
Panel Label PDF Generation Engine
Generates printable panel labels with order info, date and panel details.
"""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A5, A6, landscape, portrait
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdf_canvas

from app.schemas import LabelInput, LabelSize


_PAGE_SIZES = {
    LabelSize.A4: A4,
    LabelSize.A5: A5,
    LabelSize.A6: A6,
}

_BRAND_COLOR = colors.Color(0.11, 0.22, 0.44)   # dark navy
_ACCENT_COLOR = colors.Color(0.93, 0.64, 0.0)   # amber


def _page_size(label: LabelInput):
    """Return (width, height) for the selected label size in portrait."""
    return portrait(_PAGE_SIZES.get(label.label_size, A5))


def generate_label_pdf(label: LabelInput) -> bytes:
    """
    Generate a panel label PDF from the given LabelInput.

    Returns raw PDF bytes.
    """
    date_str = label.date or datetime.now().strftime("%d.%m.%Y")

    buffer = io.BytesIO()
    page_w, page_h = _page_size(label)
    c = pdf_canvas.Canvas(buffer, pagesize=(page_w, page_h))

    _draw_label(c, page_w, page_h, label, date_str)

    c.save()
    buffer.seek(0)
    return buffer.read()


def _draw_label(c, page_w: float, page_h: float, label: LabelInput, date_str: str):
    """Render a single label page onto the canvas."""
    margin = 8 * mm
    inner_w = page_w - 2 * margin
    inner_h = page_h - 2 * margin

    # Outer border
    c.setStrokeColor(_BRAND_COLOR)
    c.setLineWidth(2)
    c.rect(margin, margin, inner_w, inner_h, fill=0, stroke=1)

    # Header band
    header_h = inner_h * 0.22
    header_y = margin + inner_h - header_h
    c.setFillColor(_BRAND_COLOR)
    c.setStrokeColor(_BRAND_COLOR)
    c.rect(margin, header_y, inner_w, header_h, fill=1, stroke=0)

    # Company name in header
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", _scale_font(page_w, 16))
    c.drawCentredString(page_w / 2, header_y + header_h * 0.55, "DROV Engineering")
    c.setFont("Helvetica", _scale_font(page_w, 9))
    c.drawCentredString(page_w / 2, header_y + header_h * 0.2, "Endustriyel Pano Sistemleri")

    # Accent stripe below header
    stripe_h = 3
    c.setFillColor(_ACCENT_COLOR)
    c.rect(margin, header_y - stripe_h, inner_w, stripe_h, fill=1, stroke=0)

    # Content area
    content_y_top = header_y - stripe_h - 5 * mm
    _draw_fields(c, margin, content_y_top, inner_w, page_w, label, date_str)

    # Footer band
    footer_h = inner_h * 0.10
    footer_y = margin
    c.setFillColor(colors.Color(0.94, 0.94, 0.94))
    c.rect(margin, footer_y, inner_w, footer_h, fill=1, stroke=0)
    c.setFillColor(colors.Color(0.5, 0.5, 0.5))
    c.setFont("Helvetica", _scale_font(page_w, 7))
    c.drawCentredString(
        page_w / 2,
        footer_y + footer_h * 0.4,
        "Bu etiketi panoya görünür bir yere yapıştırın. / Affix this label in a visible location on the panel.",
    )


def _draw_fields(c, margin, top_y, inner_w, page_w, label: LabelInput, date_str: str):
    """Draw the information fields in the label body."""
    row_h = 10 * mm
    label_col_w = inner_w * 0.38
    value_col_w = inner_w - label_col_w

    fields = [
        ("Pano Adı / Panel Name", label.panel_name),
        ("Sipariş No / Order No", label.order_no),
        ("Proje / Project", label.project_name),
        ("Müşteri / Customer", label.customer),
        ("Tarih / Date", date_str),
    ]
    if label.notes:
        fields.append(("Notlar / Notes", label.notes))

    x_label = margin + 3 * mm
    x_value = margin + label_col_w + 2 * mm
    y = top_y

    for field_name, field_value in fields:
        if not field_value:
            continue
        y -= row_h

        # Row background for alternating rows
        row_idx = fields.index((field_name, field_value))
        if row_idx % 2 == 0:
            c.setFillColor(colors.Color(0.97, 0.97, 0.97))
            c.setStrokeColor(colors.Color(0.85, 0.85, 0.85))
            c.rect(margin, y, inner_w, row_h, fill=1, stroke=1)
        else:
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.Color(0.85, 0.85, 0.85))
            c.rect(margin, y, inner_w, row_h, fill=1, stroke=1)

        # Vertical divider
        c.setStrokeColor(colors.Color(0.75, 0.75, 0.75))
        c.setLineWidth(0.5)
        c.line(margin + label_col_w, y, margin + label_col_w, y + row_h)

        # Field label
        c.setFillColor(colors.Color(0.3, 0.3, 0.3))
        c.setFont("Helvetica", _scale_font(page_w, 7))
        c.drawString(x_label, y + row_h * 0.3, field_name)

        # Field value
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", _scale_font(page_w, 9))
        c.drawString(x_value, y + row_h * 0.3, str(field_value))


def _scale_font(page_w: float, base_size: int) -> float:
    """Scale font size proportionally to the page width relative to A5."""
    a5_w, _ = A5
    return round(base_size * (page_w / a5_w), 1)
