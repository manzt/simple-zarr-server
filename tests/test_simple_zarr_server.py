import numpy as np
import pytest
import zarr
from starlette.applications import Starlette
from starlette.testclient import TestClient
from zarr.storage import BaseStore

from simple_zarr_server.server import create_zarr_route


class HTTPStore(BaseStore):
    def __init__(self, client: TestClient):
        self.client = client

    def __getitem__(self, path: str):
        r = self.client.get(f"/{path}")
        if r.is_error:
            raise KeyError(path)
        return r.content

    def __contains__(self, path: str):
        r = self.client.head(f"/{path}")
        return r.is_success

    def __setitem__(self, path: str, cdata: bytes):
        r = self.client.put(f"/{path}", content=cdata)
        if r.is_error:
            raise ValueError

    def __delitem__(self, path: str):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError


def test_numpy_read_only():
    # Create data
    original = np.random.rand(1024, 1024)
    z = zarr.array(original, read_only=True)

    # Initialize app
    route = create_zarr_route(z)
    app = Starlette(routes=[route])

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
    route = create_zarr_route(mutable)
    app = Starlette(routes=[route])

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
    route = create_zarr_route(grp.get("nested"))
    app = Starlette(routes=[route])

    # Ensure indexing works
    remote_store = HTTPStore(TestClient(app))
    arr = zarr.open_array(remote_store)
    np.testing.assert_allclose(arr[:], original)
