# simple-zarr-server

[![License](https://img.shields.io/pypi/l/simple-zarr-server.svg?color=green)](https://github.com/manzt/simple-zarr-server/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/simple-zarr-server.svg?color=green)](https://pypi.org/project/simple-zarr-server)
[![Python Version](https://img.shields.io/pypi/pyversions/simple-zarr-server.svg?color=green)](https://python.org)
[![tests](https://github.com/manzt/simple-zarr-server/workflows/tests/badge.svg)](https://github.com/manzt/simple-zarr-server/actions)

A simple server for sharing zarr over HTTP.

----------------------------------

## Installation

You can install `simple-zarr-server` via [pip]:

    pip install simple-zarr-server

## Usage

#### CLI:

```bash
$ simple-zarr-server /dataset.zarr # or /dataset.n5, or /dataset.zip
```

#### Python API:

The python API is more flexible than the CLI, and can serve any `zarr.Array`, 
`zarr.Group` or `np.ndarray`. 

##### Server 

```python
from simple_zarr_server import serve
import numpy as np
arr = np.random.rand(1024, 1024)
serve(arr)
```

#### Client

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
grp = zarr.open(store)
datasets = z_grp.attrs["multiscales"][0]["datasets"]
pyramid = [
    da.from_zarr(store, component=d["path"]) for d in datasets
]
with napari.gui_qt():
    napari.view_image(pyramid)
```


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
