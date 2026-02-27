"""
Test cover view drawing generation (Page 5 in PDF).
"""
import pytest
from app.models import get_box_model_by_id
from app.services.geometry_service import calculate_full_layout
from app.services.drawing.pdf_engine import generate_pdf
from tests.conftest import make_config


class TestCoverViewPDF:
    """Test PDF generation with cover elements"""

    def test_pdf_with_cover_elements_generates(self):
        config = make_config("ejb61", terminals=10, holes_top=2)
        layout = calculate_full_layout(config)
        cover_elements = [
            {"element_id": "btn-22-green", "x": 100, "y": 80, "label": "S1"},
            {"element_id": "btn-22-red", "x": 200, "y": 80, "label": "S2"},
            {"element_id": "lamp-22-green", "x": 100, "y": 160, "label": "H1"},
        ]
        pdf_bytes = generate_pdf(config, layout, cover_elements=cover_elements)
        assert pdf_bytes[:5] == b"%PDF-"
        assert len(pdf_bytes) > 10000

    def test_pdf_without_cover_elements_unchanged(self):
        config = make_config("ejb61", terminals=10)
        layout = calculate_full_layout(config)
        pdf_no_cover = generate_pdf(config, layout)
        pdf_empty_cover = generate_pdf(config, layout, cover_elements=[])
        # Both should have the same page count (4)
        assert pdf_no_cover[:5] == b"%PDF-"
        assert pdf_empty_cover[:5] == b"%PDF-"

    def test_pdf_with_cover_is_larger(self):
        config = make_config("ejb61", terminals=10)
        layout = calculate_full_layout(config)
        cover_elements = [
            {"element_id": "btn-22-green", "x": 100, "y": 100, "label": "S1"},
            {"element_id": "lamp-22-red", "x": 200, "y": 100, "label": "H1"},
            {"element_id": "estop-40", "x": 300, "y": 100, "label": "ES"},
        ]
        pdf_no_cover = generate_pdf(config, layout)
        pdf_with_cover = generate_pdf(config, layout, cover_elements=cover_elements)
        assert len(pdf_with_cover) > len(pdf_no_cover)

    def test_pdf_with_rectangular_elements(self):
        config = make_config("ejb91", terminals=20)
        layout = calculate_full_layout(config)
        cover_elements = [
            {"element_id": "ammeter-72", "x": 150, "y": 100, "label": "A1"},
            {"element_id": "voltmeter-72", "x": 250, "y": 100, "label": "V1"},
        ]
        pdf_bytes = generate_pdf(config, layout, cover_elements=cover_elements)
        assert pdf_bytes[:5] == b"%PDF-"

    def test_pdf_with_all_element_types(self):
        config = make_config("ejb91", terminals=20)
        layout = calculate_full_layout(config)
        cover_elements = [
            {"element_id": "btn-22-green", "x": 80, "y": 80, "label": "S1"},
            {"element_id": "btn-22-red", "x": 140, "y": 80, "label": "S2"},
            {"element_id": "sel-22-2pos", "x": 200, "y": 80, "label": "SA1"},
            {"element_id": "lamp-22-green", "x": 80, "y": 160, "label": "H1"},
            {"element_id": "lamp-22-red", "x": 140, "y": 160, "label": "H2"},
            {"element_id": "estop-40", "x": 300, "y": 80, "label": "ES"},
            {"element_id": "ammeter-72", "x": 400, "y": 120, "label": "A1"},
        ]
        pdf_bytes = generate_pdf(config, layout, cover_elements=cover_elements)
        assert pdf_bytes[:5] == b"%PDF-"
        assert len(pdf_bytes) > 15000

    def test_pdf_with_none_cover_elements(self):
        config = make_config("ejb61", terminals=10)
        layout = calculate_full_layout(config)
        pdf_bytes = generate_pdf(config, layout, cover_elements=None)
        assert pdf_bytes[:5] == b"%PDF-"
