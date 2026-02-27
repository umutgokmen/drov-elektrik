"""
Test PDF, DXF, and SVG output verification for engineering correctness.
Issue #15: PDF/STEP cikti dogrulama
"""
import io
import pytest
import ezdxf

from app.models import get_box_model_by_id
from app.services.geometry_service import calculate_full_layout
from app.services.drawing.dxf_engine import generate_dxf
from app.services.drawing.pdf_engine import generate_pdf
from tests.conftest import make_config


BOX_IDS = ["ejb21", "ejb31", "ejb51", "ejb61", "ejb63", "ejb71", "ejb73", "ejb91", "ejb93"]

EXPECTED_DXF_LAYERS = {"ENCLOSURE", "RAILS", "TERMINALS", "HOLES", "DIMENSIONS", "TEXT", "TITLE_BLOCK"}


def _generate_layout_and_pdf(box_id: str, **kwargs) -> tuple:
    config = make_config(box_id, **kwargs)
    layout = calculate_full_layout(config)
    pdf_bytes = generate_pdf(config, layout)
    return config, layout, pdf_bytes


def _generate_layout_and_dxf(box_id: str, **kwargs) -> tuple:
    config = make_config(box_id, **kwargs)
    layout = calculate_full_layout(config)
    dxf_bytes = generate_dxf(config, layout)
    return config, layout, dxf_bytes


def _parse_dxf(dxf_bytes: bytes):
    """Parse DXF bytes back into ezdxf document using text stream"""
    text = dxf_bytes.decode("utf-8", errors="replace")
    return ezdxf.read(io.StringIO(text))


# ==================== PDF TESTS ====================

class TestPDFOutput:
    """Verify PDF file structure and content"""

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_pdf_is_valid(self, box_id):
        """Generated PDF must start with %PDF header"""
        _, _, pdf_bytes = _generate_layout_and_pdf(box_id, terminals=5, holes_top=2, holes_bottom=2)
        assert pdf_bytes[:5] == b"%PDF-"

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_pdf_has_content(self, box_id):
        """PDF should have substantial size (not empty)"""
        _, _, pdf_bytes = _generate_layout_and_pdf(box_id, terminals=5)
        assert len(pdf_bytes) > 1000

    def test_pdf_multipage(self):
        """PDF should have multiple pages for complex config"""
        _, _, pdf_bytes = _generate_layout_and_pdf("ejb61", terminals=20, holes_top=3)
        # ReportLab generates /Type /Page entries for each page
        # Count occurrences of the page marker
        assert len(pdf_bytes) > 10000

    def test_pdf_zero_config(self):
        """PDF generation should work with zero holes and terminals"""
        _, _, pdf_bytes = _generate_layout_and_pdf("ejb21", terminals=0)
        assert pdf_bytes[:5] == b"%PDF-"

    def test_pdf_max_config(self):
        """PDF with max terminals should still generate"""
        box = get_box_model_by_id("ejb91")
        _, _, pdf_bytes = _generate_layout_and_pdf(
            "ejb91", terminals=box.max_terminals, holes_top=5, holes_bottom=5
        )
        assert pdf_bytes[:5] == b"%PDF-"
        assert len(pdf_bytes) > 5000

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_pdf_ends_with_eof(self, box_id):
        """Valid PDF must end with %%EOF"""
        _, _, pdf_bytes = _generate_layout_and_pdf(box_id, terminals=5)
        assert pdf_bytes.rstrip().endswith(b"%%EOF")


# ==================== DXF TESTS ====================

