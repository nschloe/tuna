import argparse
import shutil
import threading
import webbrowser
from pathlib import Path

from .__about__ import __version__
from .main import read, render, start_server


def main(argv=None):
    parser = _get_parser()
    args = parser.parse_args(argv)

    prof_filename = args.infile

    if args.infile == '-':
        import os
        import sys
        import tempfile
        with (
            os.fdopen(sys.stdin.fileno(), 'r') as input_file,
            tempfile.NamedTemporaryFile(mode='w', encoding="utf-8", suffix='.prof', delete=False) as output_file
        ):
            shutil.copyfileobj(input_file, output_file)
            prof_filename = output_file.name

    if args.outdir:
        data = lambda: read(prof_filename)
        outdir = Path(args.outdir)
        if not outdir.is_dir():
            outdir.mkdir(parents=True)
        with open(outdir / "index.html", "wt", encoding="utf-8") as out:
            out.write(render(data, prof_filename))
        this_dir = Path(__file__).resolve().parent
        static_dir = outdir / "static"
        if static_dir.is_dir():
            shutil.rmtree(static_dir)
        shutil.copytree(this_dir / "web" / "static", static_dir)
        if args.browser:
            threading.Thread(
                target=lambda: webbrowser.open_new_tab(outdir / "index.html")
            ).start()
    else:
        start_server(prof_filename, args.browser, args.port)

    if args.infile == '-':
        import os
        os.remove(prof_filename)


def _get_parser():
    """Parse input options."""
    parser = argparse.ArgumentParser(description=("Visualize Python profile."))

    parser.add_argument("infile", type=str, help="input runtime or import profile file (`-` for stdin)")
    parser.add_argument(
        "-o",
        "--outdir",
        default=None,
        type=str,
        help="output directory for static files "
        "(no server is started if outdir is specified)",
    )

    parser.add_argument(
        "--no-browser",
        default=True,
        dest="browser",
        action="store_false",
        help="Don't start a web browser (default: do start)",
    )

    parser.add_argument(
        "--port",
        "-p",
        default=None,
        type=int,
        help="Webserver port (default: first free port from 8000)",
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s " + (f"(version {__version__})"),
    )
    return parser
