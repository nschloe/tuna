# -*- coding: utf-8 -*-
#
import argparse

from .__about__ import __version__
from .main import start_server


def main(argv=None):
    parser = _get_parser()
    args = parser.parse_args(argv)

    start_server(args.infile, args.browser)
    return


def _get_parser():
    """Parse input options."""
    parser = argparse.ArgumentParser(description=("Visualize Python profile."))

    parser.add_argument("infile", type=str, help="input runtime or import profile file")

    parser.add_argument(
        "--no-browser",
        default=True,
        dest="browser",
        action="store_false",
        help="Don't start a web browser (default: do start)",
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s " + ("(version {})".format(__version__)),
    )
    return parser