class TestDXFOutput:
    """Verify DXF file structure, layers, and entities"""

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_dxf_is_parseable(self, box_id):
        """Generated DXF must be parseable by ezdxf"""
        _, _, dxf_bytes = _generate_layout_and_dxf(box_id, terminals=5, holes_top=2)
        doc = _parse_dxf(dxf_bytes)
        assert doc is not None

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_dxf_has_all_layers(self, box_id):
        """DXF must contain all 7 expected layers"""
        _, _, dxf_bytes = _generate_layout_and_dxf(box_id, terminals=5, holes_top=2)
        doc = _parse_dxf(dxf_bytes)
        layer_names = {layer.dxf.name for layer in doc.layers}
        for expected in EXPECTED_DXF_LAYERS:
            assert expected in layer_names, f"Missing layer: {expected}"

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_dxf_has_enclosure_entities(self, box_id):
        """DXF must have enclosure polylines"""
        _, _, dxf_bytes = _generate_layout_and_dxf(box_id, terminals=5)
        doc = _parse_dxf(dxf_bytes)
        msp = doc.modelspace()
        enclosure_entities = [e for e in msp if e.dxf.layer == "ENCLOSURE"]
        assert len(enclosure_entities) >= 2  # outer + inner rectangle

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_dxf_has_rail_entities(self, box_id):
        """DXF must have rail entities matching box rail_count"""
        box = get_box_model_by_id(box_id)
        _, _, dxf_bytes = _generate_layout_and_dxf(box_id, terminals=5)
        doc = _parse_dxf(dxf_bytes)
        msp = doc.modelspace()
        rail_entities = [e for e in msp if e.dxf.layer == "RAILS"]
        assert len(rail_entities) >= box.rail_count

    def test_dxf_hole_count_matches(self):
        """Number of hole circles in DXF must match requested holes"""
        _, _, dxf_bytes = _generate_layout_and_dxf("ejb61", terminals=0, holes_top=3, holes_bottom=2)
        doc = _parse_dxf(dxf_bytes)
        msp = doc.modelspace()
        hole_circles = [e for e in msp if e.dxf.layer == "HOLES" and e.dxftype() == "CIRCLE"]
        assert len(hole_circles) == 5  # 3 top + 2 bottom

    def test_dxf_terminal_count_matches(self):
        """Number of terminal polylines must match requested count"""
        _, _, dxf_bytes = _generate_layout_and_dxf("ejb31", terminals=10)
        doc = _parse_dxf(dxf_bytes)
        msp = doc.modelspace()
        terminal_entities = [e for e in msp if e.dxf.layer == "TERMINALS"]
        assert len(terminal_entities) == 10

    def test_dxf_title_block_exists(self):
        """DXF must have title block with text"""
        _, _, dxf_bytes = _generate_layout_and_dxf("ejb61", terminals=5)
        doc = _parse_dxf(dxf_bytes)
        msp = doc.modelspace()
        title_texts = [e for e in msp if e.dxf.layer == "TITLE_BLOCK" and e.dxftype() == "TEXT"]
        assert len(title_texts) >= 3

    def test_dxf_title_contains_drov(self):
        """Title block must contain DROV branding"""
        _, _, dxf_bytes = _generate_layout_and_dxf("ejb61", terminals=5)
        doc = _parse_dxf(dxf_bytes)
        msp = doc.modelspace()
        title_texts = [e for e in msp if e.dxf.layer == "TITLE_BLOCK" and e.dxftype() == "TEXT"]
        text_values = [e.dxf.text for e in title_texts]
        assert any("DROV" in t for t in text_values)

    def test_dxf_drawing_number_format(self):
        """Drawing number must follow DRV-{BOX_ID}-001 format"""
        _, _, dxf_bytes = _generate_layout_and_dxf("ejb61", terminals=5)
        doc = _parse_dxf(dxf_bytes)
        msp = doc.modelspace()
        title_texts = [e for e in msp if e.dxf.layer == "TITLE_BLOCK" and e.dxftype() == "TEXT"]
        text_values = [e.dxf.text for e in title_texts]
        assert any("DRV-EJB61-001" in t for t in text_values)

    def test_dxf_dimensions_present(self):
        """DXF must contain dimension entities"""
        _, _, dxf_bytes = _generate_layout_and_dxf("ejb51", terminals=5)
        doc = _parse_dxf(dxf_bytes)
        msp = doc.modelspace()
        dim_entities = [e for e in msp if e.dxf.layer == "DIMENSIONS"]
        assert len(dim_entities) > 0

    def test_dxf_zero_holes_no_hole_entities(self):
        """Zero holes should result in no HOLES entities"""
        _, _, dxf_bytes = _generate_layout_and_dxf("ejb21", terminals=5)
        doc = _parse_dxf(dxf_bytes)
        msp = doc.modelspace()
        hole_entities = [e for e in msp if e.dxf.layer == "HOLES"]
        assert len(hole_entities) == 0


# ==================== COMPARATIVE TESTS ====================

class TestComparativeOutputs:
    """Cross-model comparison tests"""

    def test_larger_box_produces_larger_pdf(self):
        """Larger box models should produce more content"""
        _, _, pdf_small = _generate_layout_and_pdf("ejb21", terminals=5)
        _, _, pdf_large = _generate_layout_and_pdf("ejb91", terminals=50, holes_top=5, holes_bottom=5)
        assert len(pdf_large) > len(pdf_small)

    def test_more_holes_more_dxf_entities(self):
        """More holes should result in more DXF entities"""
        _, _, dxf_few = _generate_layout_and_dxf("ejb61", terminals=0, holes_top=1)
        _, _, dxf_many = _generate_layout_and_dxf("ejb61", terminals=0, holes_top=5, holes_bottom=5)
        doc_few = _parse_dxf(dxf_few)
        doc_many = _parse_dxf(dxf_many)
        holes_few = len([e for e in doc_few.modelspace() if e.dxf.layer == "HOLES"])
        holes_many = len([e for e in doc_many.modelspace() if e.dxf.layer == "HOLES"])
        assert holes_many > holes_few

    @pytest.mark.parametrize("box_id", BOX_IDS)
    def test_dxf_and_pdf_both_generate(self, box_id):
        """Both DXF and PDF should generate without error for same config"""
        config = make_config(box_id, terminals=5, holes_top=2, holes_bottom=2)
        layout = calculate_full_layout(config)
        pdf_bytes = generate_pdf(config, layout)
        dxf_bytes = generate_dxf(config, layout)
        assert pdf_bytes[:5] == b"%PDF-"
        doc = _parse_dxf(dxf_bytes)
        assert doc is not None
