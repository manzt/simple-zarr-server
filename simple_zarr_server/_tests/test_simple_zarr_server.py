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


def test_numpy_read():
    # Create data
    original = np.random.rand(1024, 1024)
    z = zarr.array(original)

    # Initialize app
    app = create_zarr_server(z.store)

    # Open remote array and compare
    remote_store = HTTPStore(TestClient(app))
    arr = zarr.open_array(remote_store)
    np.testing.assert_allclose(arr[:], original)


def test_numpy_write():
    # Create data
    original = np.random.rand(1024, 1024)
    mutable = zarr.array(original)

    # Initialize app
    app = create_zarr_server(mutable.store, writeable=True)

    # Open remote array and compare
    remote_store = HTTPStore(TestClient(app))
    arr = zarr.open_array(remote_store)
    arr[:50, :50] = 2

    np.testing.assert_allclose(arr[:], mutable[:])
