# simple-zarr-server

[![License](https://img.shields.io/pypi/l/simple-zarr-server.svg)](https://github.com/manzt/simple-zarr-server/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/simple-zarr-server.svg?color=green)](https://pypi.org/project/simple-zarr-server)
[![Python Version](https://img.shields.io/pypi/pyversions/simple-zarr-server.svg?color=green)](https://python.org)
[![tests](https://github.com/manzt/simple-zarr-server/workflows/tests/badge.svg)](https://github.com/manzt/simple-zarr-server/actions)

A minimal server for sharing zarr over HTTP.

----------------------------------

## Installation

You can install `simple-zarr-server` via [pip]:

    pip install simple-zarr-server

## Usage

#### CLI:

```bash
$ simple-zarr-server --help

# Usage: simple-zarr-server [OPTIONS] PATH
#
# Options:
#  --cors TEXT                     Origin to allow CORS. Use wildcard '*' to allow all.
#  -w, --allow-write
#  --host TEXT                     Bind socket to this host.  [default: 127.0.0.1]
#
#  --port INTEGER                  Bind socket to this port.  [default: 8000]
#  --reload                        Enable auto-reload.
#  --loop [auto|asyncio|uvloop]    Event loop implementation.  [default: auto]
#  --http [auto|h11|httptools]     HTTP protocol implementation.  [default: auto]
#
#  --ws [auto|none|websockets|wsproto]
#                                  WebSocket protocol implementation. [default: auto]
#
#  --use-colors / --no-use-colors  Enable/Disable colorized logging.
#  --proxy-headers / --no-proxy-headers
#                                  Enable/Disable X-Forwarded-Proto,
#                                  X-Forwarded-For, X-Forwarded-Port to
#                                  populate remote address info.
#
#  --forwarded-allow-ips TEXT      Comma seperated list of IPs to trust with
#                                  proxy headers. Defaults to the
#                                  $FORWARDED_ALLOW_IPS environment variable if
#                                  available, or '127.0.0.1'.

$ simple-zarr-server /dataset.zarr # or /dataset.n5, or /dataset.zip
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

#### Python API:

The python API is more flexible than the CLI, and can serve any [`zarr.Array`](https://zarr.readthedocs.io/en/stable/api/core.html#zarr.core.Array), 
[`zarr.Group`](https://zarr.readthedocs.io/en/stable/api/hierarchy.html#zarr.hierarchy.Group) or `np.ndarray`. 

##### Server 

```python
from simple_zarr_server import serve
import numpy as np
arr = np.random.rand(1024, 1024)
serve(arr) # creates an in-memory store if not zarr.Array or zarr.Group
```

##### Client

##### `zarr-python`

```python
import zarr
from fsspec import get_mapper
store = get_mapper("http://localhost:8000") 
arr = zarr.open(store, mode='r')
# or 
import dask.array as da
arr = da.from_zarr("http://localhost:8000")
```

##### `zarr.js`

```javascript
import { openArray } from 'zarr';
arr = await openArray({ store: 'http://localhost:8000' });
```

#### Advanced: Serving a remote pyramidal tiff as Zarr

##### Server

```python
from napari_lazy_openslide import OpenSlideStore
from simple_zarr_server import serve
import zarr

store = OpenSlideStore('tumor_004.tif') # custom zarr store
grp = zarr.open(store)
serve(grp)
```

##### Client

```python
import napari
import dask.array as da
import zarr
from fsspec import get_mapper

store = get_mapper("http://localhost:8000")
z_grp = zarr.open(store)
datasets = z_grp.attrs["multiscales"][0]["datasets"]
pyramid = [
    da.from_zarr(store, component=d["path"]) for d in datasets
]
with napari.gui_qt():
    napari.view_image(pyramid)
```

## Note

This package is experimental. It wraps *any* `zarr-python` store as a REST API, enabling remote access over HTTP.
It is similar to [`xpublish`](https://github.com/xarray-contrib/xpublish), but is more minimal and 
does not provide special endpoints that are specific to Xarray datasets. If your data are Xarray dataset, 
_please_ use `xpublish`! `simple-zarr-server` was designed with imaging data in mind, and when combined with a tool
like `ngrok` provides an interesting way to share local images with collaborators. 

Some non-standard zarr stores that might be of interest include:

- [`napari_lazy_openslide.OpenSlideStore`](https://github.com/manzt/napari-lazy-openslide) - read multiscale RGB TIFFs as zarr
- [`HDF5Zarr`](https://github.com/catalystneuro/HDF5Zarr) - read HDF5 with zarr

## Contributing

Contributions are very welcome. Tests can be run with [tox].

## License

Distributed under the terms of the [BSD-3] license,
"simple-zarr-server" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[file an issue]: https://github.com/manzt/simple-zarr-server/issues
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
