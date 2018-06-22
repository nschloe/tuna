# -*- coding: utf-8 -*-
#
import argparse

from .__about__ import __version__
from .main import read, start_server


def main(argv=None):
    parser = _get_parser()
    args = parser.parse_args(argv)

    read(args.infile)
    start_server()
    return


def _get_parser():
    """Parse input options."""
    parser = argparse.ArgumentParser(description=("Visualize Python profile."))

    parser.add_argument("infile", type=str, help="input profile file")

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s " + ("(version {})".format(__version__)),
    )
    return parser
