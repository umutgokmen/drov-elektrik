"""
DXF Drawing Engine - AutoCAD-compatible DXF file generation using ezdxf
"""
import io
from datetime import datetime
import ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment

from app.schemas import ConfigurationInput, LayoutResult
from app.models import get_box_model_by_id, COMPONENTS


class DXFDrawingEngine:
    """Generates AutoCAD-compatible DXF drawings"""
    
    def __init__(self):
        self.scale = 1.0  # DXF uses real-world units (mm)
        
    def generate(self, config: ConfigurationInput, layout: LayoutResult) -> bytes:
        """
        Generate a DXF drawing for the given configuration.
        
        Returns:
            DXF file as bytes
        """
        box = get_box_model_by_id(config.box_id)
        if not box:
            raise ValueError(f"Invalid box model: {config.box_id}")
        
        # Create new DXF document
        doc = ezdxf.new('R2018')
        doc.units = units.MM
        
        # Setup layers
        self._setup_layers(doc)
        
        # Get modelspace
        msp = doc.modelspace()
        
        # Draw components
        self._draw_enclosure(msp, box)
        self._draw_mounting_plate(msp, box)
        self._draw_rails(msp, layout, box)
        self._draw_terminals(msp, layout, box)
        self._draw_holes(msp, layout, box)
        self._draw_dimensions(msp, box)
        self._draw_title_block(msp, config, box)
        
        # ezdxf requires a text stream for ASCII DXF output
        text_buffer = io.StringIO()
        doc.write(text_buffer)
        return doc.encode(text_buffer.getvalue())
    
    def _setup_layers(self, doc):
        """Create standard CAD layers"""
        layers = [
            ("ENCLOSURE", ezdxf.colors.WHITE),
            ("RAILS", ezdxf.colors.CYAN),
            ("TERMINALS", ezdxf.colors.GREEN),
            ("HOLES", ezdxf.colors.RED),
            ("DIMENSIONS", ezdxf.colors.YELLOW),
            ("TEXT", ezdxf.colors.WHITE),
            ("TITLE_BLOCK", ezdxf.colors.WHITE),
        ]
        
        for name, color in layers:
            doc.layers.add(name=name, color=color)
    
    def _draw_enclosure(self, msp, box):
        """Draw enclosure outline"""
        # Outer rectangle
        msp.add_lwpolyline(
            [(0, 0), (box.internal_width, 0), 
             (box.internal_width, box.internal_length), 
             (0, box.internal_length), (0, 0)],
            dxfattribs={'layer': 'ENCLOSURE', 'lineweight': 50}
        )
        
        # Inner cavity (offset by 5mm)
        offset = 5
        msp.add_lwpolyline(
            [(offset, offset), 
             (box.internal_width - offset, offset),
             (box.internal_width - offset, box.internal_length - offset),
             (offset, box.internal_length - offset), 
             (offset, offset)],
            dxfattribs={'layer': 'ENCLOSURE', 'lineweight': 25}
        )
    
    def _draw_mounting_plate(self, msp, box):
        """Draw mounting plate outline"""
        mp_w = getattr(box, 'mounting_plate_x', None)
        mp_h = getattr(box, 'mounting_plate_y', None)
        if not mp_w or not mp_h:
            return

        x_off = (box.internal_width - mp_w) / 2
        y_off = (box.internal_length - mp_h) / 2

        msp.add_lwpolyline(
            [(x_off, y_off), (x_off + mp_w, y_off),
             (x_off + mp_w, y_off + mp_h),
             (x_off, y_off + mp_h), (x_off, y_off)],
            dxfattribs={'layer': 'ENCLOSURE', 'lineweight': 18,
                        'linetype': 'DASHED'}
        )

        # Corner screw holes
        screw_r = 2.5
        for dx, dy in [(8, 8), (mp_w - 8, 8), (8, mp_h - 8), (mp_w - 8, mp_h - 8)]:
            msp.add_circle((x_off + dx, y_off + dy), screw_r,
                           dxfattribs={'layer': 'ENCLOSURE'})

    def _draw_rails(self, msp, layout: LayoutResult, box):
        """Draw DIN rails"""
        rail_height = 35  # NS 35 standard height
        
        for rail in layout.rails:
            # Rail as rectangle
            x1 = rail.x
            x2 = rail.x + rail.width
            y1 = rail.y - rail_height / 2
            y2 = rail.y + rail_height / 2
            
            msp.add_lwpolyline(
                [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)],
                dxfattribs={'layer': 'RAILS', 'lineweight': 35}
            )
            
            # Rail label
            msp.add_text(
                f"RAIL {layout.rails.index(rail) + 1}",
                dxfattribs={
                    'layer': 'TEXT',
                    'height': 8,
                    'insert': (x1 + 5, rail.y + rail_height/2 + 3)
                }
            )
    
    def _draw_terminals(self, msp, layout: LayoutResult, box):
        """Draw terminal blocks on rails"""
        terminal_width = COMPONENTS["TERMINAL_2_5"]["width"]
        terminal_height = COMPONENTS["TERMINAL_2_5"]["height"]
        
        for rail in layout.rails:
            for i in range(rail.terminal_count):
                tx = rail.x + 5 + i * terminal_width
                ty = rail.y - terminal_height / 2
                
                msp.add_lwpolyline(
                    [(tx, ty), (tx + terminal_width * 0.9, ty),
                     (tx + terminal_width * 0.9, ty + terminal_height),
                     (tx, ty + terminal_height), (tx, ty)],
                    dxfattribs={'layer': 'TERMINALS', 'lineweight': 13}
                )
    
    def _draw_holes(self, msp, layout: LayoutResult, box):
        """Draw M20 holes"""
        hole_radius = COMPONENTS["HOLE_M20"]["diameter"] / 2
        
        # Top holes
        for hole in layout.holes_top:
            cx = hole.position
            cy = box.internal_length + 15
            msp.add_circle((cx, cy), hole_radius, 
                          dxfattribs={'layer': 'HOLES'})
            # Crosshair
            msp.add_line((cx - 8, cy), (cx + 8, cy), 
                        dxfattribs={'layer': 'HOLES'})
            msp.add_line((cx, cy - 8), (cx, cy + 8), 
                        dxfattribs={'layer': 'HOLES'})
        
        # Bottom holes
        for hole in layout.holes_bottom:
            cx = hole.position
            cy = -15
            msp.add_circle((cx, cy), hole_radius, 
                          dxfattribs={'layer': 'HOLES'})
            msp.add_line((cx - 8, cy), (cx + 8, cy), 
                        dxfattribs={'layer': 'HOLES'})
            msp.add_line((cx, cy - 8), (cx, cy + 8), 
                        dxfattribs={'layer': 'HOLES'})
        
        # Left holes
        for hole in layout.holes_left:
            cx = -15
            cy = hole.position
            msp.add_circle((cx, cy), hole_radius, 
                          dxfattribs={'layer': 'HOLES'})
            msp.add_line((cx - 8, cy), (cx + 8, cy), 
                        dxfattribs={'layer': 'HOLES'})
            msp.add_line((cx, cy - 8), (cx, cy + 8), 
                        dxfattribs={'layer': 'HOLES'})
        
        # Right holes
        for hole in layout.holes_right:
            cx = box.internal_width + 15
            cy = hole.position
            msp.add_circle((cx, cy), hole_radius, 
                          dxfattribs={'layer': 'HOLES'})
            msp.add_line((cx - 8, cy), (cx + 8, cy), 
                        dxfattribs={'layer': 'HOLES'})
            msp.add_line((cx, cy - 8), (cx, cy + 8), 
                        dxfattribs={'layer': 'HOLES'})
    
    def _draw_dimensions(self, msp, box):
        """Draw dimension annotations"""
        # Width dimension (bottom)
        msp.add_linear_dim(
            base=(box.internal_width / 2, -40),
            p1=(0, -30),
            p2=(box.internal_width, -30),
            dimstyle='EZDXF',
            dxfattribs={'layer': 'DIMENSIONS'}
        ).render()
        
        # Length dimension (right)
        msp.add_linear_dim(
            base=(box.internal_width + 40, box.internal_length / 2),
            p1=(box.internal_width + 30, 0),
            p2=(box.internal_width + 30, box.internal_length),
            angle=90,
            dimstyle='EZDXF',
            dxfattribs={'layer': 'DIMENSIONS'}
        ).render()
    
    def _draw_title_block(self, msp, config: ConfigurationInput, box):
        """Draw title block"""
        # Position below main drawing
        x = 0
        y = -80
        
        # Border
        msp.add_lwpolyline(
            [(x, y), (x + 150, y), (x + 150, y + 40), (x, y + 40), (x, y)],
            dxfattribs={'layer': 'TITLE_BLOCK'}
        )
        
        # Title
        msp.add_text(
            "DROV Engineering",
            dxfattribs={
                'layer': 'TITLE_BLOCK',
                'height': 8,
                'insert': (x + 5, y + 30)
            }
        )
        
        msp.add_text(
            f"{box.name} Configuration",
            dxfattribs={
                'layer': 'TITLE_BLOCK',
                'height': 6,
                'insert': (x + 5, y + 20)
            }
        )
        
        msp.add_text(
            f"Drawing No: DRV-{box.id.upper()}-001",
            dxfattribs={
                'layer': 'TITLE_BLOCK', 
                'height': 5,
                'insert': (x + 5, y + 10)
            }
        )
        
        msp.add_text(
            f"Date: {datetime.now().strftime('%d.%m.%Y')} | Scale: 1:1 | Sheet: 1/1",
            dxfattribs={
                'layer': 'TITLE_BLOCK',
                'height': 4,
                'insert': (x + 5, y + 3)
            }
        )


# Singleton instance
dxf_engine = DXFDrawingEngine()


def generate_dxf(config: ConfigurationInput, layout: LayoutResult) -> bytes:
    """Generate DXF drawing"""
    return dxf_engine.generate(config, layout)
