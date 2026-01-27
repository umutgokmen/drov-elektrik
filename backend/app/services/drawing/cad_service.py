import os
import subprocess
import json
from app.schemas import ConfigurationInput

def generate_cad_svg_content(config: ConfigurationInput) -> bytes:
    """
    Executes the CadQuery script to generate an SVG model and returns its content.
    """
    # Hardcoded path as debugged previously
    script_path = "/Users/wazder/Documents/GitHub/Drov/backend/generate_cad.py"
    
    # Get component size mapping (mock for now, or fetch from DB/Models)
    # Ideally should match what frontend sends or what models.py has.
    # We'll use the BoxModel lookup inside the script or pass dimensions.
    # The current generate_cad.py expects a JSON argument with dimensions.
    
    # We need to fetch box dimensions based on box_id to pass to script.
    # Small circular dependency if we import from app.models, but it's fine.
    from app.models import get_box_model_by_id
    box = get_box_model_by_id(config.box_id)
    if not box:
        raise ValueError(f"Box {config.box_id} not found")

    config_data = json.dumps({
        "width": box.internal_width,
        "length": box.internal_length,
        "depth": box.internal_depth,
        "holes_bottom": config.holes_bottom,
        "holes_top": config.holes_top,
        # Pass other params if needed by script
    })
    
    # Conda environment handling
    conda_python = os.path.expanduser("~/miniconda3/envs/cadquery/bin/python")
    # It might be safer to just use the path we used in pdf_engine
    
    # Clean environment
    my_env = os.environ.copy()
    if 'PYTHONPATH' in my_env:
        del my_env['PYTHONPATH']

    cmd = [conda_python, script_path, config_data]

    # Run script
    process = subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        cwd=os.path.dirname(script_path),
        env=my_env
    )
    
    # The script writes to 'cad_output.svg' in its directory
    svg_path = os.path.join(os.path.dirname(script_path), 'cad_output.svg')
    
    if os.path.exists(svg_path):
        import re
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
            
        # 1. Inject ViewBox if missing (CadQuery export creates fixed width/height but no viewBox)
        w_match = re.search(r'width="([^"]+)"', svg_content)
        h_match = re.search(r'height="([^"]+)"', svg_content)
        
        if w_match and h_match:
            try:
                w_val = w_match.group(1).replace("pt", "").replace("mm", "")
                h_val = h_match.group(1).replace("pt", "").replace("mm", "")
                
                # Replace width/height with 100% for responsive web container
                svg_content = re.sub(r'width="[^"]+"', 'width="100%"', svg_content, count=1)
                svg_content = re.sub(r'height="[^"]+"', 'height="100%"', svg_content, count=1)
                
                # Add viewBox if not present
                if 'viewBox' not in svg_content:
                    viewBox_str = f'viewBox="0 0 {w_val} {h_val}"'
                    svg_content = svg_content.replace('<svg', f'<svg {viewBox_str} preserveAspectRatio="xMidYMid meet"', 1)
            except Exception as e:
                print(f"SVG Processing Warning: {e}")

        return svg_content.encode('utf-8')
    else:
        raise FileNotFoundError("SVG output not found from CadQuery script")
