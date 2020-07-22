try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from .server import serve, create_zarr_server
