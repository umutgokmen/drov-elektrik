import os
import subprocess
import json
from app.schemas import ConfigurationInput

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CAD_SCRIPT = os.path.join(_BACKEND_DIR, "generate_cad.py")


def _run_cad_script(config: ConfigurationInput) -> str:
    """
    Execute the CadQuery script and return its working directory.
    Raises subprocess.CalledProcessError on failure.
    """
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
    })

    conda_python = os.path.expanduser("~/miniconda3/envs/cadquery/bin/python")

    my_env = os.environ.copy()
    if 'PYTHONPATH' in my_env:
        del my_env['PYTHONPATH']

    subprocess.run(
        [conda_python, _CAD_SCRIPT, config_data],
        check=True,
        capture_output=True,
        cwd=os.path.dirname(_CAD_SCRIPT),
        env=my_env,
    )

    return os.path.dirname(_CAD_SCRIPT)


def generate_cad_svg_content(config: ConfigurationInput) -> bytes:
    """
    Execute the CadQuery script to generate an SVG model and return its content.
    """
    script_dir = _run_cad_script(config)
    svg_path = os.path.join(script_dir, "cad_output.svg")

    if not os.path.exists(svg_path):
        raise FileNotFoundError("SVG output not found from CadQuery script")

    import re
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()

    # Inject viewBox and make dimensions responsive
    w_match = re.search(r'width="([^"]+)"', svg_content)
    h_match = re.search(r'height="([^"]+)"', svg_content)

    if w_match and h_match:
        try:
            w_val = w_match.group(1).replace("pt", "").replace("mm", "")
            h_val = h_match.group(1).replace("pt", "").replace("mm", "")

            svg_content = re.sub(r'width="[^"]+"', 'width="100%"', svg_content, count=1)
            svg_content = re.sub(r'height="[^"]+"', 'height="100%"', svg_content, count=1)

            if 'viewBox' not in svg_content:
                viewBox_str = f'viewBox="0 0 {w_val} {h_val}"'
                svg_content = svg_content.replace(
                    '<svg',
                    f'<svg {viewBox_str} preserveAspectRatio="xMidYMid meet"',
                    1,
                )
        except Exception as e:
            print(f"SVG Processing Warning: {e}")

    return svg_content.encode('utf-8')


def generate_step(config: ConfigurationInput) -> bytes:
    """
    Execute the CadQuery script to generate a STEP model and return its content.
    """
    script_dir = _run_cad_script(config)
    step_path = os.path.join(script_dir, "cad_output.step")

    if not os.path.exists(step_path):
        raise FileNotFoundError("STEP output not found from CadQuery script")

    with open(step_path, 'rb') as f:
        return f.read()
