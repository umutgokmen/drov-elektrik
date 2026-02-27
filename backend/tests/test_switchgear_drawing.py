"""
Test switchgear components in PDF/DXF drawing outputs (Issue #21, #22).
"""
import io
import pytest
import ezdxf
from app.models import get_box_model_by_id
from app.schemas import SwitchgearPosition
from app.services.geometry_service import calculate_full_layout
from app.services.drawing.pdf_engine import generate_pdf
from app.services.drawing.dxf_engine import generate_dxf
from tests.conftest import make_config


def _make_sw_positions() -> list[SwitchgearPosition]:
    """Create sample switchgear positions for testing."""
    return [
        SwitchgearPosition(
            component_id="mcb-1p", rail_index=0,
            x=25, y=50, width=17.5, height=45, label="Q1",
        ),
        SwitchgearPosition(
            component_id="mcb-3p", rail_index=0,
            x=45, y=50, width=52.5, height=45, label="Q2",
        ),
        SwitchgearPosition(
            component_id="relay-2co", rail_index=1,
            x=25, y=120, width=17.5, height=45, label="K1",
        ),
    ]


class TestSwitchgearInPDF:
    """Test PDF generation with switchgear components"""

    def test_pdf_with_switchgear_generates(self):
        config = make_config("ejb61", terminals=10)
        layout = calculate_full_layout(config)
        sw = _make_sw_positions()
        pdf = generate_pdf(config, layout, switchgear_positions=sw)
        assert pdf[:5] == b"%PDF-"
        assert len(pdf) > 10000

    def test_pdf_with_switchgear_is_larger(self):
        config = make_config("ejb61", terminals=10)
        layout = calculate_full_layout(config)
        pdf_no_sw = generate_pdf(config, layout)
        pdf_with_sw = generate_pdf(config, layout, switchgear_positions=_make_sw_positions())
        assert len(pdf_with_sw) > len(pdf_no_sw)

    def test_pdf_with_switchgear_and_cover(self):
        config = make_config("ejb61", terminals=10)
        layout = calculate_full_layout(config)
        sw = _make_sw_positions()
        cover = [
            {"element_id": "btn-22-green", "x": 100, "y": 80, "label": "S1"},
        ]
        pdf = generate_pdf(config, layout, cover_elements=cover, switchgear_positions=sw)
        assert pdf[:5] == b"%PDF-"
        assert len(pdf) > 15000

    def test_pdf_none_switchgear_unchanged(self):
        config = make_config("ejb61", terminals=10)
        layout = calculate_full_layout(config)
        pdf1 = generate_pdf(config, layout)
        pdf2 = generate_pdf(config, layout, switchgear_positions=None)
        assert abs(len(pdf1) - len(pdf2)) < 100  # roughly same size

    @pytest.mark.parametrize("box_id", ["ejb21", "ejb61", "ejb91"])
    def test_pdf_with_switchgear_all_boxes(self, box_id):
        config = make_config(box_id, terminals=5)
        layout = calculate_full_layout(config)
        sw = [SwitchgearPosition(
            component_id="mcb-1p", rail_index=0,
            x=25, y=50, width=17.5, height=45, label="Q1",
        )]
        pdf = generate_pdf(config, layout, switchgear_positions=sw)
        assert pdf[:5] == b"%PDF-"


class TestSwitchgearInDXF:
    """Test DXF generation with switchgear components"""

    def _parse_dxf(self, dxf_bytes: bytes):
        text = dxf_bytes.decode("utf-8", errors="replace")
        return ezdxf.read(io.StringIO(text))

    def test_dxf_with_switchgear_generates(self):
        config = make_config("ejb61", terminals=10)
        layout = calculate_full_layout(config)
        sw = _make_sw_positions()
        dxf = generate_dxf(config, layout, switchgear_positions=sw)
        doc = self._parse_dxf(dxf)
        msp = doc.modelspace()
        # Should have more entities with switchgear
        assert len(list(msp)) > 20

    def test_dxf_without_switchgear(self):
        config = make_config("ejb61", terminals=10)
        layout = calculate_full_layout(config)
        dxf_no_sw = generate_dxf(config, layout)
        dxf_with_sw = generate_dxf(config, layout, switchgear_positions=_make_sw_positions())
        assert len(dxf_with_sw) > len(dxf_no_sw)

    def test_dxf_switchgear_has_text_labels(self):
        config = make_config("ejb61", terminals=10)
        layout = calculate_full_layout(config)
        sw = _make_sw_positions()
        dxf = generate_dxf(config, layout, switchgear_positions=sw)
        doc = self._parse_dxf(dxf)
        msp = doc.modelspace()
        texts = [e.dxf.text for e in msp.query("TEXT") if hasattr(e.dxf, 'text')]
        labels_found = [t for t in texts if t in ("Q1", "Q2", "K1")]
        assert len(labels_found) >= 2


class TestLabelPDF:
    """Test label PDF generation"""

    def test_label_generates(self):
        from app.schemas import LabelInput
        from app.services.drawing.label_engine import generate_label_pdf

        box = get_box_model_by_id("ejb61")
        label = LabelInput(box_id="ejb61", customer_name="Test Corp")
        pdf = generate_label_pdf(label, box)
        assert pdf[:5] == b"%PDF-"
        assert len(pdf) > 1000

    def test_label_with_all_fields(self):
        from app.schemas import LabelInput
        from app.services.drawing.label_engine import generate_label_pdf

        box = get_box_model_by_id("ejb91")
        label = LabelInput(
            box_id="ejb91",
            drawing_number="DRV-2026-0042",
            order_number="ORD-001",
            customer_name="Drov Engineering",
            project_name="Test Project",
            panel_name="Main Panel",
            voltage="400V AC",
            ip_rating="IP67",
            date="27.02.2026",
        )
        pdf = generate_label_pdf(label, box)
        assert pdf[:5] == b"%PDF-"
