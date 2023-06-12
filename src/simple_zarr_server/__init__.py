"""Serve Zarr stores over HTTP."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("simple-zarr-server")
except PackageNotFoundError:
    __version__ = "uninstalled"

from .server import serve, create_zarr_route  # noqa
