from importlib import metadata

try:
    __version__ = metadata.version("tuna")
except Exception:
    __version__ = "unknown"
