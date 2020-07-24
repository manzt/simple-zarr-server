import pytest
import numpy as np
import zarr
from simple_zarr_server.server import create_zarr_server
from starlette.testclient import TestClient


class HTTPStore:
    def __init__(self, client):
        self.client = client

    def __getitem__(self, path):
        r = self.client.get(f"/{path}")
        if r.ok:
            return r.content
        else:
            raise KeyError

    def __contains__(self, path):
        r = self.client.head(f"/{path}")
        if r.ok:
            return True

    def __setitem__(self, path, cdata):
        r = self.client.put(f"/{path}", cdata)
        if not r.ok:
            raise ValueError


def test_numpy_read_only():
    # Create data
    original = np.random.rand(1024, 1024)
    z = zarr.array(original, read_only=True)

    # Initialize app
    app = create_zarr_server(z)

    # Open remote array and compare
    remote_store = HTTPStore(TestClient(app))
    arr = zarr.open_array(remote_store)
    np.testing.assert_allclose(arr[:], original)

    # Make sure can't write
    with pytest.raises(ValueError):
        arr[:50, :50] = 10


def test_numpy_writeable():
    # Create data
    original = np.random.rand(1024, 1024)
    mutable = zarr.array(original)

    # Initialize app
    app = create_zarr_server(mutable)

    # Open remote array and compare
    remote_store = HTTPStore(TestClient(app))
    arr = zarr.open_array(remote_store)
    arr[:50, :50] = 2

    np.testing.assert_allclose(arr[:], mutable[:])


def test_nested_array():
    # Create zarr hierarchy
    original = np.random.rand(1024, 1024)
    grp = zarr.open()
    grp.create_dataset("nested", data=original)

    # Intitilize app with nested nested array
    app = create_zarr_server(grp.get("nested"))

    # Ensure indexing works
    remote_store = HTTPStore(TestClient(app))
    arr = zarr.open_array(remote_store)
    np.testing.assert_allclose(arr[:], original)
