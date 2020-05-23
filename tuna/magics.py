import html
import re
import tempfile
import warnings
from pathlib import Path
from typing import Optional

from IPython.core.magic import register_line_cell_magic
from IPython.display import HTML
from IPython.utils.io import capture_output

from .cli import main as tuna_main


def _display_tuna(
    tuna_dir: str, row_height: int = 60, iframe_height: int = 500
) -> HTML:
    tuna_dir = Path(tuna_dir)
    static_dir = tuna_dir / "static"

    # in-line all of the css and js files
    replacements = {
        '<link rel="stylesheet" href="static/bootstrap.min.css">': "bootstrap.min.css",
        '<link href="static/tuna.css" rel="stylesheet">': "tuna.css",
        '<script src="static/d3.min.js"></script>': "d3.min.js",
        '<script src="static/icicle.js"></script>': "icicle.js",
    }

    page = (tuna_dir / "index.html").read_text()
    page = re.sub(r"<nav.*</nav>", "", page, flags=re.DOTALL)
    page = re.sub(r"<footer.*</footer>", "", page, flags=re.DOTALL)
    page = page.replace('row-height="100"', f'row-height="{row_height}"')

    for rep_string, rep_fname in replacements.items():
        asset = (static_dir / rep_fname).read_text()
        if rep_fname.endswith(".js"):
            asset = f"<script>{asset}</script>"
        elif rep_fname.endswith(".css"):
            asset = f"<style>{asset}</style>"
        page = page.replace(rep_string, asset)
    # Use `HTML` with an iframe inside rather than just `IFrame` so that we don't have
    # to write out an html file and ensure it's not deleted before the results are
    # displayed
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        return HTML(
            f"""
            <iframe
              srcdoc="{html.escape(page)}"
              style="border: 0"
              width="100%"
              height={iframe_height}>
            </iframe>
            """
        )


@register_line_cell_magic
def tuna(line: str, cell: Optional[str] = None) -> HTML:
    ip = get_ipython()  # noqa: F821
    with tempfile.TemporaryDirectory() as tmp_dir:
        prun_fname = f"{tmp_dir}/prun"
        prun_line = f"-q -D {prun_fname}"
        with capture_output():
            ip.run_cell_magic("prun", prun_line, cell if cell is not None else line)
        args = [prun_fname, "-o", tmp_dir, "--no-browser"]
        tuna_main(args)
        return _display_tuna(tmp_dir)
