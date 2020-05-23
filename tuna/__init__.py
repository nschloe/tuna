from . import cli
from .__about__ import __version__
from .main import read_import_profile


def load_ipython_extension(ipython):
    from . import magics  # noqa: F401


__all__ = [
    "__version__",
    "cli",
    "read_import_profile",
]
